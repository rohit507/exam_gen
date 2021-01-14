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
class SiblingIterator(TraversalBase):
    """
    This traverses a path from the root to each node which passes through
    all the parent's earlier siblings.

      - modify: Do something with the data from your parents, then pass data
        to your children, with sig:
        ```
        def modify_func(self,pred_data):
            ...
            self.do_something(pred_data)
            ...
            return (succ_data, child_data)
        ```

      - members: The children of this object used for this traversal, with sig
        `def members_func(self): ... return child_list`.

    Note: Your modify function will probably want to make a personal copy of
    the data it's passing to its successor and child, but it's the caller's
    responsibility to make sure that references being passed around are safe.

    Also, yes, most of the other traversals could be implemented in terms of
    this. It would be a huge pain and it's easier on everyone to separate them
    out.
    """

    _modify = attr.ib(
        converter = TypedDispatch,
    )

    @traversal_dispatcher(dispatcher_name = '_modify')
    def _modify_indirect(): pass

    @traversal_updater(dispatcher_name = '_modify')
    def modify(self, func): return func

    @classmethod
    @traversal_decorator(key_param = 'modify')
    def decorate(cls, modify, **kwargs):
        return SiblingIterator(modify, **kwargs)

    def __get__(self, obj, objtype = None):
        def func(data) : return self._traverse(obj, data)
        return func

    def _traverse(self, obj, pred_data):
        (succ_data, child_data) = self._modify_indirect(obj, pred_data)
        for member in self._members_indirect(obj):
            child_data = self._traverse(member, child_data)
        return succ_data
