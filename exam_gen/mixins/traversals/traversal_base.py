
from copy import copy, deepcopy
from pprint import pformat, pprint
from textwrap import dedent, indent
from collections import Iterable

import inspect

import attr
import attr.validators as valid

from exam_gen.mixins.traversals.typed_dispatch import TypedDispatch
from exam_gen.mixins.traversals.decorators import *

import exam_gen.util.logging as logging

log = logging.new(__name__, level="WARNING")


@attr.s
class TraversalBase():

    _members : TypedDispatch = attr.ib(
        default = lambda self: list(),
        converter = TypedDispatch,
        kw_only = True,
    )

    @traversal_dispatcher('_members')
    def _members_indirect(): pass

    @traversal_updater('_members')
    def members(self, func): return func

    doc = attr.ib(
        default = None,
        validator = valid.optional(valid.instance_of(str)),
        kw_only = True,
    )

    _owner = attr.ib(
        default = None,
        init = False,
    )

    _name = attr.ib(
        default = None,
        init = False,
    )

    _flag_default_disp = attr.ib(
        factory = list,
        init = False
    )

    def flag_default_disp(self, disp_name, func = None):
        """
        This is an indirect way of flagging that a dispatcher should
        have its default set as the handler for its owner.
        """
        self._flag_default_disp.append((disp_name, func))
        if self._owner != None:
            self.apply_default_disp()

    def apply_default_disp(self):
        """
        This will be run to apply a set of default flags once the owner
        and name of this descriptor are set.
        """
        pprint(self._flag_default_disp)
        for (disp_name, func) in self._flag_default_disp:
            disp = getattr(self, disp_name)
            func = func if func != None else disp.default
            disp.add_dispatch(self._owner, func)
        self._flag_default_disp = list()

    @classmethod
    @traversal_decorator(key_param = 'members')
    def decorate(cls, members = None, doc = None):
        return TraversalBase(members, doc)

    def __attrs_post_init__(self):
        self.__doc__ = self.doc

    def __set_name__(self, obj, name):
        self._owner = obj
        self._name = name

        # This is so that the initial attrs for defaults are also used
        # for the specific class we're an instance of.
        #
        # Otherwise we can have errors where the primary declared attr is
        # overriden by a subclass, because the subclass binds tighter than
        # the default.
        for attrib in self.__attrs_attrs__:
            disp = getattr(self, attrib.name)
            if isinstance(disp, TypedDispatch) and (not attrib.kw_only):
                self.flag_default_disp(attrib.name)

        self.apply_default_disp()

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
