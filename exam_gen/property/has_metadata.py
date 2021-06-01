import textwrap

from pprint import *

from .templated import TemplateSpec, Templated

from exam_gen.util.merge_dict import merge_dicts
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
class MetadataVariable():
    """
    When you inherit from this superclass you get a `metadata` variable that
    allows you to register new metadata fields.
    """
    pass

class HasMetadata(MetadataVariable, Templated):

    def build_template_spec(self, build_info=None):

        spec = super(HasMetadata, self).build_template_spec(build_info)

        spec.context = merge_dicts(spec.context, self.metadata.value_dict)

        return spec
