# import exam_gen.mixins.config.format as fmt
import textwrap
from pprint import *

import exam_gen.mixins.config.superclass as cls
import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

def var_docstring(var_name, desc):
    return textwrap.dedent(desc)

@cls.config_superclass(
    var_name = "settings",
    val_table_name = "Available Settings",
    group_table_name = "Available Setting Groups",
    combined_table_name = "Available Settings",
    recurse_entries = True,
    combine_tables = True,
    var_docstring = var_docstring(
        var_name = "settings",
        desc =
        """
        Assorted settings that are used by this class and can be set during
        class initialization or runtime.
        """
    )
)
class SettingsManager():
    """
    When you inherit from this superclass you get a `settings` variable that
    allows you to register new settings variables and subgroups. These terms
    are then properly documented in the docstring for `settings` even for
    classes that inherit from yours.
    """
    pass

@cls.config_superclass(
    var_name = "metadata",
    val_table_name = "Metadata Fields",
    group_table_name = "Metadata Subgroups",
    combined_table_name = "Metadata Fields",
    recurse_entries = True,
    combine_tables = True,
    var_docstring = var_docstring(
        var_name = "metadata",
        desc =
        """
        Metadata used as part of rendering or annotating output.
        """
    )
)

class MetadataManager():
    """
    When you inherit from this superclass you get a `metadata` variable that
    allows you to register new metadata fields.
    """
    pass


# class TestConfigUser(SettingsManager, MetadataManager):
#     """
#     This class exists to help test the generated configuration superclasses.
#     It's not really meant to be used anywhere and shouldn't be exported.
#     """

#     settings.new_value("test", 12, "Test doc **please** *ignore*.")

#     settings.new_group("subgroup", "this si a subgroup that we can use.")

#     settings.subgroup.new_value("subtest", None, "Some stuff here")

#     pass
