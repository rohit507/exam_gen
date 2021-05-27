import attr

from pathlib import *

from .student import Student

from exam_gen.util.with_options import WithOptions

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class Grades(WithOptions):

    exam = attr.ib()

    def print_grades(self, student_dict, out_dir):
        raise NotImplementedError("")
