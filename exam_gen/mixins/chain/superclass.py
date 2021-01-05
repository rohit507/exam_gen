import attr
from textwrap import indent, dedent
from pprint import pprint, pformat
from copy import copy, deepcopy
from exam_gen.mixins.chain.util import *
from exam_gen.mixins.prepare_attrs import PrepareAttrs
import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

class Chainable(metaclass=PrepareAttrs):

    @classmethod
    def __prepare_attrs__(cls, name, bases, env):
        """
        Add the decorators to the class's environment
        """
        if hasattr(super(),"__prepare_attrs__"):
            env = super().__prepare_attrs__(name,bases,env)

        # We're being rather simple here and just adding the decorators
        # to the
        env['gather'] = Gatherer.decorator
        env['distribute'] = Distributor.decorator
        env['nested_iter'] = NestedIterator.decorator
        env['depth_iter'] = PropagateDown.decorator
        env['tree_iter'] = TreeTraverse.decorator

        return env

class StrippedProperty():

    def __init__(self, doc = None, members = None):
        # Get rid of all the stuff from `Property` so that we can exploit
        # how docstring tools use it but nothing
        # for attr in ['getter', 'setter', 'deleter']:
        #    if hasattr(self, attr): delattr(self, attr)

        self.fmembers = members
        self._name =  "UNKNOWN_NAME"
        self.__doc__ = doc


    def __set_name__(self, obj, name):
        self._owner = obj
        self._name = name

    def __get__(self, obj, value):
        raise AttributeError(
            "Can't get with attr `{}` of kind {}.".format(
                self._name, type(self).__name__))

    def __set__(self, obj, value):
        raise AttributeError(
            "Can't set with attr `{}` of kind {}.".format(
                self._name, type(self).__name__))

    def __delete__(self, obj):
        raise AttributeError(
            "Can't delete with attr `{}` of kind {}.".format(
                self._name, type(self).__name__))

    def _imembers(self, obj):
        sa = self._sub_attr(obj)
        if sa != None:
            return sa._imembers(obj)
        elif ((self != obj) and hasattr(obj, 'default_members')):
            return getattr(obj, 'default_members')(obj)
        else:
            return self.fmembers(obj)

    def _sub_attr(self, obj):
        sub_attr = getattr(obj, self._name, None)
        if ((sub_attr == None)
            or (obj == self._owner)
            or (sub_attr == self)
            or (not isinstance(sub_attr, type(self)))):
            return None
        else:
            return sub_attr


class Gatherer(StrippedProperty):

    def __init__(
            self,
            gather = None,
            combine = None,
            members = None,
            doc = None
    ):

        super().__init__(
            doc = doc if doc != None else gather.__doc__,
            members = members
        )

        self.fgather  = gather
        self.fcombine = combine

    @staticmethod
    def decorator(gather = None, *, members = None, combine = None, doc = None):
        def stub(func):
            return Gatherer(func, combine, members, doc)

        if gather == None:
            return stub
        else:
            return stub(gather)

    def __get__(self, obj, objtype = None):
        def func() : return self._collect(obj)
        return func


    def combine(self, func):
        pprint("combine")
        return type(self)(
            gather = self.fgather,
            combine = func,
            members = self.fmembers,
            doc = self.__doc__)

    def gather(self, func):
        pprint("gather")
        return type(self)(
            gather = func,
            combine = self.fcombine,
            members = self.fmembers,
            doc = self.__doc__)

    def members(self, func):
        pprint("members")
        return type(self)(
            gather = self.fgather,
            combine = self.fcombine,
            members = func,
            doc = self.__doc__)


    def _igather(self, obj):
        sa = self._sub_attr(obj)
        return (self.fgather if sa == None else sa._igather)(obj)

    def _icombine(self, obj, item, items):
        sa = self._sub_attr(obj)
        return (self.fcombine if sa == None else sa._icombine)(obj, item, items)

    def _collect(self, obj):
        item = [self._igather(obj)]
        items = [self._collect(x) for x in self._imembers(obj)]
        return self._icombine(obj, item, items)


class Distributor(StrippedProperty):

    def __init__(
            self,
            assign = None,
            distribute = None,
            members = None,
            doc = None
    ):

        super().__init__(
            doc = doc if doc != None else assign.__doc__,
            members = members
        )

        self.fassign  = assign
        self.fdistrib = distribute

    @staticmethod
    def decorator(assign = None, *, members = None, distribute = None, doc = None):
        def stub(func):
            return Distributor(func, distribute, members, doc)

        if assign == None:
            return stub
        else:
            return stub(assign)

    def __get__(self, obj, objtype = None):
        def func(items) : return self._distrib(obj, items)
        return func

    def assign(self, func):
        return type(self)(func,
                          self.fdistrib,
                          self.fmembers,
                          self.__doc__)

    def distribute(self, func):
        return type(self)(self.fassign,
                          func,
                          self.fmembers,
                          self.__doc__)

    def members(self, func):
        return type(self)(self.fassign,
                          self.fdistrib,
                          func,
                          self.__doc__)

    def _iassign(self, obj, datum):
        sa = self._sub_attr(obj)
        return (self.fassign if sa == None else sa._iassign)(obj, datum)

    def _idistrib(self, obj, data):
        sa = self._sub_attr(obj)
        return (self.fdistrib if sa == None else sa._idistrib)(obj, data)

    def _distrib(self, obj, data):
        (self_data, sub_data) = self._idistrib(obj, data)
        self._iassign(obj, self_data)
        for member in self._imembers(obj):
            self._distrib(member, sub_data)


class NestedIterator(StrippedProperty):
    """
    process:
      - apply seed to self.
      - create iterator from seed, pull items for each sub_elem, let each
        process.
    """

    def __init__(
            self,
            assign = None,
            recurse = None,
            members = None,
            doc = None,
    ):

        super().__init__(
            doc = doc if doc != None else assign.__doc__,
            members = members,
        )

        self.fassign  = assign
        self.frecurse = recurse

    @staticmethod
    def decorator(assign = None, *, members = None, recurse = None, doc = None):
        def stub(func):
            return NestedIterator(func, recurse, members, doc)

        if assign == None:
            return stub
        else:
            return stub(assign)

    def __get__(self, obj, objtype = None):
        def func(seed) : return self._traverse(obj, seed)
        return func

    def assign(self, func):
        return type(self)(func,
                          self.frecurse,
                          self.fmembers,
                          self.__doc__)

    def recurse(self, func):
        return type(self)(self.fassign,
                          func,
                          self.fmembers,
                          self.__doc__)

    def members(self, func):
        return type(self)(self.frecurse,
                          self.fdistrib,
                          func,
                          self.__doc__)

    def _iassign(self, obj, seed):
        sa = self._sub_attr(obj)
        return (self.fassign if sa == None else sa._iassign)(obj, seed)

    def _irecurse(self, obj, seed):
        sa = self._sub_attr(obj)
        return (self.frecurse if sa == None else sa._irecurse)(obj, seed)

    def _traverse(self, obj, seed):
        self._iassign(obj, seed)
        seeds = iter(self._irecurse(obj, seed))
        for member in self._imembers(obj):
            self._traverse(member, next(seeds))

# Things like pushing metadata or other settings from the top down.
# has `assign`, `members`, and `copy`
class PropagateDown(StrippedProperty):

    def __init__(
            self,
            assign = None,
            copy = None,
            members = None,
            doc=None,
    ):

        super().__init__(
            doc = doc if doc != None else assign.__doc__,
            members = members,
        )

        self.fassign  = assign

        def def_copy(self, dat): return deepcopy(dat)

        self.fcopy = copy if copy != None else def_copy

    @staticmethod
    def decorator(assign = None, *, members = None, copy = None, doc = None):
        def stub(func):
            return PropagateDown(func, copy, members, doc)

        if assign == None:
            return stub
        else:
            return stub(assign)

    def __get__(self, obj, objtype = None):
        def func(data) : return self._push(obj, data)
        return func

    def assign(self, func):
        return type(self)(func,
                          self.fcopy,
                          self.fmembers,
                          self.__doc__)

    def copy(self, func):
        return type(self)(self.fassign,
                          func,
                          self.fmembers,
                          self.__doc__)

    def members(self, func):
        return type(self)(self.fassign,
                          self.copy,
                          func,
                          self.__doc__)

    def _iassign(self, obj, data):
        sa = self._sub_attr(obj)
        return (self.fassign if sa == None else sa._iassign)(obj, data)

    def _icopy(self, obj, data):
        sa = self._sub_attr(obj)
        return (self.fcopy(obj,data) if sa == None else sa._icopy(obj, data))

    def _push(self, obj, data):
        new_data = self._iassign(obj, data)
        for member in self._imembers(obj):
            self._push(member, self._icopy(obj, new_data))

# Fold through members one item after another, gathering data from
# the parents, and pass through each child
# Has `use`, `members`, and `copy`
class TreeTraverse(StrippedProperty):

    def __init__(
            self,
            modify = None,
            copy = None,
            members = None,
            doc = None
    ):

        super().__init__(
            doc = doc if doc != None else modify.__doc__,
            members = members,
        )

        self.fmodify = modify

        def def_copy(self, dat): return deepcopy(dat)

        self.fcopy = copy if copy != None else def_copy

    @staticmethod
    def decorator(modify = None, *, members = None, copy = None, doc = None):
        def stub(func):
            return TreeTraverse(func, copy, members, doc)

        if modify == None:
            return stub
        else:
            return stub(modify)

    def __get__(self, obj, objtype = None):
        def func(data) : return self._traverse(obj, data)
        return func

    def modify(self, func):
        return type(self)(func,
                          self.fcopy,
                          self.fmembers,
                          self.__doc__)

    def copy(self, func):
        return type(self)(self.fmodify,
                          func,
                          self.fmembers,
                          self.__doc__)

    def members(self, func):
        return type(self)(self.fmodify,
                          self.copy,
                          func,
                          self.__doc__)

    def _imodify(self, obj, data):
        sa = self._sub_attr(obj)
        return (self.fmodify if sa == None else sa._imodify)(obj, data)

    def _icopy(self, obj, data):
        sa = self._sub_attr(obj)
        return (self.fcopy if sa == None else sa._icopy)(obj, data)

    def _traverse(self, obj, data):
        new_data = self._imodify(obj, data)
        copy_data = self._icopy(obj, new_data)
        for member in self._imembers(obj):
            copy_data = self._traverse(member, copy_data)
        return new_data
