import attr
import exam_gen.util.logging as logging

from exam_gen.mixins.with_options import WithOptions
from exam_gen.mixins.path_manager import PathManager
from exam_gen.exam.metadata import ExamMetadata, ExamSettings
from exam_gen.student_inst import BuildableTemplate

log = logging.new(__name__, level="DEBUG")

@attr.s
class Question(BuildableTemplate, PathManager, WithOptions):
    """
    The top level question class that others will inherit from
    """

    metadata.new_value("question_name", default="Example Question", doc=
        """
        The name of the question.

        !!! note ""
            Can be changed in `user_setup`.
        """)

    metadata.new_value("author", default=r'''J. Doe \& B. Smith''', doc=
        """
        The author(s) of this question.

        !!! note ""
            Can be changed in `user_setup`.
        """)

    student_id = attr.ib()
    classroom = attr.ib()

    body = ""
    solution = ""

    pass




class MultipleChoiceQuestion(Question):

    settings.new_value("shuffle_answers", default=True, doc="")

    choices = list()

    pass

class Choices():
    # text
    # num
    # correct
    # solution text
    pass
