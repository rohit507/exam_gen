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

# I want classes to be able to define something like the below
# and produce an internal structure that allows this basic documented adt

# settings = {
#     'template': define_option(
#         default = None,
#         short_desc = "Template short desc",
#         long_desc = """
#         Here's some long form settings info 
#         """, 
#         validate = lambda opt, settings : True,
#         generate = lambda opt, settings : 14,
#         required = false. 
#         )
#     }

# Then using += and stru
