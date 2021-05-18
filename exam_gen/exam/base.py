import attr

import exam_gen.util.logging as logging
from exam_gen.builders import *
from exam_gen.mixins.config import *
from exam_gen.mixins.path_manager import PathManager
from exam_gen.exam.metadata import *
from exam_gen.mixins.user_setup import *
from exam_gen.student_inst import BuildableDoc, PersonalDoc
from exam_gen.doc_mixins import *
from exam_gen.templater.context_var import template_var

log = logging.new(__name__, level="DEBUG")



@template_var('intro')
@attr.s
class Exam(ExamSettings, ExamMetadata, PersonalDoc, ContextDoc, RNGSourceDoc):
    """
    Base class for all concrete exams, should be overridden
    """

    classes = attr.ib(factory=dict, init=False)
    """
    The dict of classes, with students and stuff, that we can perform operations
    over.

    !!! Important
        This must be set in the class definition, not at runtime or at init.
    """

    questions = attr.ib(factory=dict, init=False)
    """
    The dict of questions that are to be included in the exam

    !!! Important
        This must be set in the class definition, not at runtime or at init.
    """

    # hide from the user.
    use_class_root = attr.ib(default=True, init=False)

    def init_root_seed(self):
        """
        Get a root seed based on the student data's root seed parameter
        """
        return self.classroom.get_data(self.student_id)['root_seed']

    def start_build_files(self,
                          outputs,
                          data_dir,
                          build_dir,
                          build_settings):
        """
        Pre-question part of the build process. Generally runs the user init
        sets up questions, etc...
        """

        (sup_out, sub_log) = super().start_build_files(outputs,
                                                       data_dir,
                                                       build_dir,
                                                       build_settings)

        # Propagate RNG to questions
        # Run user setup, push vars to question

        log_data = dict()
        outputs = dict()
        return (outputs, log_data)

    def user_setup(self):
        """
        Test Docs
        """
        return dict()
