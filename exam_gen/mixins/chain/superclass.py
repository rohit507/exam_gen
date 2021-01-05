import attr
from textwrap import indent, dedent
from pprint import pprint, pformat
from copy import copy, deepcopy
from exam_gen.mixins.chain.util import *
from exam_gen.mixins.prepare_attrs import PrepareAttrs
import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

class Chainable():

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

class StrippedProperty(type(property())):

    def __init__(self, doc = None, members = None):
        # Get rid of all the stuff from `Property` so that we can exploit
        # how docstring tools use it but nothing
        for attr in ['getter', 'setter', 'deleter']:
            if hasattr(self, attr): delattr(self, attr)

        def stub(self): pass
        self.fget = stub

        for attr in ['fset', 'fdel']:
            setattr(self, attr, None)

        self.fget.__doc__ = doc
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
    def decorator(func, *, members = None, combine = None, doc = None):
        if ((members == None) and (combine == None) and (doc == None)):
            return Gatherer(func)
        else:
            def stub(func):
                return Gatherer(func, members, combine, doc)
            return stub

    def __get__(self, obj, objtype = None):
        def func() : return self._collect(obj)
        return func


    def combine(self, func):
        return type(self)(self,
                          self.fgather,
                          self.fmembers,
                          func,
                          self.__doc__)

    def gather(self, func):
        return type(self)(self,
                          func,
                          self.fmembers,
                          self.fcombine,
                          self.__doc__)

    def members(self, func):
        return type(self)(self,
                          self.fgather,
                          func,
                          self.fcombine,
                          self.__doc__)


    def _igather(self, obj):
        sa = self._sub_attr(obj)
        return (self.fgather if sa == None else sa._igather)(obj)

    def _icombine(self, obj, items):
        sa = self._sub_attr(obj)
        return (self.fcombine if sa == None else sa._icombine)(obj, items)

    def _collect(self, obj):
        items = [self._igather(obj)]
        items += [self._collect(x) for x in self._imembers(obj)]
        return self._icombine(obj, items)


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
    def decorator(func, *, members = None, distribute = None, doc = None):
        if ((members == None) and (distribute == None) and (doc == None)):
            return Distributor(func)
        else:
            def stub(func):
                return Distributor(func, distribute, members, doc)
            return stub

    def __get__(self, obj, objtype = None):
        def func(items) : return self._distrib(obj, items)
        return func

    def assign(self, func):
        return type(self)(self,
                          func,
                          self.fdistrib,
                          self.fmembers,
                          self.__doc__)

    def distribute(self, func):
        return type(self)(self,
                          self.fassign,
                          func,
                          self.fmembers,
                          self.__doc__)

    def members(self, func):
        return type(self)(self,
                          self.fassign,
                          self.fdistrib,
                          func,
                          self.__doc__)

    def _iassign(self, obj, item):
        sa = self._sub_attr(obj)
        return (self.fassign if sa == None else sa._iassign)(obj, item)

    def _idistrib(self, obj, items):
        sa = self._sub_attr(obj)
        return (self.fdistrib if sa == None else sa._idistrib)(obj, items)

    def _distrib(self, obj, items):
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
    ):

        super().__init__(
            doc = doc if doc != None else assign.__doc__,
            members = members,
        )

        self.fassign  = assign
        self.frecurse = recurse

    @staticmethod
    def decorator(func, *, members = None, recurse = None, doc = None):
        if ((members == None) and (recurse == None) and (doc == None)):
            return NestedIterator(func)
        else:
            def stub(func):
                return NestedIterator(func, recurse, members, doc)
            return stub

    def __get__(self, obj, objtype = None):
        def func(seed) : return self._traverse(obj, items)
        return func

    def assign(self, func):
        return type(self)(self,
                          func,
                          self.frecurse,
                          self.fmembers,
                          self.__doc__)

    def recurse(self, func):
        return type(self)(self,
                          self.fassign,
                          func,
                          self.fmembers,
                          self.__doc__)

    def members(self, func):
        return type(self)(self,
                          self.frecurse,
                          self.fdistrib,
                          func,
                          self.__doc__)

    def _iassign(self, obj, seed):
        sa = self._sub_attr(obj)
        return (self.fassign if sa == None else sa._iassign)(obj, seed)

    def _irecurse(self, obj, seed):
        sa = self._sub_attr(obj)
        return (self.irecurse if sa == None else sa._irecurse)(obj, seed)

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
            copy = deepcopy,
            members = None,
    ):

        super().__init__(
            doc = doc if doc != None else assign.__doc__,
            members = members,
        )

        self.fassign  = assign
        self.fcopy = copy

    @staticmethod
    def decorator(func, *, members = None, copy = None, doc = None):
        if ((members == None) and (copy == None) and (doc == None)):
            return PropagateDown(func)
        else:
            def stub(func):
                return PropagateDown(func, copy, members, doc)
            return stub

    def __get__(self, obj, objtype = None):
        def func(seed) : return self._push(obj, data)
        return func

    def assign(self, func):
        return type(self)(self,
                          func,
                          self.fcopy,
                          self.fmembers,
                          self.__doc__)

    def copy(self, func):
        return type(self)(self,
                          self.fassign,
                          func,
                          self.fmembers,
                          self.__doc__)

    def members(self, func):
        return type(self)(self,
                          self.fassign,
                          self.copy,
                          func,
                          self.__doc__)

    def _iassign(self, obj, data):
        sa = self._sub_attr(obj)
        return (self.fassign if sa == None else sa._iassign)(obj, data)

    def _icopy(self, obj, data):
        sa = self._sub_attr(obj)
        return (self.fcopy(data) if sa == None else sa._icopy(obj, data))

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
            copy = deepcopy,
            members = None,
    ):

        super().__init__(
            doc = doc if doc != None else assign.__doc__,
            members = members,
        )

        self.fmodify  = assign
        self.fcopy = copy

    @staticmethod
    def decorator(func, *, members = None, modify = None, doc = None):
        if ((members == None) and (modify == None) and (doc == None)):
            return TreeTraverse(func)
        else:
            def stub(func):
                return TreeTraverse(func, copy, members, doc)
            return stub

    def __get__(self, obj, objtype = None):
        def func(seed) : return self._traverse(obj, data)
        return func

    def modify(self, func):
        return type(self)(self,
                          func,
                          self.fcopy,
                          self.fmembers,
                          self.__doc__)

    def copy(self, func):
        return type(self)(self,
                          self.fassign,
                          func,
                          self.fmembers,
                          self.__doc__)

    def members(self, func):
        return type(self)(self,
                          self.fassign,
                          self.copy,
                          func,
                          self.__doc__)

    def _imodify(self, obj, data):
        sa = self._sub_attr(obj)
        return (self.fmodify if sa == None else sa._imodify)(obj, data)

    def _icopy(self, obj, data):
        sa = self._sub_attr(obj)
        return (self.fcopy(data) if sa == None else sa._icopy(obj, data))

    def _traverse(self, obj, data):
        new_data = self._iassign(obj, data)
        copy_data = self._icopy(obj, new_data)
        for member in self._imembers(obj):
            copy_data = self._traverse(member, copy_data)
        return new_data
