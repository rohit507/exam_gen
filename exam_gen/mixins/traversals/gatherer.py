from copy import copy, deepcopy
from pprint import pformat, pprint
from textwrap import dedent, indent
from collections import Iterable

import inspect

import attr
import attr.validators as valid

from exam_gen.mixins.traversals.typed_dispatch import TypedDispatch
from exam_gen.mixins.traversals.decorators import *
from exam_gen.mixins.traversals.traversal_base import TraversalBase

import exam_gen.util.logging as logging

log = logging.new(__name__, level="WARNING")

@attr.s
class Gatherer(TraversalBase):
    """
    Traverse the set of objects and gather some information.

      - gather: Gets the info for this specific member, should have sig:
        `def gather_func(self): ... return my_data`

      - combine: Combine info from myself ans all children. Should have sig:
        `def combine_func(self, my_data, child_data): ... return combined_data`
        The child_data will be a list where each item is the combined data of
        the specific child.

     - members: The children of this object used for this traversal, with sig:
       `def members_func(self): ... return child_list`
    """

    _gather = attr.ib(
        converter = TypedDispatch,
    )

    @traversal_dispatcher(dispatcher_name = '_gather')
    def _gather_indirect(): pass

    @traversal_updater(dispatcher_name = '_gather')
    def gather(self, func): return func

    _combine = attr.ib(
        default = lambda self, item, items: itertools.chain(item, *items),
        converter = TypedDispatch,
        kw_only = True,
    )

    @traversal_dispatcher(dispatcher_name = '_combine')
    def _combine_indirect(): pass

    @traversal_updater(dispatcher_name = '_combine')
    def combine(self, func): return func

    @classmethod
    @traversal_decorator(key_param = 'gather')
    def decorate(cls, gather, **kwargs):
        return Gatherer(gather, **kwargs)

    def __get__(self, obj, objtype = None):
        def func() : return self._collect(obj)
        return func

    def _collect(self, obj):
        item = [self._gather_indirect(obj)]
        items = [self._collect(x) for x in self._members_indirect(obj)]
        return self._combine_indirect(obj, item, items)
