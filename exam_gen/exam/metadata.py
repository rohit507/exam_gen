import exam_gen.util.logging as logging
from exam_gen.mixins.config import *

from exam_gen.builders import Builder
from exam_gen.templater import TemplateManager

log = logging.new(__name__, level="DEBUG")

class ExamMetadata(MetadataManager):
    """
    This class initializes exam specific metadata fields in a way that can be
    inherited by other classes.

    `exam_gen.exam.Exam`, `exam_gen.classroom.Classroom`, and
    `exam_gen.question.Question` are the intended inheritors and the metadata
    should apply in the relevant context.
    """


    pass


class ExamSettings(SettingsManager):
    """
    This class initializes exam specific settings in a way that can be
    inherited by other classes.

    `exam_gen.exam.Exam`, `exam_gen.classroom.Classroom`, and
    `exam_gen.question.Question` are the intended inheritors and the settings
    should apply in the relevant context.
    """

    settings.new_value('builder', default=Builder, doc=
      """
      An `exam_gen.builders.Builder` or subclass, possibly
      with some initialization options preset using
      `with_options`.

      This specifies where build outputs should go, the commands
      used for constructing the exam files, the default locations
      for templates, and similar things.
      """)

    settings.new_value('template_manager', default=TemplateManager, doc=
      """
      An `exam_gen.templater.TemplateManager` or subclass
      """)
    pass
