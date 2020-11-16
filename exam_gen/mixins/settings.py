from exam_gen.mixins.prepare_attrs import *
from typing import *

class SettingsManager(metaclass=PrepareAttrs):
    """
    A class that inherits from this settings manager will given a `settings`
    attribute with various options and autogenerate documentation from the
    different parent options given.
    """

    def __init_subclass__(cls, **kwargs):
        """
        """
        super().__init_subclass__(cls, **kwargs)

    def __init__(self, **kwargs):
        """
        """
        pass

class SettingOption(NamedTuple):
    """
    A single valid option for a setting. Multiple options are added to
    a list that will be turned into a table.

    !!! Important
        This in an internal structure that should never be exposed to users
        of this module directly.

    Params:
       definer (class or object): Which class initialization or object's
           evaluation this SettingOption was added under.
       value (str): One option for a value this setting can take.
       description (str): The description of what setting the setting to
           that value would entail.
    """
    definer: Any
    value: str
    description: str
    pass

class SettingInfo(NamedTuple):
    """
    Named tuple that stores all the properties of a setting leaf node.

    !!! Important
        This in an internal structure that should never be exposed to users
        of this module directly.

    Attributes:
       definer (class or object): Which class initialization or object's
           evaluation this SettingOption was added under. (`required`)
       default (Any, optional): The default value for this setting.
           (`optional`)
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

       validate_on (str, optional): Determines when to run the validation
           function. (default = `'read'`)

           | Options | Description |
           | :-- | :-- |
           | `'read'`  | Validate the setting when it's read by something. |
           | `'write'` | Validate the setting when it's assigned a value.  |
           | `'both'`  | Validate the setting on both read and write.      |
           | `'never'` | Never validate the setting. |

           Defaults to `'read'` because there can be cases where a bunch of
           settings need to be assigned and the intermediate state can be
           invalid.

       needs_validation (bool): Does this setting need to be validated on the
            next read operation?  (default = `False`)

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

       options (list of SettingOption): A list of options for the setting that
            will be rendered as a table in the docs.


    """
    definer: Any
    default: Optional[Any] = None
    short_desc: Optional[str] = None
    long_desc: Optional[str] = None
    validator: Optional[Callable[..., bool]] = None
    validate_on: str = 'read'
    needs_validation: bool = False
    derivation: Optional[Callable[...,Any]] = None
    derive_on_read: bool = True
    required: bool = False
    update_with: Optional[Callable[...,Any]] = None
    copy_with: Optional[Callable[...,Any]] = None
    options: List[SettingOption] = []

    pass
