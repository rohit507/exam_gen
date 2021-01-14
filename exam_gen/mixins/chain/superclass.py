from copy import copy, deepcopy
from pprint import pformat, pprint
from textwrap import dedent, indent
from collections import Iterable

import inspect

import attr
import attr.validators as valid

from exam_gen.util.attrs_wrapper import attrs
import exam_gen.util.logging as logging
from exam_gen.mixins.chain.util import *
from exam_gen.mixins.prepare_attrs import PrepareAttrs

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

        def mark_func(self, typ = None, func = None, *, default = False):
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

                if typ != None:
                    getattr(self, dispatcher_name).add_dispatch(
                        typ, updated_function)
                else:
                    getattr(self, dispatcher_name).add_default(
                        updated_function)

                return self

            return update(func) if func != None else update

        mark_func.__doc__ = transform_func.__doc__

        return mark_func

    return wrapper


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
            attr = getattr(self, attrib.name, None)
            if (attr != None) and isinstance(attr, TypedDispatch):
                attr.add_dispatch(obj, attr.default)



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


@attr.s
class Gatherer(TraversalBase):
    """
    Traverse the set of objects and gather some information.

      - gather: Gets the info for this specific member, should have sig:
        `def gather_func(self): ... return my_data`

      - combine: Combine info from myself ans all children. Should have sig:
        `def combine_func(self, my_data, child_data): ... return combined_data`
        The child_data will be a list where each item is the combined data of
        the specific child.

     - members: The children of this object used for this traversal, with sig:
       `def members_func(self): ... return child_list`
    """

    _gather = attr.ib(
        converter = TypedDispatch,
    )

    @traversal_dispatcher(dispatcher_name = '_gather')
    def _gather_indirect(): pass

    @traversal_updater(dispatcher_name = '_gather')
    def gather(self, func): return func

    _combine = attr.ib(
        default = lambda self, item, items: itertools.chain(item, *items),
        converter = TypedDispatch,
        kw_only = True,
    )

    @traversal_dispatcher(dispatcher_name = '_combine')
    def _combine_indirect(): pass

    @traversal_updater(dispatcher_name = '_combine')
    def combine(self, func): return func

    @classmethod
    @traversal_decorator(key_param = 'gather')
    def decorate(cls, gather, **kwargs):
        return Gatherer(gather, **kwargs)

    def __get__(self, obj, objtype = None):
        def func() : return self._collect(obj)
        return func

    def _collect(self, obj):
        item = [self._gather_indirect(obj)]
        items = [self._collect(x) for x in self._members_indirect(obj)]
        return self._combine_indirect(obj, item, items)

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

@attr.s
class PropagateDown(TraversalBase):
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
        return PropagateDown(descend, **kwargs)

    def __get__(self, obj, objtype = None):
        def func(data) : return self._push(obj, data)
        return func

    def _push(self, obj, data):
        new_data = self._descend_indirect(obj, data)
        for member in self._members_indirect(obj):
            self._push(member, self._copy_indirect(obj, new_data))

# Fold through members one item after another, gathering data from
# the parents, and pass through each child
# Has `use`, `members`, and `copy`
@attr.s
class TreeTraverse(TraversalBase):
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
        return TreeTraverse(modify, **kwargs)

    def __get__(self, obj, objtype = None):
        def func(data) : return self._traverse(obj, data)
        return func

    def _traverse(self, obj, pred_data):
        (succ_data, child_data) = self._modify_indirect(obj, pred_data)
        for member in self._members_indirect(obj):
            child_data = self._traverse(member, child_data)
        return succ_data
