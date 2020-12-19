from enum import Flag, auto
from exam_gen.mixins.settings.errors import *
from exam_gen.util.dynamic_call import *
from exam_gen.mixins.settings.options_tuple import Options as NamedTuple
from typing import Optional, Any, Callable
from copy import *
from textwrap import *

class ValidationTime(Flag):
    """
    Options for when to validate a setting.
    """
    READ = auto()
    WRITE = auto()
    BOTH = READ | WRITE
    NEVER = 0

class Described(NamedTuple):

    short_desc: str = None
    long_desc : Optional[str] = None

    super_update = object.update if hasattr(object,'update') else None

    def update(self, other):
        if super_update != None : super_update(other)
        if other.short_desc != None: self.short_desc = other.short_desc
        if other.long_desc != None: self.long_desc = other.long_desc

class Defined(NamedTuple):
    """
    Just captures the historical information of the last entity to change
    this data.

    Params:
        definer (class or object): Which class initialization or object's
            evaluation this SettingOption was added under. (`required`)
    """
    definer : Any = None

    super_update = object.update if hasattr(object,'update') else None

    def update(self, other):
        if super_update != None : super_update(other)
        if other.definer == None:
            raise RuntimeError("Internal Error: Broken historical logging.")
        self.definer = other.definer

class Option(Defined, Described,  NamedTuple):
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

    super_update = object.update if hasattr(object,'update') else None

    def update(self, other, force_update = False):

        if self.name != other.name:
            raise RuntimeError("Internal Error: update of mismatched options.")

        if not (isinstance(other, UpdateOption) or force_update):
            raise RuntimeError("Internal Error: invalid option used to update.")

        if super_update != None : super_update(other)

    def add_option(self):
        return AddOption(**self._asdict())

    def update_option(self):
        return UpdateOption(**self._asdict())


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

class SettingInfo(Defined, Described,  NamedTuple):
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
    options: dict = dict()

    def add_option(self, option : Option, force_update = False):
        if not (isinstance(option, AddOption) or force_update):
            raise RuntimeError("InternalError: New option is invalid.")

        self.options[option.name] = Option(**option._asdict())

    def update_option(self, option : Option, force_update = False):
        if not (isinstance(option, UpdateOption) or force_update):
            raise RuntimeError("InternalError: Invalid option update.")

        self.options[option.name].update(option, force_update)

    def has_option(self, name : str):
        return name in options

    super_update = object.update if hasattr(object,'update') else None

    def update(self, other):
        """
        !!! Note
            Options from the parameter will supersede option from self.
        """

        if self.name != other.name:
            raise RuntimeError("Internal Error: update of mismatched settings.")

        if super_update != None : super_update(other)
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

    super_update = object.update if hasattr(object,'update') else None

    def update(self, other):
        """
        !!! Note
            If the setters are different, then the value of the parameter will
            overwrite the value of self.
        """
        if super_update != None : super_update(other)
        if self.setter != other.setter:
            self.setter = other.setter
            self.value = other.value



class SettingValidation(NamedTuple):
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

    super_update = object.update if hasattr(object,'update') else None

    def update(self, other):
        if self.setter != other.setter:
            self.needs_validation = True
        if super_update != None : super_update(other)
        if other.required != None: self.required = other.required
        if other.validator != None: self.validator = other.validator
        if other.validate_on != None: self.validate_on = other.validate_on

    def dirty(self): self.needs_validation = True

    def validate(self, parent, name = None):
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

class SettingConstruction(NamedTuple):
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

    super_update = object.update if hasattr(object,'update') else None

    def update(self, other):
        if super_update != None : super_update(other)
        if update.derive_with != None: self.derive_with = update.derive_with
        if update.update_with != None: self.update_with = update.update_with
        if update.copy_with != None: self.copy_with = update.copy_with
        if update.derive_on_read != None:
            self.derive_on_read = update.derive_on_read

    def copy(self):
        val = None
        if self.copy_with != None:
            val = self.copy_with(self.value)
        else:
            val = deepcopy(self.value)
        return self._replace(value = val,
                             options = deepcopy(options))

    def derive(self, parent, name = None):
        name = self.name if name == None else name
        if self.is_set:
            return None
        if self.derive_with != None:
            self.set(self.derive_with(parent.get_root), name, parent)
        else:
            raise SettingNotDerivableError(
                ("Cannot derive setting `{}.{}` since no method to do " +
                 "so was provided.").format(parent.path_string, name))

class Setting(SettingInfo,
              SettingValue,
              SettingValidation,
              SettingConstruction):
    """
    The complete collected information about a setting.
    """

    super_update = object.update if hasattr(object,'update') else None

    def update(self, other):
        if not isinstance(other, UpdateSetting):
            raise RuntimeError("Internal Error: Invalid Setting Update.")
        if super_update != None : super_update(other)

    def get(self, parent, name = None):

        name = self.name if name == None else name

        if not self.is_set and self.derive_on_read:
            self.derive(name, parent)

        if self.validate_on & ValidationTime.READ:
            self.validate(name, parent)

        if not self.is_set:
            raise UndefinedSettingError(
                ("Setting at `{}.{}` not defined at attempted use."
                ).format(parent.path_string, name))

        return self.value

    def set(self, value, parent, name = None):
        name = self.name if name == None else name
        self.setter = parent.context

        if self.update_with != None:
            self.value = self.update_with(self.value, value)
        else:
            self.value = value
        self.dirty()

        if self.validate_on & ValidationTime.WRITE:
            self.validate(name, parent)

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

def format_description(
        description : str = None,
        short_desc : str = None,
        long_desc : str = None):

    if long_desc:
        long_desc = dedent(long_desc).strip()

    if short_desc:
        short_desc = short_desc.strip()

    if description and (not short_desc) and (not long_desc):
        description = dedent(description)
        if (len(description) > 80) and (len(description.splitlines()) > 1):
            short_desc = shorten(fill(description).strip(), width = 80)
            long_desc = description
        else:
            short_desc = description
            long_desc = None
    elif long_desc and not short_desc:
            short_desc = shorten(fill(long_desc).strip(), width = 80)

    return (short_desc, long_desc)
