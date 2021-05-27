import attr

from exam_gen.property.has_dir_path import HasDirPath
from exam_gen.util.with_options import WithOptions

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class Classroom(HasDirPath, WithOptions):

    roster = attr.ib()
    """
    Rosters are mandatory entries that let us retrieve a list of students,
    relevant metadata and the like.
    """

    answers = attr.ib(default=None, kw_only=True)
    """
    Answers are optional entries that let us import answers students have
    given to each question.
    """

    scores  = attr.ib(default=None, kw_only=True)
    """
    Score are optional entries that let us import manually scored or annotated
    results for each question.
    """

    grades  = attr.ib(default=None, kw_only=True)
    """
    Grades are optional entries that describe how to output and tweak grade
    information for each student.
    """

    exam = attr.ib()
    """
    The exam object this classroom is attached to.
    """

    students = attr.ib(factory=dict)
    """
    Cache where we store the generated student data.
    """

    def __attrs_post_init__(self):

        if hasattr(super(),'__attrs_post_init__'):
            super().__attrs_post_init__()

        self.roster = self.roster(parent_obj = self,
                                  exam = self.exam)

        if self.answers != None: self.answers(parent_obj = self,
                                              exam = self.exam)
        if self.scores  != None: self.scores( parent_obj = self,
                                              exam = self.exam)
        if self.grades  != None: self.grades( parent_obj = self,
                                              exam = self.exam)

    def __getitem__(self, name):
        return self.students[item]

    def load_students(self):
        self.students |= self.roster.load_roster()

    def load_answers(self):
        answers = self.answers.load_answers()

        for (ident, answer) in answers.items():
            if self.students[ident].answer_data == None:
                self.students[ident].answer_data = answer
            else:
                self.students[ident].answer_data.merge(answer)

    def load_scores(self):
        scores = self.scored.load_scores()

        for (ident, score) in scores.items():
            if self.students[ident].score_data == None:
                self.students[ident].score_data = score
            else:
                self.students[ident].score_data.merge(score)

    def assign_grades(self, ident, grade_data):
        self.students[ident].grade_data = grade_data

    def print_grades(self, out_file):
        self.grades.print_grades(self.students, out_file)
