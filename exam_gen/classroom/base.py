import attr
from pathlib import *
import inspect
import exam_gen.util.logging as logging
import exam_gen.classroom.roster_parser as roster
from exam_gen.mixins.path_manager import PathManager
from exam_gen.exam.metadata import ExamSettings, ExamMetadata
from exam_gen.mixins.with_options import WithOptions

log = logging.new(__name__, level="DEBUG")

@attr.s
class Classroom(ExamSettings, ExamMetadata, PathManager, WithOptions):

    roster  = attr.ib(default=None)
    "obj that defines to find and parse a roster"

    def parse_roster(self, builder):
        """
        Returns a dict from student-id to student metadata.

        if the new classroom is created in a subfolder relative to the exam
        this will use that
        """
        return self.roster.get_roster_data(builder,self.root_dir)

    answers = attr.ib(default=None)
    "defines where to find and how to parse student answers"

    grades = attr.ib(default=None)
    "defines how to parse grades"

    results = attr.ib(default=None)
    "defines how to print the results of grading an exam"
