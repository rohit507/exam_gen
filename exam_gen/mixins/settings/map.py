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
                 description = None,
                 context_stack = [],
                 **kwargs
    ):
        super().__init__(**kwargs)

        if context == None:
            raise RuntimeError("There must be a current context in which this"+
                               " SettingsMap is initialized.")

        self.context_stack = [context] + context_stack
        self.context = context
        self.root = self if root == None else root
        self.docs_dirty = True
        self.docs = None
        self.description = description
        self.members = dict()


    def __getattr__(self, name):
        # If there's a member
           # If it's a setting
              # if it's set
                 # if it needs to be validated, validate and return it
              # if it's not set and is derivable on read
                 # derive it, set it, and return it
              # else
                 # raise UndefinedSettingError
           # if it's a settingsMap
              # return it
        # else
           # raise NoSuchSettingError
        raise NotImplementedError

    def __setattr__(self, name, value):
        # if value is a new settings object
          # if setting exists
             # raise SettingAlreadyExistsError
          # if setting is settingMap
             # raise SettingsMapNotUpdatableError
          # else create a new setting & mark revalidation & regen docs
        # if value is an update settings object
          # if setting doesn't exist
            # raise NoSettingToUpdateError
          # else update the setting & mark all for revalidation & regen docs
        # if value is an add_option object
          # if setting exists
            # add the option & regen docs
          # else
            # raise NoSuchSettingError or SettingsMapNotUpdatableError
        # if value is a dict
          # if setting is a settings map
            # `+=` the value and the setting together
        # else
          # if setting exists
            # set the value & mark for revalidation & regen docs & and etc
          # if not
            # raise NoSuchSettingError
        raise NotImplementedError

    def __iadd__(self, other): # Note: this is `+=`
        # if other is a dict
          # go through and add each item to this object via __setattr__
        # else
          # raise InvalidBulkAssignment
        raise NotImplementedError

    def copy(self, context, root = None):
        # Make a clone of this object that we can use elsewhere that has a
        # a new defined context

        # create a new SettingsMap with appropriate additional context
        # go through each term in our map and add it, with the appropriate
        # modifications to the new settings map. Use the `copy_with` functions
        # of the various values as needed.
        raise NotImplementedError

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
        # mark all the validation flags dirty
        raise NotImplementedError

    def dirty_validation(self, name):
        raise NotImplementedError

    def validate_all(self):
        # go through all elements and
          # if settingsmap, run validate_all
          # else validate the specific value
        raise NotImplementedError

    def validate(self, name):
        # validate a single item
        # if its required and does not exist
          # raise UndefinedRequiredSettingError
        # if it needs validation
          # if validation fails
            # raise InvalidSettingError
          # else
            # mark validation clean
        raise NotImplementedError

    def derive_all(self):
        # go through all items and derive them
        raise NotImplementedError

    def derive(self, name):
        # for a single item
        # if its derivable
          # do that, set the value
        # if it's not
          # raise SettingNotDerivableError
        raise NotImplementedError

    def set_context(self, context):
        self.context_stack = [context] + self.context_stack
        self.context = context

    def make_docstring(self, context):
        raise NotImplementedError

    def gather_docs(self, context):
        raise NotImplementedError
