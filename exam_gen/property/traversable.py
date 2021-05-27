import attr
import functools
import textwrap

from copy import *
from pprint import *

import exam_gen.util.logging as logging

log = logging.new(__name__, level="WARNING")

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

        log.debug("initializing Traversable for subclass: {}".format(cls))

        super().__init_subclass__(*vargs, **kwargs)

        final_traversable_vars = list()

        cls._traversables = getattr(cls, '_traversables', dict())
        cls._traversable_cache = getattr(cls, '_traversable_cache', dict())

        for var_spec in cls.__traversable_vars__:

            spec = Traversable._format_var_spec(cls, var_spec)
            var_name = spec['var']

            cls._traversables[var_name] = getattr(cls, var_name, dict())

            Traversable._setup_tvar(cls, spec)
            if spec['cache'] != None: Traversable._setup_tcache(cls, spec)

            final_traversable_vars.append(spec)

        cls.__traversable_vars__ = final_traversable_vars

    def __attrs_post_init__(self):
        if hasattr(super(),'__attrs_post_init__'):
            super().__attrs_post_init__()

        self._traversables = getattr(self, '_traversables',
                                     copy(type(self)._traversables))

        self._traversable_cache = getattr(self, '_traversable_cache',
                                          copy(type(self)._traversable_cache))

    @staticmethod
    def _format_var_spec(cls, var_spec):

        if isinstance(var_spec, str):
            var_spec = {'var': var_spec}
        elif isinstance(var_spec, dict):
            pass
        else:
            raise RuntimeError(("Invalid entry in `__traversable_vars__`"))

        assert ('var' in var_spec), "No var name provided in traversable"

        spec = dict()

        # convenience
        spec['singular'] = var_spec.get('singular', var_spec['var'])

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
        if spec['doc'] != None: spec['doc'] = textwrap.dedent(spec['doc'])

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
        if spec['cache_doc'] != None:
            spec['cache_doc'] = textwrap.dedent(spec['cache_doc'])

        return spec

    @staticmethod
    def _setup_tvar(cls, spec):

        def get_t(self, *, t_v):
            if t_v not in self._traversables:
                self._traversables[t_v] = copy(type(self)._traversables[t_v])
            return self._traversables[t_v]

        if spec['doc'] != None: get_t.__doc__ = spec['doc']

        setattr(cls, spec['var'], property(
            functools.partial(get_t, t_v = spec['var'])))

        def get_var(self, name, *, t_v):
            t_dict = get_t(self, t_v)
            if name not in t_dict:
                return None
            else:
                return t_dict[name]

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

    @staticmethod
    def _setup_tcache(cls, spec):
        # TODO: Fix this to add the checks from `_setup_tvar`
        # they should mirror each other pretty closely.

        def get_t_c(self, tc_v): return self._traversable_cache[tc_v]

        if spec['cache_doc'] != None: get_t_c.__doc__ = spec['cache_doc']

        setattr(cls, spec['cache'], property(
            functools.partial(get_t_c, tc_v = spec['var'])))

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
