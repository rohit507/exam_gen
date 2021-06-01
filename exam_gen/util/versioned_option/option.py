import attr
import functools

from copy import *
from pprint import *

from .object import VersionedObj

import exam_gen.util.logging as logging


log = logging.new(__name__, level="WARNING")

__all__ = ["VersionedOptions"]


@attr.s
class VersionedOptions(VersionedObj):

    _option_spec = attr.ib(factory = dict)
    options = attr.ib(factory = dict)

    def __attrs_post_init__(self):
        self.pre_init = False
        if self._parent != None:
            self._option_spec = self._parent._option_spec
            self.options = deepcopy(self._parent.options)

    def __getattr__(self, name):
        """
        Gets an attribute, if it's in our options dict and missing then
        retrieve it from the parent.
        """

        if name == 'pre_init':
            raise AttributeError("{} attr not found pre-init".format(name))


        if name not in self.__getattribute__('_option_spec'):
            log.debug(pformat(self.var_name))
            log.debug(pformat(self._option_spec))
            # raise AttributeError("No such option.")
            return super(VersionedOptions, self).__getattribute__(name)
        # log.error("getting attr %s from %s", name, self.var_name)

        if name in self.options:
            return self.options[name]
        elif 'default' in self._option_spec[name]:
            return self._option_spec[name]['default']
        elif 'factory' in self._option_spec[name]:
            return self._option_spec[name]['factory']()

        if self._parent != None:
            return getattr(self._parent, name)

        raise AttributeError("No attribute '{}' found in '{}'".format(
            name, self.var_name))

    def setattr_single(self, name, value):
        """
        Will set an attribute, looks in the option spec first.
        """

        if name in self._option_spec:

            spec =  self._option_spec[name]

            if (('root_only' in spec)
                and (self.parent != None)
                and spec['root_only']):

                raise RuntimeError(("Option `{}` can only be set at the root "
                                    "level of this term.").format(name))

            self.options[name] = deepcopy(value)

        else:

            super(VersionedOptions,self).__setattr__(name, value)

    def __setattr__(self, name, value):

        if not hasattr(self,'pre_init'):
            super(VersionedOptions, self).__setattr__(name, value)
            return None

        set_func = functools.partial(
            VersionedOptions.setattr_single,
            name=name,
            value=value)

        self.prop_child_func(
            set_func,
            apply_self = True,
            apply_child = True)

    def apply_version_tree(self, tree, override=False):

        def merge_opts(self, other):
            for (name, val) in other.options.items():
                if override or (name not in self.options):
                    setattr(self, name, val)

        apply_func = self.mk_apply_tree_func(merge_opts)

        apply_func(self, tree)
