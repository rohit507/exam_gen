# import exam_gen.mixins.config.format as fmt
import exam_gen.mixins.config.superclass as cls


# val_table_name
# group_table_name
# combined_table_name
# recurse_entries
# combine_tables

SettingsManager = cls.new_config_superclass(
    class_name = "SettingsManager",
    var_name = "settings",
    val_table_name = "Available Settings",
    group_table_name = "Available Setting Groups",
    combined_table_name = "Available Settings",
    recurse_entries = True,
    combine_tables = True,
    docstring = """
    When you inherit from this superclass you get a `settings` variable that
    allows you to register new settings variables and subgroups. These terms
    are then properly documented in the docstring for `settings` even for
    classes that inherit from yours.
    """,
    var_docstring = """
    Various settings for use by this class. If any settings are available the
    docs will show them the tables below.
    """,
)

class Foo(SettingsManager):
    """Foo dostring"""

    settings.new_value("test", 12, "Test doc **please** *ignore*.")

    settings.new_group("subgroup", "this si a subgroup that we can use.")

    settings.subgroup.new_value("subtest", None, "Some stuff here")

    pass
