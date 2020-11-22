from typing import *
from enum import Flag, auto
from wrapt import ObjectProxy
from exam_gen.mixins.settings.errors import *
from exam_gen.util.dynamic_call import *
from copy import *

class SettingOption(NamedTuple):
    """
    A single valid option for a setting. Multiple options are added to
    a list that will be turned into a table. Used both as internal store

    !!! Important
        This in an internal structure that should never be exposed to users
        of this module directly.

    !!! Todo
        Make this an internal class of `SettingsMap`.

    Params:
       definer (class or object): Which class initialization or object's
           evaluation this SettingOption was added under.
       description (str): The description of what setting the setting to
           that value would entail.
       adding (bool): Are we using this as an `add_option` object?
    """
    definer: Any
    name: str
    description: str


class ValidationTime(Flag):
    """
    Options for when to validate a setting.
    """
    READ = auto()
    WRITE = auto()
    BOTH = READ | WRITE
    NEVER = 0


class SettingInfo(NamedTuple):
    """
    Named tuple that stores all the properties of a setting leaf node. Also
    can serve as a partial

    !!! Important
        This in an internal structure that should never be exposed to users
        of this module directly.

    !!! Todo
        Make this an internal class of `SettingsMap`.

    Attributes:
       definer (class or object): Which class initialization or object's
           evaluation this SettingOption was added under. (`required`)
       setter (class or object): Which class init or object evaluation set
           this value. (`optional`)
       value (Any): The actual value that was set. (`optional`)
       short_desc (str, optional): A short (< 80 char) description of the
           setting. (`optional`)
       long_desc (str, optional): A longer description of a setting and what
           it does. (`optional`)
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

       derivation (function): Function to derive the value of the setting
            from other settings. The function should accept the root settings
            object as an input. (`optional`)

       derive_on_read (bool): Should this setting be derived when the setting
            is read and no value has been specified? If `True` the first read
            will run the derivation function and set the value of the setting.
            (`optional`)

            Note: A default will take precedence over this setting. Also,
            this is the only way a derivation will be automatically run.

       required (bool): Does this setting need to be assigned directly?
            (default = `false`)

            Note: This is checked whenever a term is validated, either when
            validation is explicitly run or when the `validate_on` value would
            specify.

       update_with (function): Two parameter function used to combine the
            new value for a setting with the old whenever it's set. (`optional`)

       copy_with (function): Function used to make a deep clone of the value
            of a setting when we need to copy a settings object.

       options (dict): A dict of options for the setting that
            will be rendered as a table in the docs. The key of the dict is
            the name of the option

       updating (bool): Are we using this as an `update_setting` object?
       creating (bool): Are we using this as a `new_setting` object?


    """
    definer: Any
    setter: Any = None
    value: Any = None
    short_desc: Optional[str] = None
    long_desc: Optional[str] = None
    validator: Optional[Callable[..., bool]] = None
    validate_on: ValidationTime = ValidationTime.NEVER
    needs_validation: bool = False
    derivation: Optional[Callable[...,Any]] = None
    derive_on_read: bool = True
    required: bool = False
    update_with: Optional[Callable[...,Any]] = None
    copy_with: Optional[Callable[...,Any]] = None
    options: dict = dict()
    updating: bool = False
    creating: bool = False

    def add_option(self, name, option):
        self.options[option.name] = option

    def update(self, update):
        self.definer = update.definer
        if update.setter != None: self.setter = update.setter
        if update.value != None:
            self.value = update.value
            self.needs_validation |= update.needs_validation
        if update.short_desc != None: self.short_desc = update.short_desc
        if update.long_desc != None: self.long_desc = update.long_desc
        if update.validator != None: self.validator = update.validator
        if update.validate_on != None: self.validate_on = update.validate_on
        if update.derivation != None: self.derivation = update.derivation
        if update.derive_on_read != None:
            self.derive_on_read = update.derive_on_read
        if update.required != None: self.required = update.required
        if update.update_with != None: self.update_with = update.update_with
        if update.copy_with != None: self.copy_with = update.copy_with
        if update.options != None:
            self.options.update(update.options)

    def copy(self):
        val = None
        if self.copy_with != None:
            val = self.copy_with(self.value)
        else:
            val = deepcopy(self.value)
        return self._replace(value = val,
                             options = deepcopy(options))

    def is_set(self):
        return self.setter != None

    def get_val(self, name, parent):
        if not self.is_set() and self.derive_on_read:
            self.derive(name, parent)
        if self.validate_on & ValidationTime.READ:
            self.validate(name, parent)
        if not self.is_set():
            raise UndefinedSettingError(
                ("Setting at `{}.{}` not defined at attempted use."
                ).format(parent.path_string, name))
        else:
            return self.value

    def set_val(self, value, name, parent):
        self.setter = parent.context
        if self.update_with != None:
            self.value = self.update_with(self.value, value)
        else:
            self.value = value
        self.dirty()
        if self.validate_on & ValidationTime.WRITE:
            self.validate(name, parent)
        pass

    def dirty(self):
        self.needs_validation = True

    def derive(self, name, parent):
        if not self.is_set():
            if self.derivation != None:
                self.set_val(self.derivation(parent.get_root), name, parent)
            else:
                raise SettingNotDerivableError(
                    ("Cannot derive setting `{}.{}`"
                    ).format(parent.path_string, name))
        else:
            pass

    def validate(self, name, parent):
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

                if isinstance(result, bool) and (not result):
                    raise InvalidSettingError(
                        ("Validation of setting `{}.{}` failed."
                        ).format(parent.path_string, name))
                elif isinstance(result, str):
                    raise InvalidSettingError(
                        ("Validation of setting `{}.{}` failed with error: {}"
                        ).format(parent.path_string, name, result))

            self.needs_validation = False
        else:
            pass
