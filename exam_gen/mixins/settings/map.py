from exam_gen.mixins.settings.errors import *
from exam_gen.mixins.settings.data import *
from inspect import isclass
from textwrap import *

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

    #kwargs = None
    context_stack = None
    context = None
    root_ref = None
    path = None
    members = None

    def __init__(self,
                 context,
                 root = None,
                 path = [],
                 description = None,
                 context_stack = [],
                 **kwargs
    ):
        # self.kwargs = kwargs
        super().__init__(**kwargs)

        if context == None:
            raise RuntimeError("There must be a current context in which this"+
                               " SettingsMap is initialized.")

        self.context_stack = context_stack
        self.context = context
        self.root_ref = root
        self.path = path
        self.members = dict()


    def __getattr__(self, name):
        if name in self.members:
           member = self.members[name]
           if isinstance(member, SettingInfo):
               return member.get(self, name)
           elif isinstance(member, SettingsMap):
               return member
           else:
               raise RuntimeError("Internal Error: Invalid SettingsMap " +
                                  "member type: {}".format(type(member)))
        else:
          raise AttributeError("Could not find setting '{}.{}'.".format(
              self.path_string, name))

    def __setattr__(self, name, value):

        value_type = SettingsType.type_of(value)
        print((value_type, SettingsType.OPTION_LIST))

        if hasattr(super(), name) or hasattr(self, name):
            super().__setattr__(name, value)
        elif value_type & SettingsType.OPTION:
            self.__set_option(name, value)
        elif value_type == SettingsType.OPTION_LIST:
            raise SomeError
        #     self.__set_option_list(name, value)
        elif value_type & SettingsType.SETTING:
            self.__set_setting(name, value)
        elif value_type & SettingsType.SETTING_DICT:
            self.__set_setting_dict(name, value)
        elif value_type & SettingsType.SETTING_MAP:
            raise SomeError
        #     self.__set_setting_map(name, value)
        elif name in self.members:
            self.__set_value(name, value)
        else:
            super().__setattr__(name, value)

    def __set_option(self, name, value, force_update = False):
        value_type = SettingsType.type_of(value)
        is_member = name in self.members
        member = self.members[name] if is_member else None
        member_type = SettingsType.type_of(member) if is_member else None

        if not (value_type & SettingsType.OPTION):
            raise SomeError
        elif not is_member:
            raise SomeError
        elif name != value.name:
            raise SomeError
        elif member_type != SettingsType.SETTING:
            raise SomeError
        elif (not member.has_option(name) and
             (value_type == SettingsType.ADD_OPTION or force_update)):
            member.add_option(value, force_update)
        elif (member.has_option(name) and
              (value_type == SettingsType.UPDATE_OPTION or force_update)):
            member.update_option(value, force_update)
        elif value_type == SettingsType.ADD_OPTION:
            raise SomeError
        elif value_type == SettingsType.UPDATE_OPTION:
            raise SomeError
        else:
            raise RuntimeError("Internal Error: Invalid set option call.")

    def __set_option_list(self, name, value):
        value_type = SettingsType.type_of(value)
        is_member = name in self.members
        member = self.members[name] if is_member else None
        member_type = SettingsType.type_of(member) if is_member else None

        if not is_member:
            raise SomeError
        elif member_type != SettingsType.SETTING:
            raise SomeError
        elif value_type == SettingsType.OPTION_LIST:
            for opt in value:
                self.__set_option(name, opt, force_update = True)
        else:
            raise SomeError

    def __set_setting(self, name, value, force_update = False):
        value_type = SettingsType.type_of(value)
        is_member = name in self.members
        member = self.members[name] if is_member else None
        member_type = SettingsType.type_of(member) if is_member else None

        if is_member and (member_type != SettingsType.SETTING):
            raise SomeError
        elif not (value_type & SettingsType.SETTING):
            raise SomeError
        elif (not is_member) and (
                (value_type == SettingsType.ADD_SETTING) or force_update):
            self.__new_setting(name, value)
        elif value_type == SettingsType.ADD_SETTING:
            raise SomeError
        elif is_member and (
                (value_type == SettingsType.UPDATE_SETTING) or force_update):
            member.update(value)
        elif value_type == SettingsType.UPDATE_SETTING:
            raise SomeError
        else:
            raise RuntimeError("Internal Error: Invalid set option call.")

        if member.needs_validation:
            self.root.dirty()

    def __set_setting_dict(self, name, value):
        value_type = SettingsType.type_of(value)
        is_member = name in self.members
        member_type = SettingsType.type_of(member) if is_member else None

        if member_type != SettingsType.SETTING_MAP:
            raise SomeError
        elif (not is_member) and (value_type == SettingsType.ADD_SETTING_DICT):
            self.__new_submap(name)
            self.members[name].__iadd__(value)
        elif is_member and (value_type & SettingsType.SETTING_DICT):
            self.members[name].__iadd__(value)
        else:
            raise SomeError


    def __set_setting_map(self, name, value):
        value_type = SettingsType.type_of(value)
        is_member = name in self.members
        member_type = SettingsType.type_of(member) if is_member else None

        if value_type != SettingsType.SETTING_MAP:
            raise SomeError
        elif not is_member:
            self.__new_submap(name)
        elif member_type != SettingsType.SETTING_MAP:
            raise SomeError

        self.members[name].update(value)


    def __new_setting(self, name, value):

        if name in self.members:
            raise SomeError

        if name != value.name:
            raise SomeError

        setting_dict = value._asdict()
        if setting_dict['definer'] != None:
            setting_dict['definer'] = self.context
        if setting_dict['value'] != None:
            setting_dict['setter'] = self.context
        if setting_dict['required'] == None:
            setting_dict['required'] = False
        if setting_dict['validate_on'] == None:
            setting_dict['validate_on'] = ValidationTime.NEVER
        setting_dict['needs_validation'] = True
        if setting_dict['derive_on_read'] == None:
            setting_dict['derive_on_read'] = False

        self.members[name] = Setting(setting_dict)

    def __new_submap(self, name):
        self.members[name] = SettingsMap(
            self.context,
            self.root,
            self.path + [name],
            self.context_stack)

    def __iadd__(self, other):
        if isinstance(other, dict):
            for (name, val) in other:
                self.__set_attr__(name, val)
        else:
            raise InvalidBulkAssignmentError("Expected a dict as input " +
                                             "to bulk setting assignment.")

    def update(self, other):
        # we go through all the members and for each
        for (name,new) in other.members.items():
            new_type = SettingsType.type_of(other)
            if new_type == SettingsType.SETTING:
                self.__set_setting(name, new, force_update = True)
            elif new_type == SettingsType.SETTING_MAP:
                self.__set_setting_map(name, new)
            else:
                raise SomeError



    def copy(self, context, root = None, path = []):
        new_map = SettingsMap(context,
                              root,
                              path,
                              self.description,
                              [self.context] + self.context_stack,
                              **self.kwargs)
        new_map.update(self)
        return new_map

    def dirty(self):
        for member in self.members.values():
            member.dirty()

    def validate(self, parent = None, name = None):
        for (name,member) in self.members.items():
            member.validate(self, name)

    def derive(self, parent = None, name = None):
        for (name, member) in self.members.items():
            member.derive(self, name)

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
    def is_root(self):
        return self.root_ref == None

    @property
    def root(self):
        return self if self.root_ref == None else self.root_ref

    def new_setting_func(self):

        def new_setting(
                description : str = None,
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
            """ Test do for internal new_setting func """

            (short_desc, long_desc) = format_description(description,
                                                         short_desc,
                                                         long_desc)

            info = AddSetting(
                setter = self.context if default != None else None,
                definer = self.context,
                value = default,
                short_desc = short_desc,
                long_desc = long_desc,
                needs_validation = default != None,
                required = required,
                validator = validator,
                validate_on = validate_on,
                derive_with = derivation,
                derive_on_read = derive_on_read,
                update_with = update_with,
                copy_with = copy_with,
                )

            if isinstance(options, dict):
                for (nm,dsc) in options.items():

                    (short_opt_desc, long_opt_desc) = format_description(dsc)

                    info.add_option(AddOption(
                        definer = self.context,
                        name = nm,
                        short_desc = short_opt_desc,
                        long_desc = long_opt_desc))
            elif isinstance(options, list):
                for opt in options:
                    if isinstance(opt, Option):
                        info.add_option(opt, force_update = True)
                    else:
                        raise SomeError
            else:
                raise SomeError

            return info

        return new_setting

    def update_setting_func(self):
        def update_setting(
                description : str = None,
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

            (short_desc, long_desc) = format_description(description,
                                                         short_desc,
                                                         long_desc)
            """ Test do for internal update_setting func """
            info = UpdateSetting(
                definer = self.context,
                setter = self.context if default != None else None,
                value = default,
                short_desc = short_desc,
                long_desc = long_desc,
                needs_validation = default != None,
                required = required,
                validator = validator,
                validate_on = validate_on,
                derive_with = derivation,
                derive_on_read = derive_on_read,
                update_with = update_with,
                copy_with = copy_with,
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
                    if isinstance(opt, Option):
                        info.add_option(opt, force_update = True)
                    else:
                        raise SomeError

            return info

        return update_setting

    def option_func(self):
        return self.add_option_func()

    def add_option_func(self):
        def add_option(name,
                   description = None,
                   short_desc = None,
                   long_desc = None):

            (short_desc, long_desc) = format_description(description,
                                                         short_desc,
                                                         long_desc)
            return AddOption(
                definer = self.context,
                name = name,
                short_desc = short_desc,
                long_desc = long_desc)

        return add_option

    def update_option_func(self):
        def update_option(name,
                   description = None,
                   short_desc = None,
                   long_desc = None):

            (short_desc, long_desc) = format_description(description,
                                                         short_desc,
                                                         long_desc)
            return UpdateOption(
                definer = self.context,
                name = name,
                short_desc = short_desc,
                long_desc = long_desc)

        return update_option

    def make_docstring(self, context):
        raise NotImplementedError

    def gather_docs(self, context):
        raise NotImplementedError



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
    _ADD_DATA_AUTO = auto()
    ADD_DATA = _ADD_DATA_AUTO | ACTION
    _UPDATE_DATA_AUTO = auto()
    UPDATE_DATA = _UPDATE_DATA_AUTO | ACTION
    OPTION = auto()
    _ADD_OPTION_AUTO = auto()
    ADD_OPTION = _ADD_OPTION_AUTO | OPTION | ADD_DATA
    _UPDATE_OPTION_AUTO = auto()
    UPDATE_OPTION = _UPDATE_OPTION_AUTO | OPTION | UPDATE_DATA
    _OPTION_LIST_AUTO = auto()
    OPTION_LIST = _OPTION_LIST_AUTO | ADD_DATA | UPDATE_DATA
    SETTING = auto()
    _ADD_SETTING_AUTO = auto()
    ADD_SETTING = _ADD_SETTING_AUTO | SETTING | ADD_DATA
    _UPDATE_SETTING_AUTO = auto()
    UPDATE_SETTING = _UPDATE_SETTING_AUTO | SETTING | UPDATE_DATA
    SETTING_MAP = auto()
    SETTING_DICT = auto()
    _ADD_SETTING_DICT_AUTO = auto()
    ADD_SETTING_DICT = _ADD_SETTING_DICT_AUTO | SETTING_DICT | ADD_DATA
    _UPDATE_SETTING_DICT_AUTO = auto()
    UPDATE_SETTING_DICT = _UPDATE_SETTING_DICT_AUTO | SETTING_DICT | UPDATE_DATA

    @classmethod
    def type_of(self, data):

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
