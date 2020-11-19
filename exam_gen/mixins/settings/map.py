from exam_gen.mixins.settings.errors import *
from exam_gen.mixins.settings.data import *
from inspect import isclass
from textwrap import indent, dedent

class SettingsMap:
    """
    Create a new `SettingsMap` object for storing the different settings a
    class is allowed to have.

    Parameters:

        context (class or object): The current context with which the map
            is being manipulated. This is used to track when variables are
            set and updated.
        root (SettingsMap): The root of the `SettingsMap` tree this is part
            of. If `None`, this object is the root of the tree.
    """

    def __init__(self,
                 context,
                 root = None,
                 path = [],
                 description = None,
                 context_stack = [],
                 **kwargs
    ):
        self.kwargs = kwargs
        super().__init__(**kwargs)

        if context == None:
            raise RuntimeError("There must be a current context in which this"+
                               " SettingsMap is initialized.")

        self.context_stack = context_stack
        self.context = context
        self.root = root
        self.path = path
        self.docs_dirty = True
        self.docs = None
        self.description = description
        self.members = dict()


    def __getattr__(self, name):
        # If there's a member
        if name in self.members:
           member = self.members[name]
           if isinstance(member, SettingInfo):
               return member.get_val(self)
           elif isinstance(member, SettingsMap):
               return member
           else:
               raise RuntimeError("Internal Error w/ SettingsMap")
        elif hasattr(super(), name):
            super().__getattr__(name)
        else:
          raise NoSuchSettingError("Could not find setting '{}.{}'.".format(
              self.path_string, name))

    def __setattr__(self, name, value):
        if isinstance(value, SettingInfo):
            if value.creating:
                self.__new_setting(name, value)
            elif value.updating:
                self.__update_setting(name, value)
            else:
                raise RuntimeError("Internal Error w/ SettingsMap")
        elif isinstance(value, SettingOption):
            self.__add_option(name, value)
        elif (name in self.members) and isinstance(value, dict):
            self.__update_settings_map(name, value)
        elif (not hasattr(super(), name)) and isinstance(value, dict):
            self.__new_settings_map(name, value)
        elif name in self.members:
            member = self.members[name]
            if isinstance(member, SettingInfo):
                member.set_val(value, name, self)
            else:
                raise NoSuchSettingError(
                    ("No settings exists at `{}.{}`."
                    ).format(self.path_string, name))
        else:
            super().__set_attr__(name, value)

    def __iadd__(self, other):
        if isinstance(other, dict):
            for (name, val) in other:
                self.__set_attr__(name, val)
        else:
            raise InvalidBulkAssignmentError("Expected a dict as input " +
                                             "to bulk setting assignment.")

    def copy(self, context, root = None, path = []):

        new_map = SettingsMap(context,
                              root,
                              path,
                              self.description,
                              [self.context] + self.context_stack,
                              **self.kwargs)

        root = new_map if root == None else root

        for (name, member) in self.members.items():
            if isinstance(member, SettingInfo):
                new_setting = member.copy(context, root, path)
                new_setting.creating = True
                new_map.__set_attr__(name, new_setting)
            elif isinstance(member, SettingsMap):
                new_submap = member.copy(context,
                                         root,
                                         path + [name])
                new_map.__new_raw_settings_map(name, new_submap)
            else:
                raise RuntimeError("Internal Error w/ SettingsMap")

        return new_map

    def new_setting_func(self):
        # get a new_setting function for the current context

        # create a function which will create new settings objects with the
        # correct initial context and properties for whatever we're up to.
        raise NotImplementedError

    def update_setting_func(self):
        # get an update_setting function for the current context
        raise NotImplementedError

    def option_func(self):
        # get a option function for the current context
        raise NotImplementedError

    def add_option_func(self):
        # get an add/update option function for the current context.
        raise NotImplementedError

    def dirty_all_validation(self):
        for (name, member) in self.members.items():
            if isinstance(member, SettingInfo):
                member.dirty()
            elif isinstance(member, SettingsMap):
                member.dirty_all_validation()

    def dirty_validation(self, name):
        if name in self.members:
            member = self.members[name]
            if isinstance(member, SettingInfo):
                member.dirty()
            elif isinstance(member, SettingsMap):
                member.dirty_all_validation()
        else:
            raise NoSuchSettingError(
                ("No setting `{}.{}` to mark as dirty."
                 ).format(self.path_string, name))

    def validate_all(self):
        for (name, member) in self.members.items():
            if isinstance(member, SettingInfo):
                member.validate(name, self)
            elif isinstance(member, SettingsMap):
                member.validate_all()

    def validate(self, name):
        if name in self.members:
            member = self.members[name]
            if isinstance(member, SettingInfo):
                member.validate(name, self)
            elif isinstance(member, SettingsMap):
                member.validate_all()
        else:
            raise NoSuchSettingError(
                ("No setting `{}.{}` to validate."
                 ).format(self.path_string, name))

    def derive_all(self):
        for (name, member) in self.members.items():
            if isinstance(member, SettingInfo):
                member.derive(name, self)
            elif isinstance(member, SettingsMap):
                member.derive_all()

    def derive(self, name):
        if name in self.members:
            member = self.members[name]
            if isinstance(member, SettingInfo):
                member.derive(name, self)
            elif isinstance(member, SettingsMap):
                member.derive_all()
        else:
            raise NoSuchSettingError(
                ("No setting `{}.{}` to derive value for."
                 ).format(self.path_string, name))

    def set_context(self, context):
        self.context_stack = [context] + self.context_stack
        self.context = context

    def make_docstring(self, context):
        raise NotImplementedError

    def gather_docs(self, context):
        raise NotImplementedError

    @property
    def path_string(self):
        return '.'.join(self.path)

    @property
    def __is_root(self):
        return self.root == None

    @property
    def get_root(self):
        return self if self.root == None else root

    def __new_setting(self, name, info): pass

    def __update_setting(self, name, info): pass

    def __new_settings_map(self, name, info): pass

    def __new_raw_settings_map(self, name, smap): pass

    def __update_settings_map(self, name, opts): pass

    def __add_option(self, name, info): pass

    def __set_value(self, name, info): pass
