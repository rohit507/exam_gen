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


    # def parse_roster(self, builder):
    #     """
    #     Returns a dict from student-id to student metadata.

    #     if the new classroom is created in a subfolder relative to the exam
    #     this will use that
    #     """
    #     return self.roster.get_roster_data(builder,self.root_dir)


    # suppress the following fields to minimize chance for error
    parent_obj = attr.ib(default=None, init=False)
    parent_path = attr.ib(default=None, init=False)

    builder = attr.ib()
    """
    The builder that an instance of classroom uses to determine local directory
    structure and the like.
    """

    roster  = attr.ib(default=None)
    "obj that defines to find and parse a roster"

    roster_cache = attr.ib(default=None, init=False)
    """
    Cached roster data
    """

    def roster_data(self):
        if self.roster_cache == None:
            self.roster_cache = self.roster.get_roster_data(self.builder,
                                                            self.root_dir)

        return self.roster_cache

    def students(self):
        return self.roster_data().keys()

    def get_data(self, student_id):
        if student_id in self.roster_data():
            return (self.roster_data())[student_id]
        else:
            return None

    answers = attr.ib(default=None)
    "defines where to find and how to parse student answers"


    answer_cache = attr.ib(default=None, init=False)
    """
    Cached information on student answers
    """

    def answer_data(self):

        if answers == None:
            return dict()

        if self.answer_cache == None:
            self.answer_cache = self.answers.get_answer_data(self.builder,
                                                             self.root_dir)

        return self.answer_cache

    def get_answers(self, student_id):
        """
        Get info on the answers that a single student provided
        """

        if student_id in self.answer_data():
            return (self.answer_data())[student_id]
        else:
            return None

    grades = attr.ib(default=None)
    "defines how to parse grades"

    grade_cache = attr.ib(default=None, init=False)
    """
    Cached information on student grades
    """

    def grade_data(self):

        if grades == None:
            return dict()

        if self.grade_cache == None:
            self.grade_cache = self.grades.get_grade_data(self.builder,
                                                             self.root_dir)

        return self.grade_cache

    def get_grades(self, student_id):
        """
        Get info on the (non-autogenerated) grades for a single student
        """
        if student_id in self.grade_data():
            return (self.grade_data())[student_id]
        else:
            return None

    results = attr.ib(default=None)
    "defines how to print the results of grading an exam"


    def __attrs_post_init__(self):

        self.parent_obj = self.builder

        if hasattr(super(),'__attrs_post_init__'):
            super().__attrs_post_init__()
