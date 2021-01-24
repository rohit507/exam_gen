import textwrap
import types
from copy import *
from pprint import *

import attr

import exam_gen.mixins.config as config
import exam_gen.util.logging as logging

import jinja2

log = logging.new(__name__, level='DEBUG')

@attr.s
class TemplateSettings(config.SettingsManager, config.MetadataManager):
    """
    This class is what assorted parent classes should inherit when they'll use
    a template to render text into a nicer format.

    This allows for more convenient settings propagation and general setup.
    """
    pass

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


@attr.s
class BaseTemplate():
    """
    This is a wrapper around jinja2.Template that gives us better error
    messages and other stuff in the potential future.
    """

    def render(self):
        """
        !!! Todo
            Function should produce an output string based on current settings
            and input data.
        """
        pass
