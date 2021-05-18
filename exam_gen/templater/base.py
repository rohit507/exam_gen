import attr
from pathlib import *
import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class TemplateManager():

    template_path = attr.ib(factory=list, kw_only=True)

    def add_template_path(template_loc : Path):
        pass

    def apply_template_file(
            template : Path,
            context : dict,
            debug_prefix : str = None,
            debug_loc : Path = None,
            output_file : Path = None):
        pass

    def apply_template_string(
            template : str,
            context : dict,
            debug_prefix : str = None,
            debug_loc : Path = None,
            output_file : Path = None):
        pass

# helps lookup templates for use
# write intermediate/debug template data to file
# prints output template data to file
#
