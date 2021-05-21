import attr
import functools
from copy import *

from exam_gen.util.typed_dispatch import TypedDispatch

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

__traversal

@attr.s
class Traversable():
    """
    Traversable objects contain a tree of named sub-objects under various
    variables which can be walked over with other functions.
    """

    __traversable_vars__ = []
    """
    list of class variables that can contain subdocument sets.
    """

    _traversables = attr.ib(factory=dict, init=False)
    """
    a dictionary of subcomponent sets found within this document.
    """

    _traversable_cache = attr.ib(factory=dict, init=False)
    """
    Different caches for each set of subcomponents.
    """

    def __init_subclass__(cls, *vargs, **kwargs):
        """
        Will go through the variables in `__traversable_vars__` and generate
        the stub properties for each of them.
        """

        super().__init_subclass__(*vargs, **kwargs)

        final_traversable_vars = list()

        for var_spec in cls.__traversable_vars__:

            spec = Traversable._format_var_spec(var_spec)
            var_name = spec['var']

            cls._traversables[var_name] = getattr(cls, var_name, dict())

            Traversable._setup_tvar(cls, spec)
            if spec['cache'] != None: Traversable._setup_tcache(cls, spec)

            final_traversable_vars.append(spec)

        cls.__traversable_vars__ = final_traversable_vars

    @staticfunction
    def _format_var_spec(cls, var_spec):

        if isinstance(var_spec, str):
            var_spec = {'var': var_spec}
        elif isinstance(item, dict):
            pass
        else:
            raise RuntimeError(("Invalid entry in `__traversable_vars__`"))

        assert ('var' in var_spec), "No var name provided in traversable"

        # convenience
        spec['singular'] = var_spec.get('singular', default = var_spec['var'])

        # traversable var
        spec['var'] = var_spec['var']

        spec['getter'] = var_spec.get('getter', None)
        if spec['getter'] == True:
            spec['getter'] = "get_{}".format(spec['singular'])
        spec['getter_doc'] = var_spec.get('getter_doc', None)

        spec['setter'] = var_spec.get('setter', None)
        if spec['setter'] == True:
            spec['setter'] = "set_{}".format(spec['singular'])
        spec['setter_doc'] = var_spec.get('setter_doc', None)

        spec['doc'] = spec.get('doc', None)

        # var cache
        spec['cache'] = spec.get('cache',None)
        if spec['cache'] == True:
           spec['cache'] = "__{}_cache".format(spec['var'])

        spec['cache_getter'] = var_spec.get('cache_getter',None)
        if spec['cache_getter'] == True:
            spec['cache_getter'] = "get_{}_cache".format(spec['singular'])
        spec['cache_getter_doc'] = var_spec.get('cache_getter_doc', None)

        spec['cache_setter'] = var_spec.get('cache_setter',None)
        if spec['cache_setter'] == True:
            spec['cache_setter'] = "set_{}_cache".format(spec['singular'])
        spec['cache_setter_doc'] = var_spec.get('cache_setter_doc', None)

        spec['cache_doc'] = spec.get('cache_doc', None)

        return spec

    @staticfunction
    def _setup_tvar(cls, spec):

        def get_t(self, t_v): return self._traversables[t_v]

        if spec['var_doc'] != None: get_t.__doc__ = spec['var_doc']

        setattr(cls, spec['var'], property(get_t))

        def get_var(self, name, *, t_v):
            if name not in self._traversables[t_v]:
                return None
            else:
                return self._traversables[t_v][name]

        if spec['getter_doc']: get_var.__doc__ = spec['getter_doc']

        if spec['getter']:
            setattr(cls,  spec['getter'],
                    functools.partial(get_var, t_v = spec['var']))

        def set_var(self, name, value, *, t_v):
            if t_v not in self._traversables:
                self._traversables[t_v] = dict()
            self._traversables[t_v][name] = value

        if spec['setter_doc']: get_var.__doc__ = spec['setter_doc']

        if spec['setter']:
            setattr(cls, spec['setter'],
                    functools.partial(set_var, t_v = spec['var']))

    @staticfunction
    def _setup_tcache(cls, spec):

        def get_t_c(self, tc_v): return self._traversable_cache[tc_v]

        if spec['cache_doc'] != None: get_t_c.__doc__ = spec['cache_doc']

        setattr(cls, spec['cache'], property(get_t_c))

        def get_cache_var(self, name, *, t_v):
            if name not in self._traversable_cache[t_v]:
                return None
            else:
                return self._traveraable_cache[t_v][name]

        if spec['cache_getter_doc']:
            get_cache_var.__doc__ = spec['cache_getter_doc']

        if spec['cache_getter']:
            setattr(cls,
                    spec['cache_getter'],
                    functools.partial(get_cache_var, t_v = spec['var']))

        def set_var(self, name, value, *, c_v, t_v):
            if t_v not in self._traversable_cache:
                self._traversable_cache[t_v] = dict()
            self._traversable_cache[t_v][name] = value

        if spec['cache_setter_doc']:
            get_cache_var.__doc__ = spec['cache_setter_doc']

        if spec['cache_setter']:
            setattr(cls,
                    spec['cache_setter'],
                    functools.partial(set_cache_var, t_v = spec['var']))

    def _get_t_var(self, t_var, name):
        if t_var not in self._traversables:
            return None
        elif name not in self._traversables[t_var]:
            return None
        else:
            return self._traversables[t_var][name]

    def _get_t_cache(self, t_var, name):
        if t_var not in self._traversable_cache:
            return None
        elif name not in self._traversable_cache[t_var]:
            return None
        else:
            return self._traversable_cache[t_var][name]

    def _set_t_var(self, t_var, name, val):
        if t_var not in self._traversables:
            self._traversables[t_var] = dict()
        self._traversable_cache[t_var][name] = val

    def _set_t_cache(self, t_var, name, val):
        if t_var not in self._traversable_cache:
            self._traversable_cache[t_var] = dict()
        self._traversable_cache[t_var][name] = val

    def _has_t_var(self, t_var):
        return (t_var in self._traversables)

    @staticfunction
    def make_walk(setup, step, finalize):
        """
        Helper to make it easy to walk though the various children of a
        traversable. You should be handling type fallbacks and similar in the
        functions you pass in, raither

        Parameters:

           setup: `(self) -> A` which creates the initial data that goes to
             children

           step: A function
             `(self, t_var : str, name : str, member, init : A, recurse) -> B`
             called on each child. The last parameter is `(self) -> C` that
             is the recursive call for this function

           finalize: `(self, init : A, result : Dict[t_var,Dict[name, B]]) -> C`

        Returns:

           `(self) -> C`: Function that will do the recursive call on your
           element of choice.
        """

        # stupidity to deal with python being stupid. This is the best way to
        # get python to defer a call to make_walk until it's needed by `step`
        def _recurse(self,
                     setup = setup,
                     step=step,
                     finalize=finalize):
            return Traversable.make_walk(setup, step, finalize)(s)

        def walk(self, *, setup, step, finalize):

            init = setup(self)
            result = dict()

            for (t_var, membs) in self._traversables.items():

                result[t_var] = dict()

                for (name, member) in membs.items():


                    params = dict(
                        t_var = t_var,
                        name = name,
                        member = member,
                        init = init,
                        recurse = _recurse,
                        get_var = functools.partial(
                            self._get_t_var, name=name, t_var=t_var),
                        set_var = functools.partial(
                            self._set_t_var, name=name, t_var=t_var),
                        get_cache = functools.partial(
                            self._get_t_cache, name=name, t_var=t_var),
                        set_cache = functools.partial(
                            self._set_t_cache, name=name, t_var=t_var)
                    )

                    result[t_var][name] = step(self,**params)

            return finalize(self, init, result)

        return functools.partial(
            walk,
            setup=setup,
            step=step,
            finalize=finalize)

@attr.s
class Traversal():

    var = attr.ib()
    _cache = attr.ib(default=None)

    _setup = attr.ib(default=None)
    _child = attr.ib(default=None)
    _recurse = attr.ib(default=None)
    _finish = attr.ib(default=None)

    _doc = attr.ib(default=None)

    _owner = attr.ib(default=None, init=False)
    _name = attr.ib(default=None, init=False)

    def __set_name__(self, owner, name):
        self._owner = owner
        self._name = name

    def __get__(self, owner, objtype=None):
        pass

    def __call__(self, *args, **kwargs):
        pass

    def __attrs_post_init__(self):
        self._setup_docstring()


    @static_function
    def default_setup(trav, self, *vargs, **kwargs):
        return self

    @static_function
    def default_child(trav, self, name, child, *vargs, **kwargs):
        """
        """
        pass

    @static_function
    def default_recurse(trav, self, *vargs, **kwargs):
        pass

    @static_function
    def default_finish(trav, self, results):
        return results

    @staticfunction
    def default_call(trav, self, *vargs, **kwargs):
        if isinstance(self, Traversable) and self._has_t_var(trav._var):
            parent_context = trav._setup_func(self, *vargs, **kwargs)
            results = dict()
            for (name, entry) in self._traversables[trav._var].items():
                params = dict()
                params['input'] = parent_context
                results[name] = trav._child_func(entry,
                                                 self,
                                                 parent_context,
                                                 *vargs,
                                                 **kwargs)
            return trav._finish_func(self, parent_context, results)
        else:
            return None

    def _recurse(self, child, vargs=[], kwargs={}):
        # Check if child has parameter w/ name
        if hasattr(child, self._name):
            return getattr(child, self._name)(*vargs, **kwargs)
        else: # otherwise use our dis
            return self._child.dispatch(child)(*vargs, **kwargs)
        pass

    def _setup_docstring(self):

        if hasattr(self,'__doc__'):
            pass
        elif self._doc:
            self.__doc__ = self._doc
        elif hasattr(self._setup,'__doc__'):
            self.__doc__ = self._setup.__doc__
        elif hasattr(self._child,'__doc__'):
            self.__doc__ = self._child.__doc__
        elif hasattr(self._finish,'__doc__'):
            self.__doc__ = self._finish.__doc__
