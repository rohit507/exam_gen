import textwrap
from pprint import *

from exam_gen.util.config import config_superclass

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@config_superclass(
    var_name = "settings",
    val_table_name = "Available Settings",
    group_table_name = "Available Setting Groups",
    combined_table_name = "Available Settings",
    recurse_entries = True,
    combine_tables = True,
    var_docstring = textwrap.dedent(
        """
        Assorted settings that are used by this class and can be set during
        class initialization or runtime.
        """
    )
)
class HasSettings():
    """
    When you inherit from this superclass you get a `settings` variable that
    allows you to register new settings variables and subgroups. These terms
    are then properly documented in the docstring for `settings` even for
    classes that inherit from yours.
    """
    pass
