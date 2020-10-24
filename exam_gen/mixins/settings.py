"""
Some Docs
"""

class SettingsManager():
    """
    A class that inherits from this settings manager will given a `settings`
    attribute with various options and autogenerate documentation from the
    different parent options given.

    TODO :: How do you add new settings to a class?


    TODO :: How do you override settings defined in a parent class?
    TODO :: How do you override settings when creating a new object?
    TODO :: How do you read and write settings for an object at runtime?
    """

    def __init_subclass__(cls, **kwargs):
        """
        TODO ::

          - [ ] Get settings info from base classes
          - [ ] Merge to get the settings information for this class
          - [ ] Add new definitions for this class
          - [ ] Generate documentation for this class
        """
        super().__init_subclass__(cls, **kwargs)

    def __init__(self, **kwargs):
        """
        TODO ::
          - [ ] Init this particular object's settings property.
          - [ ] See if any of the available **kwargs are valid settings and
                update the options as needed.
          - [ ] Validate the options.

        Note: We're at the top of this class heirarchy so we shouldn't need
        to call `super().__init__` ourselves. But our subclasses absolutely
        have to. Otherwise we're not going to be able to get much done. 
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
