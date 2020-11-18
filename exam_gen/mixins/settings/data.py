from typing import *
from enum import Flag, auto

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
    description: str
    adding: bool = False

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
