from exam_gen.mixins.settings.errors import *
from exam_gen.mixins.settings.data import *
from inspect import isclass
from textwrap import indent, dedent

class SettingsMap:
    """
    Create a new `SettingsMap` object for storing the different settings a
    class is allowed to have.

    !!! Important
        This in an internal structure that should never be exposed to users
        of this module directly.

    !!! Todo
        Refactor this module in terms of descriptors. In particular both
        SettingInfo and SettingsMap should be descriptors. Most of the error
        and other logic should be handled in a few places when a call is
        resolved.

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
        """
        !!! FIXME
            The correct logic here is:

              - Is attr in __dict__?
                  - Punt to super.__getattr__
              - Is attr in members?
                  - Get attr from members
              - Otherwise
                  - raise AttributeError
        """
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
        """
        !!! FIXME
            The actual logic for this should go:

              - Is the attr in __dict__?
                  - Punt to super().__setattr__
              - Is `value` one of our special types that we use to mark
                settings or settings categories?
                  - Otherwise punt to setters for our special types.
              - Is the value in our list of settings members?
                  - Punt to general setters for settings
              - Else punt to super().__setattr__

        !!! Note
            Special types are: SettingInfo, OptionInfo, SettingMap, and
            dictionaries with string keys and values that are all special
            types. These signal that there's some action to take when
            assigning them to an attribute in a map.
        """
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
        for (k,v) in self.members.items():
            if isinstance(v,SettingsMap):
                v.set_context(context)


    @property
    def path_string(self):
        return '.'.join(self.path)

    @property
    def __is_root(self):
        return self.root == None

    @property
    def get_root(self):
        return self if self.root == None else root

    def __new_setting(self, name, info):
        if not info.creating:
            raise RuntimeError("InternalError in SettingsMap")
        if name in self.members:
            raise SettingAlreadyExistsError(
                ("Trying to create settings `{}.{}` when it already exists."
                ).format(self.path_string, name))
        info.creating = False
        info.updating = False
        self.members[name] = info

    def __update_setting(self, name, info):
        if not info.updating:
            raise RuntimeError("Internal error in SettingsMap")
        if name not in self.members:
            raise NoSettingToUpdateError(
                ("Cannot update non-existent setting `{}.{}`."
                 ).format(self.path_string, name))
        self.members[name].update(info)

    def __new_settings_map(self, name, info):
       if name in self.members:
           raise RuntimeError("Internal Error in SettingsMap.")

       submap = SettingsMap(self.context,
                            self.get_root,
                            self.path + [name],
                            context_stack = self.context_stack)

       for (k,v) in info.items():
           submap.__set_attr__(k,v)

       self.members[name] = submap

    def __new_raw_settings_map(self, name, smap):
        if name in self.members:
            raise RuntimeError("InternalError in SettingsMap.")

        smap.root = self.get_root
        smap.path = self.path + [name]
        smap.context = self.context
        smap.context_stack = self.context_stack

        self.members[name] = smap

    def __update_settings_map(self, name, opts):
        if name not in self.members:
            raise SettingsMapNotUpdatableError(
                ("Cannot update settings sub-category `{}.{}` as it does " +
                 "not exist.").format(self.path_string, name))
        for (k,v) in opts.items:
            self.members[name].__set_attr__(k,v)

    def __add_option(self, name, info):
        if name not in self.members:
            raise NoSettingToUpdateError(
                ("Cannot add new option to setting `{}.{}` as it does not " +
                 "exist.").format(self.path_string, name))
        self.members[name].add_option(info)

    def new_setting_func(self):

        def new_setting(
                short_desc : str,
                long_desc: str = None,
                default: Any = None,
                required = None,
                validator = None,
                validate_on = None,
                derivation = None,
                derive_on_read = True,
                update_with = None,
                copy_with = None,
                options = []
            ):
            """ Test do for internal new_setting func """
            info = SettingInfo(
                definer = self.context,
                setter = self.context if default != None else None,
                value = default,
                short_desc = short_desc,
                long_desc = long_desc,
                needs_validation = default != None,
                required = required,
                validator = validator,
                validate_on = validate_on,
                derivation = derivation,
                derive_on_read = derive_on_read,
                update_with = update_with,
                copy_with = copy_with,
                creating = True
                )

            if isinstance(options, dict):
                for (nm,dsc) in options.items():
                    info.add_option(SettingOption(
                        definer = self.context,
                        name = nm,
                        description = dsc,
                        adding = True))

            return info

        return new_setting

    def update_setting_func(self):
        def update_setting(
                short_desc : str = None,
                long_desc: str = None,
                default: Any = None,
                required = None,
                validator = None,
                validate_on = None,
                derivation = None,
                derive_on_read = True,
                update_with = None,
                copy_with = None,
                options = []
            ):
            """ Test do for internal update_setting func """
            info = SettingInfo(
                definer = self.context,
                setter = self.context if default != None else None,
                value = default,
                short_desc = short_desc,
                long_desc = long_desc,
                needs_validation = default != None,
                required = required,
                validator = validator,
                validate_on = validate_on,
                derivation = derivation,
                derive_on_read = derive_on_read,
                update_with = update_with,
                copy_with = copy_with,
                updating = True
                )

            if isinstance(options, dict):
                for (nm,dsc) in options.items():
                    info.add_option(SettingOption(
                        definer = self.context,
                        name = nm,
                        description = dsc,
                        adding = True))
            elif isinstance(options, list):
                for opt in options:
                    info.add_option(opt)

            return info

        return update_setting

    def option_func(self):
        return self.add_option_func()

    def add_option_func(self):
        def option(name, desc):
            return SettingOption(
                definer = self.context,
                name = name,
                description = desc,
                adding = True)
        return option

    def make_docstring(self, context):
        raise NotImplementedError

    def gather_docs(self, context):
        raise NotImplementedError

    def update(self, other):
        # This needs to be some sort of context aware update operation that
        # will pull from the other SettingsMap while preserving the context
        # stack and other context info.

        # Ideally ties will be broken in MRO order. So the other SettingsMap
        # must come from a parent class or itself.
        pass


class SettingsType(Flag):
    """
    An Enum to capture the different general kinds of data that are relevant
    to the settings module, especially how it responds to attempts to set
    attributes to those values when no attribute already exists.

    Attributes:

       NONE : Not a relevant datatype
       ACTION : Some piece of data that represents a modification to the
           settings tree.
       ADD_DATA : A value that can create a new setting or option
       UPDATE_DATA : A term that can update
       OPTION : An unflagged OptionInfo element
       ADD_OPTION : data to represent adding an option
       UPDATE_OPTION : data to represent updating an option
       OPTION_LIST : A list of options to add or update with
       SETTING : Info on a single setting
       SETTING_MAP : a settings map object in its full gliry
       SETTING_DICT : a nested dictionary with updates and assignments to
           various settings.
       ADD_SETTING_DICT : a dict where every member is an ADD_DATA object
           suitable for initializing new subtrees of settings.
       UPDATE_SETTING_DICT : a dict where at least some members are update or
           add objects, marking the tree as reasonable for use as a recursive
           update.
    """
    NONE = 0
    ACTION = auto()
    ADD_DATA = auto() | ACTION
    UPDATE_DATA = auto() | ACTION
    OPTION = auto()
    ADD_OPTION = auto() | OPTION | ADD_DATA
    UPDATE_OPTION = auto() | OPTION | UPDATE_DATA
    OPTION_LIST = auto() | ADD_DATA | UPDATE_DATA
    SETTING = auto()
    ADD_SETTING = auto() | SETTING | ADD_DATA
    UPDATE_SETTING = auto() | SETTING | UPDATE_DATA
    SETTING_MAP = auto()
    SETTING_DICT = auto()
    ADD_SETTING_DICT = auto() | SETTING_DICT | ADD_DATA
    UPDATE_SETTING_DICT = auto() | SETTING_DICT | UPDATE_DATA

    @staticmethod
    def type_of(data):

        if isinstance(data, Option):
            if isinstance(data, AddOption):
                return self.ADD_OPTION
            if isinstance(data, UpdateOption):
                return self.UPDATE_OPTION
            return self.OPTION

        if isinstance(data, Setting):
            if isinstance(data, AddSetting):
                return self.ADD_SETTING
            if isinstance(data, UpdateSetting):
                return self.UPDATE_SETTING
            return self.SETTING

        if isinstance(data, SettingsMap):
            return self.SETTING_MAP

        if isinstance(data, list):
            if all(map(lambda x: self.type_of(x) & self.OPTION, data)):
                return self.OPTION_LIST

        if isinstance(data, dict):
            if all(map(lambda x: isinstance(x,str), data.keys())):
                if all(map(lambda i: self.type_of(i) & self.ADD_DATA, data.values())):
                    return self.ADD_SETTING_DICT
                if any(map(lambda x: self.type_of(x) & self.ACTION, data.values())):
                    return self.UPDATE_SETTING_DICT
                return self.SETTING_DICT

        return self.NONE
