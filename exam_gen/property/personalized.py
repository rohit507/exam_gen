import attr

from .document import *
from .templated import Templated

from exam_gen.classroom.student import Student

from exam_gen.util.merge_dict import merge_dicts
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
class PersonalDoc(Personalized, Templated, Document):
    """
    Will initialize all the different subdocs with the student_id and classroom
    information.

    This expects that all the questions under a parent are also personalized.
    """

    def init_document(self, doc_class, **kwargs):

        return super(PersonalDoc,self).init_document(
            doc_class,
            student    = self.student,
            classroom  = self.classroom,
            **kwargs
        )

    def build_template_spec(self, build_info=None):

        spec = super(PersonalDoc, self).build_template_spec(build_info)

        spec.context['student'] = merge_dicts(
            spec.context.get('student',dict()),
            self.student.student_data,
            attr.asdict(self.student))

        return spec
