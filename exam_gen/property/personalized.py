import attr

from .document import *

from exam_gen.classroom.student import Student
import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class Personalized():
    """
    Classes that are initialized with information on a specific student.
    """

    student = attr.ib()
    """
    The student that this instance of the exam is for.
    """

    classroom = attr.ib()
    """
    The classroom object we're querying for information on a student.
    """

@attr.s
class PersonalDoc(Personalized,Document):
    """
    Will initialize all the different subdocs with the student_id and classroom
    information.

    This expects that all the questions under a parent are also personalized.
    """

    @classmethod
    def init_document(cls, doc_class):

        new_class = doc_class.with_options(
            student    = self.student,
            classroom  = self.classroom
        )

        return super().init_document(new_class)
