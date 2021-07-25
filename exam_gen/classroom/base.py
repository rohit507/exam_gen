import attr

from exam_gen.property.has_dir_path import HasDirPath
from exam_gen.util.with_options import WithOptions

import exam_gen.util.logging as logging

# TODO : Check if
from attr._make import (_CountingAttr)

log = logging.new(__name__, level="DEBUG")

@attr.s(init=False)
class Classroom(HasDirPath, WithOptions):

    roster = attr.ib(default=None, kw_only=True)
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

    # def __init__(self,


    def __init__(self, exam, **kwargs):

        key_attribs = ['roster', 'answers', 'scores', 'grades']

        new_kwargs = dict()

        for k in key_attribs:
            attr = getattr(type(self), k, None)
            if (k not in kwargs and attr != None
               and not isinstance(attr,_CountingAttr)):
                new_kwargs[k] = attr

        kwargs |= new_kwargs

        self.__attrs_init__(exam, **kwargs)


    def __attrs_post_init__(self):

        if hasattr(super(),'__attrs_post_init__'):
            super().__attrs_post_init__()

        self.roster = self.roster(parent_obj = self,
                                  exam = self.exam)

        if self.answers != None:
            self.answers = self.answers(parent_obj = self, exam = self.exam)
        if self.scores  != None:
            self.scores = self.scores( parent_obj = self, exam = self.exam)
        if self.grades  != None:
            self.grades = self.grades( parent_obj = self,exam = self.exam)

    def __getitem__(self, name):
        return self.students[item]

    def load_students(self):
        self.students |= self.roster.load_roster()

    def load_answers(self):

        assert self.students != None, (
            "Classroom must load students before loading answers.")

        answers = self.answers.load_answers(self.students)

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

    def print_grades(self, out_dir):
        self.grades.print_grades(self.students, out_dir)
