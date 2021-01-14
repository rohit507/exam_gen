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

def yield_none_forever(self, seq):
    while True:
        yield None

@attr.s
class NestedIterator(TraversalBase):
    """
    Pass data through the line of parents, then through consecutive children.
    Useful for assigning things like section and sub-section numbers.

      - assign: given data for this specific member do something.
        `def assign_func(self,my_data): ... self.do_something(my_data)`

      - step: Given the parent's data, return an iterator for sequential
        child data. Generally should use `yeild` and copy parent data where
        needed. Should have sig:

        ```
        def step_func(self, my_data):
            ...
            while something:
                ...
                yield next_child_data
        ```

      - members: The children of this object used for this traversal, with sig
        `def members_func(self): ... return child_list`.

    Note that `step` is structured so that data isn't chained between children,
    the only chaining is the via the iterator which has no access to the
    children. This same pattern could be achieved by passing the iterator
    along though a TreeTraverse, but that would be rather painful.
    """

    _assign = attr.ib(
        converter = TypedDispatch,
    )

    @traversal_dispatcher(dispatcher_name = '_assign')
    def _assign_indirect(): pass

    @traversal_updater(dispatcher_name = '_assign')
    def assign(self, func): return func

    _step = attr.ib(
        default = yield_none_forever,
        converter = TypedDispatch,
        kw_only = True,
    )

    @traversal_dispatcher(dispatcher_name = '_step')
    def _step_indirect(): pass

    @traversal_updater(dispatcher_name = '_step')
    def step(self, func): return func

    @classmethod
    @traversal_decorator(key_param = 'assign')
    def decorate(cls, assign, **kwargs):
        return NestedIterator(assign, **kwargs)


    def __get__(self, obj, objtype = None):
        def func(seed) : return self._traverse(obj, seed)
        return func

    def _traverse(self, obj, seed):
        self._assign_indirect(obj, seed)
        seeds = iter(self._step_indirect(obj, seed))
        for member in self._members_indirect(obj):
            self._traverse(member, next(seeds))
