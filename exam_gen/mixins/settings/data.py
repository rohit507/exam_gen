from typing import *
from enum import Flag, auto
from wrapt import ObjectProxy
from exam_gen.mixins.settings.errors import *
from exam_gen.util.dynamic_call import *
from copy import *

class ValidationTime(Flag):
    """
    Options for when to validate a setting.
    """
    READ = auto()
    WRITE = auto()
    BOTH = READ | WRITE
    NEVER = 0

class Defined(NamedTuped):
    """
    Just captures the historical information of the last entity to change
    this data.

    Params:
        definer (class or object): Which class initialization or object's
            evaluation this SettingOption was added under. (`required`)
    """
    definer : Any = None

    def update(self, other):
        if hasattr(super(), 'update'): super().update(other)
        if other.definer == None:
            raise RuntimeError("Internal Error: Broken historical logging.")
        self.definer = other.definer

class Option(Defined, NamedTuple):
    """
    Basic metadata for an option.

    Params:
)       name (str): the name of the option.
       short_desc (str, optional): A short (< 80 char) description of the
           option. (`optional`)
       long_desc (str, optional): A longer description of an option and what
           it does.

           !!! Note
               Keep in mind that longer descriptions have to be rendered in a
               more verbose format for `mkdocs` to work correctly.
               This *will* allow for relatively advanced markup and structure
               in the output docs, but at cost of raw readability.

               Tools like `pydoc` will end up spitting a bunch of unreadable
               raw HTML into their output. It's not a great look. Still it
               might be worth the cost if you have a good fixed documentation
               model that can handle the complexity.

           (`optional`)

    """
    name      : str = None
    short_desc: str = None
    long_desc : Optional[str] = None

    def update(self, other):

        if self.name != other.name:
            raise RuntimeError("Internal Error: update of mismatched options.")

        if not isinstance(other, UpdateOption):
            raise RuntimeError("Internal Error: invalid option used to update.")

        if hasattr(super(), 'update'): super().update(other)
        if other.short_desc != None: self.short_desc = other.short_desc
        if other.long_desc != None: self.long_desc = other.long_desc



class AddOption(Option):
    """
    Wrapper signifying that we're adding an option that shouldn't already
    exist.
    """
    pass

class UpdateOption(Option):
    """
    Wrapper signifying that we're updating an option that should exist.
    """
    pass

class SettingInfo(Defined, NamedTuple):
    """
    Basic metadata for a setting.

    Params:
       name (str): the name of the option.
       short_desc (str, optional): A short (< 80 char) description of the
           option. (`optional`)
       long_desc (str, optional): A longer description of an option and what
           it does. (`optional`)
       options (dict): A dict of options for the setting that
            will be rendered as a table in the docs. The key of the dict is
            the name of the option
    """
    name: str = None
    short_desc: str = None
    long_desc: Optional[str] = None
    options: dict = dict()

    def add_option(self, option):
        if not isinstance(option, AddOption):
            raise RuntimeError("InternalError: New option is invalid.")

        self.options[option.name] = Option(**option._addict())

    def update_option(self, option):
        if not isinstance(option, UpdateOption):
            raise RuntimeError("InternalError: Invalid option update.")

        self.options[option.name].update(option)

    def update(self, other):
        """
        !!! Note
            Options from the parameter will supersede option from self.
        """

        if self.name != other.name:
            raise RuntimeError("Internal Error: update of mismatched settings.")

        if hasattr(super(), 'update'): super().update(other)
        if other.short_desc != None: self.short_desc = other.short_desc
        if other.long_desc != None: self.long_desc = other.long_desc
        for (name, opt) in other.options.items():
            if name not in self.options:
                self.add_option(AddOption(**opt._asdict()))
            else:
                self.update_option(UpdateOption(**opt._asdit()))


class SettingValue(NamedTuple):
    """
    The core value of the setting (if any) and the context in which it was
    last set.

    Params:
       setter (class or object): Which class init or object evaluation set
           this value. (`optional`)
       value (Any): The actual value that was set. (`optional`)
    """
    setter: Any = None
    value: Any = None

    @property
    def is_set(self):
        return self.setter != None

    def update(self, other):
        """
        !!! Note
            If the setters are different, then the value of the parameter will
            overwrite the value of self.
        """
        if hasattr(super(), 'update'): super().update(other)
        if self.setter != other.setter:
            self.setter = other.setter
            self.value = other.value



class SettingValidation(SettingValue, NamedTuple):
    """
    Data on how and whether to validate the correctness of the setting.

    Params:

       required (bool): Does this setting need to be assigned directly?
            (default = `false`)

            Note: This is checked whenever a term is validated, either when
            validation is explicitly run or when the `validate_on` value would
            specify.

       validator (function, optional): A function of that will validate this setting, returns
           `True` if valid and `False` or an error string otherwise.
           (`optional`)

           | Options | Description |
           | :-- | :-- |
           | `lambda val: ...` | A single parameter will be passed the value of the setting. Should return a `bool`. |
           | `lambda val settings: ...` | A second parameter will be passed the root settings object as well, so that the consistency of multiple settings can be tested. |

       validate_on (ValidationTime): Determines when to run the validation
           function. (default = `NEVER`)

           | Options | Description |
           | :-- | :-- |
           | `ValidationTime.READ`  | Validate the setting when it's read by something. |
           | `ValidationTime.WRITE` | Validate the setting when it's assigned a value.  |
           | `ValidationTime.BOTH`  | Validate the setting on both read and write.      |
           | `ValidationTime.NEVER` | Never validate the setting. |

           Defaults to `'read'` because there can be cases where a bunch of
           settings need to be assigned and the intermediate state can be
           invalid.

       needs_validation (bool): Does this setting need to be validated on the
            next read operation?  This is mainly for internal bookkeeping use
            (default = `False`)
    """
    required: bool = None
    validator: Optional[Callable[..., bool]] = None
    validate_on: ValidationTime = None
    needs_validation: bool = False

    def update(self, other):
        if self.setter != other.setter:
            self.needs_validation = True
        if hasattr(super(), 'update'): super().update(other)
        if other.required != None: self.required = other.required
        if other.validator != None: self.validator = other.validator
        if other.validate_on != None: self.validate_on = other.validate_on

    def dirty_val(self): self.needs_validation = True

    def validate_val(self, parent, name = None):
        name = self.name if name == None else name
        if self.needs_validation:

            if self.required and not self.is_set():
                raise UndefinedRequiredSettingError(
                    ("Setting `{}.{}` is required but not set."
                    ).format(parent.path_string, name))

            if self.validator != None:

                validation_args = {
                    'val': self.value,
                    'settings': parent.get_root
                    }
                validation_order = ['val', 'settings']
                validation_func = dcall(self.validator, order=validation_order)
                result = validation_func(validation_args)


                if isinstance(result, str):
                    raise InvalidSettingError(
                        ("Validation of setting `{}.{}` failed with error: {}"
                        ).format(parent.path_string, name, result))

                if (result != True) or (result != None):
                    raise InvalidSettingError(
                        ("Validation of setting `{}.{}` failed."
                        ).format(parent.path_string, name))

            self.needs_validation = False

class SettingConstruction(SettingValue, NamedTuple):
    """
    Functions to allow the construction and modification of setting values.

    Params:

       derive_with (function): Function to derive the value of the setting
            from other settings. The function should accept the root settings
            object as an input. (`optional`)

       update_with (function): Two parameter function used to combine the
            new value for a setting with the old whenever it's set. (`optional`)

       copy_with (function): Function used to make a deep clone of the value
            of a setting when we need to copy a settings object.

       derive_on_read (bool): Should this setting be derived when the setting
            is read and no value has been specified? If `True` the first read
            will run the derivation function and set the value of the setting.
            (`optional`)

            Note: A default will take precedence over this setting. Also,
            this is the only way a derivation will be automatically run.
    """
    derive_with: Optional[Callable[...,Any]] = None
    update_with: Optional[Callable[...,Any]] = None
    copy_with: Optional[Callable[...,Any]] = None
    derive_on_read: bool = None

    def update(self, other):
        if hasattr(super(), 'update'): super().update(other)
        if update.derive_with != None: self.derive_with = update.derive_with
        if update.update_with != None: self.update_with = update.update_with
        if update.copy_with != None: self.copy_with = update.copy_with
        if update.derive_on_read != None:
            self.derive_on_read = update.derive_on_read

    def copy_val(self):
        val = None
        if self.copy_with != None:
            val = self.copy_with(self.value)
        else:
            val = deepcopy(self.value)
        return self._replace(value = val,
                             options = deepcopy(options))

    def derive_val(self, parent, name = None):
        name = self.name if name == None else name
        if self.is_set:
            return None
        if self.derive_with != None:
            self.set_val(self.derive_with(parent.get_root), name, parent)
        else:
            raise SettingNotDerivableError(
                ("Cannot derive setting `{}.{}` since no method to do " +
                 "so was provided.").format(parent.path_string, name))

class Setting(SettingInfo,
              SettingValidation,
              SettingConstruction,
              SettingValue):
    """
    The complete collected information about a setting.
    """

    def update(self, other):
        if not isinstance(other, UpdateSetting):
            raise RuntimeError("Internal Error: Invalid Setting Update.")
        if hasattr(super(), 'update'): super().update(other)

    def get_val(self, parent, name = None):

        name = self.name if name == None else name

        if not self.is_set and self.derive_on_read:
            self.derive_val(name, parent)

        if self.validate_on & ValidationTime.READ:
            self.validate_val(name, parent)

        if not self.is_set:
            raise UndefinedSettingError(
                ("Setting at `{}.{}` not defined at attempted use."
                ).format(parent.path_string, name))

        return self.value

    def set_val(self, value, parent, name = None):
        name = self.name if name == None else name
        self.setter = parent.context

        if self.update_with != None:
            self.value = self.update_with(self.value, value)
        else:
            self.value = value
        self.dirty()

        if self.validate_on & ValidationTime.WRITE:
            self.validate_val(name, parent)

class AddSetting(Setting):
    """
    Wrapper to indicate we're adding a new setting that should not exist.
    """
    pass

class UpdateSetting(Setting):
    """
    Wrapper to indicate we're updating a setting that should already exist.
    """
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
