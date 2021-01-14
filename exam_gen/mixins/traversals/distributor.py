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
class Distributor(TraversalBase):
    """
    Distribute information through a tree, going top down.

      - assign: given data for this specific member do something.
        `def assign_func(self,my_data): ... self.do_something(my_data)`

      - allocate: split incoming data from parent into data for self, and
        data for children. Should have sig
        `def alloc_func(self, parent_data): ... return (my_data, child_data)`

      - members: The children of this object used for this traversal, with sig
        `def members_func(self): ... return child_list`.
    """

    _assign = attr.ib(
        converter = TypedDispatch,
    )

    @traversal_dispatcher(dispatcher_name = '_assign')
    def _assign_indirect(self, obj, data): pass

    @traversal_updater(dispatcher_name = '_assign')
    def assign(self, func): return func

    _allocate = attr.ib(
        default = lambda self, items: (items, items),
        converter = TypedDispatch,
        kw_only = True,
    )

    @traversal_dispatcher(dispatcher_name = '_allocate')
    def _allocate_indirect(): pass

    @traversal_updater(dispatcher_name = '_allocate')
    def allocate(self, func): return func

    @classmethod
    @traversal_decorator(key_param = 'assign')
    def decorate(cls,assign,**kwargs):
        return Distributor(assign,**kwargs)

    def __get__(self, obj, objtype = None):
        def func(items) : return self._distrib(obj, items)
        return func

    def _distrib(self, obj, data):
        (self_data, sub_data) = self._allocate_indirect(obj, data)
        self._assign_indirect(obj, self_data)
        for member in self._members_indirect(obj):
            self._distrib(member, sub_data)
