from exam_gen.mixins.prepare_attrs import *

class SettingsManager(metaclass=PrepareAttrs):
    """
    A class that inherits from this settings manager will given a `settings`
    attribute with various options and autogenerate documentation from the
    different parent options given.
    """

    def __prepare_attrs__(cls, name, bases, env):
        # Call metadata for superclasses if needed
        if hasattr(super(),"__prepare_attrs__"):
            env = super().__prepare_attrs__(name,bases,env)

        # create / update context objects
        # - settings
        # - new_setting
        # - update_setting
        # - new_option
        # - update_option

        return env

    def __init_subclass__(cls, **kwargs):
        """
        """
        super().__init_subclass__(cls, **kwargs)

        # disable new/update setting/option functions.
        # generate docs for settings available from this class.

    def __init__(self, **kwargs):
        """
        """

        super().__init__(**kwargs)

        # Clone class settings tree to get object settings tree.

        pass
