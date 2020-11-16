from exam_gen.mixins.prepare_attrs import *

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
