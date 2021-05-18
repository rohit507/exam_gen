import attr
from copy import copy, deepcopy
import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

"""
wrap = setting <<value>>
     | mutual_ex { map name wrap } << name <wrap> >>
     | context { index , wrap } << map <index> <wrap> >>
     | optional { wrap } << maybe <wrap> >>
     | fields { map name wrap } << map name <wrap> >>
"""

@attr.s
class OptionSpecifier():

    mutual_ex = attr.ib()
    """
    mutually exclusive fields. With names and optionally a specific root
    """

    context_list = attr.ib()
    """
    sub_contexts that can be accessed in order with `[]`
    """

    optional_settings = attr.ib()
    """
    settings that can be ... set.
    """

    pass
