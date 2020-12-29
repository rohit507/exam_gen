import exam_gen.util.logging as logging
import textwrap
import types
import attr
from pprint import *
from copy import *
from exam_gen.util.attrs_wrapper import attrs
import exam_gen.mixins.config as config

log = logging.new(__name__, level='DEBUG')

@attrs()
class BaseTemplate(config.SettingsManager, config.MetadataManager):
    """
    Classes inheriting from this can produce output strings from a set of
    environment variables and a template. This exists as a separate class
    from `jinja2.Template` so that we can wrap it with a few more checks and
    better errors.
    """

    settings.set_docstring("""
    Assorted settings that are available when this class is defined, it's run,
    and to any classes that inherit from it.
    """)

    settings.new_group(
        name='template',
        doc="""
        Settings that determine what template to use in a given situation,
        how to instantiate it, and how to interpret it.
        """)

    settings.template.new_value(
        name='environment',
        default=None,
        doc="""
        This is a `jinja2.Environment` that determines the search path used to
        find templates, what sort of syntax the templates use, the type of
        string escaping to use, and a whole bunch of other details.

        !!! Todo
            Pick a sensible default value, or replace with a subgroup of
            specific options.
        """)

    metadata.set_docstring("""
    Metadata about the document like author names, information about how the
    document is used, etc..

    The various values and subgroups shown below will generally be available
    to any template that's being rendered by this class.
    """)

    def render(self):
        """
        !!! Todo
            Function should produce an output string based on current settings
            and input data.
        """
        pass
