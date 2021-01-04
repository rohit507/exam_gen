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
        env['gather'] = gather_decorator
        env['distribute'] = distribute_decorator
        env['nestediter'] = nestediter_decorator

        return env



class StrippedProperty(type(property())):

    def __init__(self, doc = None):
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

    def _sub_attr(self, obj):
        sub_attr = getattr(obj, self._name, None)
        if ((sub_attr == None)
            or (obj == self._owner)
            or (sub_attr == self)
            or (not isinstance(sub_attr, type(self)))):
            return None
        else:
            return sub_attr

def gather_decorator(func, *, members = None, combine = None, doc = None):
    if ((members == None) and (combine == None) and (doc == None)):
        return Gatherer(func)
    else:
        def stub(func):
            return Gatherer(func, members, combine, doc)
        return stub

class Gatherer(StrippedProperty):

    def __init__(
            self,
            gather = None,
            combine = None,
            members = None,
            doc = None
    ):

        super().__init__(doc if doc != None else gather.__doc__)

        self.fgather  = gather
        self.fcombine = combine
        self.fmembers = members

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

    def _imembers(self, obj):
        sa = self._sub_attr(obj)
        return (self.fmembers if sa == None else sa._imembers)(obj)

    def _icombine(self, obj, items):
        sa = self._sub_attr(obj)
        return (self.fcombine if sa == None else sa._icombine)(obj, items)

    def _collect(self, obj):
        items = [self._igather(obj)]
        items += [self._collect(x) for x in self._imembers(obj)]
        return self._icombine(obj, items)

def distribute_decorator(func, *, members = None, distribute = None, doc = None):
    if ((members == None) and (distribute == None) and (doc == None)):
        return Distributor(func)
    else:
        def stub(func):
            return Distributor(func, distribute, members, doc)
        return stub

class Distributor(StrippedProperty):

    def __init__(
            self,
            assign = None,
            distribute = None,
            members = None,
            doc = None
    ):

        super().__init__(doc if doc != None else assign.__doc__)

        self.fassign  = assign
        self.fdistrib = distribute
        self.fmembers = members

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

    def _imembers(self, obj):
        sa = self._sub_attr(obj)
        return (self.fmembers if sa == None else sa._imembers)(obj)

    def _distrib(self, obj, items):
        (self_data, sub_data) = self._idistrib(obj, data)
        self._iassign(obj, self_data)
        for member in self._imembers(obj):
            self._distrib(member, sub_data)

def nestediter_decorator(func, *, members = None, recurse = None, doc = None):
    if ((members == None) and (recurse == None) and (doc == None)):
        return NestedIterator(func)
    else:
        def stub(func):
            return NestedIterator(func, recurse, members, doc)
        return stub

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

        super().__init__(doc if doc != None else assign.__doc__)

        self.fassign  = assign
        self.frecurse = recurse
        self.fmembers = members

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

    def _imembers(self, obj):
        sa = self._sub_attr(obj)
        return (self.fmembers if sa == None else sa._imembers)(obj)

    def _traverse(self, obj, seed):
        self._iassign(obj, seed)
        seeds = iter(self._irecurse(obj, seed))
        for member in self._imembers(obj):
            self._traverse(member, next(seeds))
