import attr
from copy import copy, deepcopy
import functools
import exam_gen.util.logging as logging
from exam_gen.mixins.prepare_attrs import *
from pprint import *
log = logging.new(__name__, level="DEBUG")


EntryKey = attr.make_class("EntryKey",
                           ["depth", "name"],
                           hash=True)

@attr.s
class FormatObj():
    """
    A proxy object that makes it a little nicer to work with a number of
    different options at once.
    """


    var_name = attr.ib()
    parent = attr.ib(default = None, kw_only=True)
    parent_key = attr.ib(default = None, kw_only=True)
    stored_entries = attr.ib(factory=dict, init=None)
    format_spec = attr.ib(factory = list)

    def __setitem__(self, key, val):
        raise RuntimeError("Cannot directly set '{}[{}]'".format(
            self.var_name, key))

    def __getitem__(self, key):

        if len(self.format_spec) == 0:
            raise RuntimeError(("This object has no sub-types, there is "
                                "no valid term like '{}[...]'."
            ).format(self.var_name))

        error = None

        for depth, fmt in enumerate(self.format_spec):
            try:
                new_key = fmt['key_func'](self, key)
            except RuntimeError as err:
                error = err.with_traceback(error)
            else:
                return self.get_entry(EntryKey(depth, new_key))

        raise RuntimeError(
            ("Could not find subtype '{}' for '{}' in  `{}[{}]`."
            ).format(key, self.var_name, self.var_name,key)
        ).with_traceback(error)

    @property
    def root(self):
        return self if self.parent == None else self.parent

    def prop_child_func(self, func, *,
                        key_list=None,
                        apply_self=True,
                        apply_direct_child=True,
                        apply_child=True,
                        apply_parent=False,
                        supress_parent=False):
        """
        One of our children had a set value, propagate that application
        around as needed.

        You should use this to implement getattr and setattr for child classes.

        By default this will apply some function to self and its logical
        children.

        Params:

            func: the function to call, takes self as only parameter

            apply_self: should this call apply the function to self?

            apply_child: should this call apply to children?

            apply_parent: should this call apply to parent elems?

            key_list: a list of links that defines a valid child, used mainly
               to propagate parents.
        """

        if (key_list != None) and (len(key_list) == 0):
            raise RuntimeError("List should always have at least 1 element.")

        if apply_self:
            func(self)

        child_key = None
        succ_list = None

        if (key_list != None) and apply_child:
            child_key = key_list[0]

        if (child_key != None) and (len(key_list) > 1):
            succ_list = key_list[1:]

        # Are we applying the function as we walk directly back up the
        # keylist or should we just propagate things out to other possible
        # children.
        if apply_direct_child and child_key != None:

            self.get_entry(child_key).prop_child_func(
                func,
                key_list = succ_list,
                apply_self = succ_list == None,
                apply_direct_child = True,
                apply_child = apply_child,
                supress_parent = True)

        if apply_child:
            for (key, entry) in self.stored_entries.items():

                # No key_list means we're not trying to filter so we apply the
                # function to all children.
                if key_list == None:

                    entry.prop_child_func(
                        func,
                        apply_self = True,
                        apply_child = True,
                        supress_parent = True)

                # If there is a key_list we only want to apply to relevant
                # children, relevant children (which can have entries that
                # match the list) must be strictly less deep than the child
                # key.
                elif key.depth < child_key.depth:

                    adjusted_list = deepcopy(
                        [EntryKey(child_key.depth - key.depth, child_key.name)]
                        + key_list[1:])

                    entry.prop_child_func(
                        func,
                        key_list=adjusted_list,
                        apply_self=False,
                        apply_direct_child=True,
                        apply_child=True,
                        supress_parent= True)

        # if we're applying parent we need to make a call to parent.
        # if we're applying to children then we need to propagate to parents
        # anyway in order to use other matching child trees.

        if ((not supress_parent) # no other step has taken care of this
            and (apply_parent or apply_child) # we need to do this
            and (self.parent != None)): # we have a parent

            new_list = [self.parent_key]
            new_list += [] if key_list == None else key_list

            self.parent.prop_child_func(
                func,
                key_list = new_list,
                apply_self = apply_parent,
                apply_direct_child = False,
                apply_child = apply_child,
                apply_parent = apply_parent,
                supress_parent = False
                )

    # get a sub-entry, making it up if needed.
    def get_entry(self, key):

        if key in self.stored_entries:
            return self.stored_entries[key]

        new_entry = type(self)("{}[{}]".format(self.var_name, key.name),
                               parent=self,
                               parent_key=key)

        self.stored_entries[key] = new_entry

        return new_entry

    def entry_tree(self):
        tree = dict()

        tree[None] = self

        for (key, entry) in self.stored_entries.items():
            tree[key.name] = entry.entry_tree

        return tree

    def apply_tree(self, tree, override=False):

        for (key, entry) in tree.items():
            if key == None:
                for (name, val) in entry.options.entries():
                    if override or (name not in self.options):
                        setattr(self, name, val)
            else:
                self[key].apply_tree(entry)



@attr.s
class TemplateVar(FormatObj):

    option_spec = attr.ib(factory = dict)
    options = attr.ib(factory = dict)

    def __attrs_post_init__(self):
        self.pre_init = False

    def __getattr__(self, name):
        """
        Gets an attribute, if it's in our options dict and missing then
        retrieve it from the parent.
        """

        if name == 'pre_init':
            raise AttributeError("{} attr not found pre-init".format(name))

        if name not in self.__getattribute__('option_spec'):
            # raise AttributeError("No such option.")
            return super(TemplateVar, self).__getattribute__(name)


        if name in self.options:
            return self.options[name]

        if self.parent != None:
            return getattr(parent, name)

        # return super(self, TemplateVar).__getattr__(name)

    def setattr_single(self, name, value):
        """
        Will set an attribute, looks in the option spec first.
        """

        if name in self.option_spec:

            spec =  self.option_spec[name]

            if (('root_only' in spec)
                and (self.parent != None)
                and spec['root_only']):

                raise RuntimeError(("Option `{}` can only be set at the root "
                                    "level of this template.").format(name))

            s_attr = getattr(self,name,None)

            if s_attr != None:
                raise RuntimeException("Has an option overloading an "
                                       "attribute from a parent class.")

            self.options[name] = deepcopy(value)

        else:

            super(TemplateVar,self).__setattr__(name, value)

    def __setattr__(self, name, value):

        if not hasattr(self,'pre_init'):
            super(TemplateVar, self).__setattr__(name, value)
            return None

        set_func = functools.partial(TemplateVar.setattr_single,
                                     name=name,
                                     value=value)

        self.prop_child_func(set_func,
                             apply_self = True,
                             apply_child = True)

def add_template_var(
        name,
        template_class=None,
        option_spec=None,
        format_spec=None,
        doc=None):

    if doc == None and hasattr(template_class,"__doc__"):
        doc = template_class.__doc__

    if template_class == None:
        template_class = TemplateVar

    class TemplateVarDecor(AttrDecorData):

        @staticmethod
        def prep_attr_inst(prep_meta):
            return template_class(var_name=name,
                                  option_spec=option_spec,
                                  format_spec=format_spec)

        @staticmethod
        def prep_sc_update(cls_val, sc_val, prep_meta):

            opt_spec = sc_val.option_spec | cls_val.option_spec
            cls_val.option_spec = opt_spec

            cls_val.apply_tree(sc_val.entry_tree())

            return cls_val

        @staticmethod
        def scinit_mk_secret_inst(cls_val, scinit_meta):
            return deepcopy(cls_val)

        @staticmethod
        def scinit_attr_docstring(cls_val, scinit_meta):
            return doc

        @staticmethod
        def new_mk_inst(super_obj, cls_inst, new_meta):
            return deepcopy(cls_inst)

    return create_decorator(name, TemplateVarDecor)


__template_var_opts__ = {
    'text':{},
    'file':{},
    'vars':{},
}

__choice_var_opts__ = __template_var_opts__ | {
    'shuffle':{'root_only':True},
    'num':{'root_only':True}
}

__exam_formats__ = ['exam', 'solution']

def exam_format_key_func(self, key):
    if key in __exam_formats__:
        return key
    else:
        raise RuntimeError("{} is not a valid exam format.".format(key))

def multiple_choice_key_func(self, key):
    if not isinstance(key, int):
        raise RuntimeError("Only integers can be used to reference multiple "
                           "choice answers.")
    elif self.num <= key:
        raise RuntimeError(("Key number too high, try setting "
                            "`{}.num` higher").format(self.root.var_name))
    else:
        return key

__template_var_format__ = [
    {'key_func':exam_format_key_func}]

__choice_var_format__ = [{'key_func':multiple_choice_key_func}
                        ] + __template_var_format__

template_var = functools.partial(
    add_template_var,
    format_spec = __template_var_format__,
    option_spec = __template_var_opts__
    )

choice_var = functools.partial(
    add_template_var,
    format_spec = __choice_var_format__,
    option_spec = __choice_var_opts__
    )
