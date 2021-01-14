from copy import copy, deepcopy
from pprint import pformat, pprint
from textwrap import dedent, indent
from collections import Iterable

import inspect

import attr
import attr.validators as valid

from exam_gen.mixins.traversals.typed_dispatch import TypedDispatch

import exam_gen.util.logging as logging

log = logging.new(__name__, level="WARNING")

def traversal_dispatcher(dispatcher_name):
    """
    A decorator for a function to get the value from the dispatcher for a
    particular sub-object. Ignores everthing about the function it's decorating
    other then the documentation.

    Assumes the dispatcher has functions where the object is the first param.
    """

    def wrapper(func):

        def get_dispatch(self, obj):
            """
            Create a getter to get the relevant function or member.

            If the object has a decorator of the same name and type
            its dispatcher will be used over this class'
            """

            self_dispatch = getattr(self, dispatcher_name)
            self_decor = getattr(obj, self._name, None)

            dispatch, obj_decor = self_dispatch, self_decor
            obj_dispatch = getattr(obj, dispatcher_name, None)

            # If we have a genuinely different object we're iterating over
            # that has an identical traversal then include its dispatcher
            # over our own.
            if ((obj_dispatch != None)
                and (obj != self._owner)
                and (obj_decor != None)
                and (obj_decor != self)
                and isinstance(obj_decor, type(self))):
                dispatch = obj_dispatch.combine(dispatch)

            log.debug(
                dedent("""
                Getting Dispatched for:

                  Dispatcher Name:
                %s

                  Dispatch Function:
                %s

                  Self:
                %s

                  Owner:
                %s

                  Object Decorator:
                %s

                  Object Dispatcher:
                %s

                  Target Object:
                %s

                  Target Dispatcher:
                %s

                  Return Dispatcher:
                %s

                  Return Dispatch Default:
                %s

                  Return Dispatch List:
                %s
                """),
                indent(dispatcher_name, "    "),
                indent(func.__qualname__, "    "),
                indent(pformat(self), "    "),
                indent(pformat(self._owner), "    "),
                indent(pformat(self_decor), "    "),
                indent(pformat(self_dispatch), "    "),
                indent(pformat(obj), "    "),
                indent(pformat(obj_dispatch), "    "),
                indent(pformat(dispatch), "    "),
                indent(pformat(dispatch.default), "    "),
                indent(pformat(dispatch.dispatcher_list), "    "),
                )

            return dispatch

        def with_dispatch(self, obj, *vargs, **kwargs):
            """
            Use the 'obj' argument to get the appropriate dispatcher from
            `self` then pass `obj` and the rest of the args to the retrieved
            function.
            """

            disp = get_dispatch(self, obj)
            ret_func = disp.dispatch(obj)
            out = ret_func(obj, *vargs, **kwargs)
            log.debug(
                dedent("""
                Calling Dispatcher '%s' via '%s':

                  Self:
                %s

                  Obj:
                %s

                  Vargs:
                %s

                  Kwargs:
                %s

                  Result:
                %s

                  Result Default:
                %s

                  Result Dispatch List:
                %s

                  Return Func:
                %s

                  Return Func Sig
                %s

                  Result:
                %s
                """),
                dispatcher_name,
                func.__qualname__,
                indent(pformat(self), "    "),
                indent(pformat(obj), "    "),
                indent(pformat(vargs), "    "),
                indent(pformat(kwargs), "    "),
                indent(pformat(disp), "    "),
                indent(pformat(disp.default), "    "),
                indent(pformat(disp.dispatcher_list), "    "),
                indent(pformat(ret_func), "    "),
                indent(pformat(inspect.signature(func)), "    "),
                indent(pformat(out), "    "),
            )
            return out

        with_dispatch.__doc__ = func.__doc__

        log.debug(
            dedent("""
            Creating dispatcher for variable '%s':

              Dispatcher Name:
            %s

              Dispatcher Signature:
            %s

              Return Function:
            %s
            """),
            dispatcher_name,
            indent(func.__qualname__, "    "),
            indent(pformat(with_dispatch), "    "),
        )

        return with_dispatch

    return wrapper

def traversal_decorator(key_param):
    """
    A decorator that generates the initial decorator for a traversal class, by
    wrapping a function that calls "init", and assigning one of its components
    as

    The key parameter is the one that's assumed to be the default and the
    first param when using the decorator.
    """

    def wrapper(func):

        def decorate(cls, *vargs, **kwargs):
            """
            The decorator for the traversal we're building with the
            `traversal_decorator` decorator.
            """

            log.debug(
                dedent("""
                Using Decorator to Construct Traversal:

                  Class:
                %s

                  Function:
                %s

                  Vargs:
                %s

                  Kwargs:
                %s
                """),
                indent(pformat(cls), "    "),
                indent(func.__qualname__, "    "),
                indent(pformat(vargs), "    "),
                indent(pformat(kwargs), "    "),
            )

            def create(key_func):
                """
                Function that, given just the key field, will construct the
                final traversal descriptor object.
                """
                out_kwargs = deepcopy(kwargs)

                if ('doc' not in kwargs) or (kwargs['doc'] == None):
                    out_kwargs['doc'] = key_func.__doc__

                if key_func != None:
                    out_kwargs[key_param] = key_func
                elif 'key_param' not in kwargs:
                    raise RuntimeError("Invalid Decorator Init")

                out_vargs = tuple(vargs[1:])
                dec = func(cls, *out_vargs, **out_kwargs)

                log.debug(
                    dedent("""
                    Constructing Decorator Object:

                      Input Function:
                    %s

                      Result Vargs
                    %s

                      Result Kwargs:
                    %s

                      Decorator:
                    %s

                      Decorator Dir:
                    %s
                    """),
                    indent(pformat(key_func), "    "),
                    indent(pformat(out_vargs), "    "),
                    indent(pformat(out_kwargs), "    "),
                    indent(pformat(dec), "    "),
                    indent(pformat(dir(dec), compact=True), "    "),
                   )

                return dec

            # If we have the key field just create the final descriptor
            # otherwise return `create` so that it can be used as a decorator.
            if (len(vargs) == 1) and (key_param not in kwargs):
                return create(vargs[0])
            elif key_param not in kwargs:
                return create
            else:
                return create(None)

        decorate.__doc__ = func.__doc__

        log.debug(
            dedent("""
            Constructing new decorator function for decorator:

              Key Param:
            %s

              Func Name:
            %s

              Input Signature:
            %s

              Output Signature:
            %s
            """),
            indent(key_param, "    "),
            indent(func.__qualname__, "    "),
            indent(pformat(inspect.signature(func)), "    "),
            indent(pformat(inspect.signature(decorate)), "    "),
        )

        return decorate

    return wrapper

def traversal_updater(dispatcher_name):
    """
    This is a decorator that will make a function update a dispatcher based
    on the provided arguments.

    The function on the traversal that this decorator is applied to should
    transform the function that the user is passing to update a specific field
    of the descriptor.

    Alternately if that function returns None (as a function with a body of
    `pass` would) then the function this decorates will just be used for its
    docstring.
    """

    def wrapper(transform_func):

        log.debug(
            dedent("""
            Constructing new updater for decorator:

              Dispatcher Name:
            %s

              Transform Func Name:
            %s
            """),
            indent(dispatcher_name, "    "),
            indent(transform_func.__qualname__, "    ")
        )

        def mark_func(self, typ = None, func = None, *, default = None):
            """
            Function we're creating that will modify a typed dispatcher on
            the descriptor.

            Can be used in multiple ways:

               1. As a function `d.foo(typ, func)` which will modify the
                  decorator `d` by updating `foo` with a new typed dispatch
                 option.
               2. As a function `d.foo(func)` which will update the default
                  for the dispatcher.
               3. As a decorator `@d.foo` which will use the function it's
                  decorating as the new default. (Functions as case 2 in the
                  background)
               4. As a decorator `@d.foo(typ)` which will use the function
                  it's decorating as a dispatcher for `typ`.

            These all work when used with keyword arguments instead of just
            positional.

            We differentiate between cases 2-3 and 4 based on whether in single
            argument that's provided is a function (cases 2-3) or a class
            (case 4).

            Setting `default = True` will override the `typ` parameter and
            use the input function as a default value. Useful for if you
            decorate a function that is meant for the specific class and
            want to override it later.

            If `default=False` and no type is specified then we assume we're
            writing the dispatcher for the owner class of this decorator.
            """

            if (inspect.isfunction(typ)
                and (not inspect.isclass(typ))
                and (func == None)):
                func = typ
                typ = None

            if default:
                typ = None

            log.debug(
                dedent("""
                Setting %s for Decorator '%s':

                  Decorator:
                %s

                  New Type:
                %s

                  Marking Func:
                %s
                """),
                transform_func.__qualname__,
                self._name,
                indent(pformat(self), "    "),
                indent(pformat(typ), "    "),
                indent(pformat(func), "    "),
            )

            def update(input_function):
                """
                This function actually updates the decorator with the input
                function, whether that's provided by a decorator or just
                passed in directly.
                """

                updated_function = transform_func(self, input_function)

                # Handles case where transform doesn't return anything
                if updated_function == None:
                    updated_function = input_function

                log.debug(
                    dedent("""
                    Updating parameter %s for decorator '%s':

                      Decorator:
                    %s

                      New Type:
                    %s

                      Input Function:
                    %s

                      Transformed Function:
                    %s
                    """),

                    transform_func.__qualname__,
                    self._name,
                    indent(pformat(self), "    "),
                    indent(pformat(typ), "    "),
                    indent(pformat(input_function), "    "),
                    indent(pformat(updated_function), "    "),
                )

                disp = getattr(self, dispatcher_name)

                if typ != None:
                    # There is a type specified, so we're definitely adding a
                    # dispatch
                    disp.add_dispatch(typ, updated_function)

                    # We're also making that the default
                    if default == True: disp.add_default(updated_func)
                elif default == None:
                    # If there's no type then this sets both the
                    # dispatcher for the owner of this decorator and the
                    # default.
                    disp.add_default(updated_function)
                    self.flag_default_disp(dispatcher_name, updated_function)
                elif default == False:
                    # if there's no type and there's no default, then it's
                    # for just this class.
                    self.flag_default_disp(dispatcher_name, updated_function)
                else:
                    # Otherwise there's no type and default is true so we
                    # just set the default.
                    disp.add_default(updated_function)

                return self

            return update(func) if func != None else update

        mark_func.__doc__ = transform_func.__doc__

        return mark_func

    return wrapper
