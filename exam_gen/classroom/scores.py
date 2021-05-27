import attr

from pathlib import *

from .student import Student

from exam_gen.property.has_dir_path import HasDirPath
from exam_gen.util.with_options import WithOptions

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class Scores(HasDirPath, WithOptions):

    exam = attr.ib()

    def load_scores(self):
        pass

    def read_scores(self):
        raise NotImplementedError("")

    def format_scores(self):
        pass
