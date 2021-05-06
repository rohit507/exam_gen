import attr
import exam_gen.util.logging as logging
# from doit.task import dict_to_task
# from doit.cmd_base import TaskLoader2
# import doit.loader as doit
import os
import yaml
from exam_gen.builders.base import Builder

log = logging.new(__name__, level="DEBUG")

@attr.s
class LatexBuilder(Builder):
    """
    Provides a concrete implementation for `Builder` that can be used to make
    exams with latex.
    """

    pass
