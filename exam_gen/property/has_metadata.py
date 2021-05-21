import textwrap
from pprint import *

from exam_gen.util.config import config_superclass

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@config_superclass(
    var_name = "metadata",
    val_table_name = "Metadata Fields",
    group_table_name = "Metadata Subgroups",
    combined_table_name = "Metadata Fields",
    recurse_entries = True,
    combine_tables = True,
    var_docstring = textwrap.dedent(
        """
        Metadata used as part of rendering or annotating output.
        """
    )
)

class HasMetadata():
    """
    When you inherit from this superclass you get a `metadata` variable that
    allows you to register new metadata fields.
    """
    pass
