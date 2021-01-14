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
class DepthIterator(TraversalBase):
    """
    Pass data from top down, where consecutive assign calls form a chain from
    root to the particular child. This could be done with `distribute` but
    it would be overcomplicated.

      - descend: Do something with the data from your parents, then pass data
        to your children, with sig:
        ```
        def assign_func(self,parent_data):
            ...
            self.do_something(parent_data)
            ...
            return child_data
        ```

      - copy: copy a piece of child data so that each child has their own
        version, with sig:
        `def copy_func(self, child_data): ... return child_data_copy`

      - members: The children of this object used for this traversal, with sig
        `def members_func(self): ... return child_list`.

    This is a walk from the root of the tree to each node.
    """

    _descend = attr.ib(
        converter = TypedDispatch,
    )

    @traversal_dispatcher(dispatcher_name = '_descend')
    def _descend_indirect(): pass

    @traversal_updater(dispatcher_name = '_descend')
    def descend(self, func): return func

    _copy = attr.ib(
        default = lambda self, item: deepcopy(item),
        converter = TypedDispatch,
        kw_only = True,
    )

    @traversal_dispatcher(dispatcher_name = '_copy')
    def _copy_indirect(): pass

    @traversal_updater(dispatcher_name = '_copy')
    def copy(self, func): return func

    @classmethod
    @traversal_decorator(key_param = 'descend')
    def decorate(cls, descend, **kwargs):
        return DepthIterator(descend, **kwargs)

    def __get__(self, obj, objtype = None):
        def func(data) : return self._push(obj, data)
        return func

    def _push(self, obj, data):
        new_data = self._descend_indirect(obj, data)
        for member in self._members_indirect(obj):
            self._push(member, self._copy_indirect(obj, new_data))
