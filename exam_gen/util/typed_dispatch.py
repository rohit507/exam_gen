from copy import copy, deepcopy
from pprint import pformat, pprint
from textwrap import dedent, indent
from collections import Iterable

import inspect

import attr
import attr.validators as valid

import exam_gen.util.logging as logging

log = logging.new(__name__, level="WARNING")

class TypedDispatch():
    """
    Get a value (usually a function) based on the type of a presented object.
    """

    def __init__(self, *vargs, default_class = None):
        log.debug(
            dedent("""
            Initializing new typed dispatch with args:
            %s
            """),
            indent(pformat(vargs), "    ")
            )


        self._dispatch = dict()
        self._default = None

        if (len(vargs) == 0):
            raise RuntimeError("Invalid Init of TypedDispatch")

        if len(vargs) >= 1:
            self.add_default(vargs[0])

        if len(vargs) >= 2:
            for (cls, val) in vargs[1:]:
                self.add_dispatch(cls, val)

        if self.default == None:
            raise RuntimeError("Invalid TypedDispatch Init")

    def add_dispatch(self, cls, val):
        if not inspect.isclass(cls):
            raise RuntimeError("Tried to add non-class to typedDispatch")
        self._dispatch[cls] = val

    def add_default(self, val):
        self._default = val

    def dispatch (self, val):
        disp_cls = disp_val = None

        # Find the "Closest" parent class to value, the one which is a
        # superclass to the value and a subclass to every other parent class
        # in the set. Arbitrarily chooses a return val if there's multiple
        # dispatchers of equal "distance"
        for (cls, cls_val) in self.dispatcher_list:
            if isinstance(val, cls):
                if (disp_cls == None) or issubclass(cls, disp_cls):
                    disp_cls, disp_val = cls, cls_val

        if disp_cls == None:
            disp_val = self._default

        return disp_val

    @property
    def dispatcher_list(self):
        return self._dispatch.items()

    @property
    def dispatcher_map(self):
        return self._dispatch.items()

    @property
    def default(self):
        return self._default

    def combine(self, other = None):
        """
        Make a copy of this dispatcher. If there's an 'other' param provided
        then copy all of its dispatchers and defaults, overriding if there's
        any overlap.
        """

        output = TypedDispath(self.default, *self.dispatcher_list)
        if other != None:
            for (k,v) in other.dispatcher_list:
                output.add_dispatch(k,v)
            output.add_default(other.default)


            log.debug(
                dedent("""
                Combining Dispatchers:

                  Self:
                %s

                  Self Default:
                %s

                  Self Dispatch List:
                %s

                  Other:
                %s

                  Other Default:
                %s

                  Other Dispatch List:
                %s

                  Result:
                %s

                  Result Default:
                %s

                  Result Dispatch List:
                %s


                """),
                indent(pformat(self), "    "),
                indent(pformat(self.default), "    "),
                indent(pformat(self.dispatcher_list), "    "),
                indent(pformat(other), "    "),
                indent(pformat(other.default), "    "),
                indent(pformat(other.dispatcher_list), "    "),
                indent(pformat(output), "    "),
                indent(pformat(output.default), "    "),
                indent(pformat(output.dispatcher_list), "    "),
            )

        return output
