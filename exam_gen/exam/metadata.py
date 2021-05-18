import exam_gen.util.logging as logging
from exam_gen.mixins.config import *

from exam_gen.builders.base import Builder

log = logging.new(__name__, level="DEBUG")

class ExamMetadata(MetadataManager):
    """
    This class initializes exam specific metadata fields in a way that can be
    inherited by other classes.

    `exam_gen.exam.Exam`, `exam_gen.classroom.Classroom`, and
    `exam_gen.question.Question` are the intended inheritors and the metadata
    should apply in the relevant context.
    """

    metadata.new_value("exam_name", default="Example Assignment", doc=
        """
        The name of the exam.

        !!! note ""
            Can be changed in `user_setup`.
        """
        )

    metadata.new_value("class_name", default="TEST 101", doc=
        """
        The name of the class as it should appear in the corresponding template
        fields.

        !!! note ""
            Can be changed in `user_setup`.
        """)

    metadata.new_value("instructor", default=r'''J. Doe \& B. Smith''', doc=
        """
        The name(s) of the instructors

        !!! note ""
            Can be changed in `user_setup`.
        """)

    metadata.new_value("date", default="12-12-2012", doc=
        """
        The date of the exam.

        !!! note ""
            Can be changed in `user_setup`.
        """)

    metadata.new_group("intro", doc=
        """
        The introduction text for the exam. If more than one sub-option is
        set (i.e. has a value other than `None`) will prefer to use
        `template_file` first, then `template_text`.
        """)

    metadata.intro.new_value("raw_text", default=None, doc=
        """
        Raw, untemplated, text to be used as the introduction for an exam or
        assignment. [Raw string literal format](https://www.journaldev.com/23598/python-raw-string)
        is recommended when setting this metadata field.

        !!! note ""
            Can be changed in `user_setup`.
        """)

    metadata.intro.new_value("template_text", default=None, doc=
        """
        Templated text, which will have variables and other holes filled
        automatically, that can be used as an introduction for an exam or
        assignment. [Raw string literal format](https://www.journaldev.com/23598/python-raw-string)
        is recommended when setting this metadata field.

        !!! note ""
            Can be changed in `user_setup`.
        """)

    metadata.intro.new_value("template_file", default=None, doc=
        """
        A file in one of the exam's template directories that is to be used
        for the introduction text in an exam or assignment.

        !!! note ""
            Can be changed in `user_setup`.
        """)


    # class_name
    # teachers
    # semester
    # data


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

    # settings.new_value('template_manager', default=TemplateManager, doc=
    #   """
    #   An `exam_gen.templater.TemplateManager` or subclass. Potentially with
    #   some initialization options preset with `with_options`.
    #   """)

    settings.new_value('template_dir', default=None, doc=
      """
      The directory where templates are to be located. Can be either a single
      path string like `"templates"` (without trailing path seperators) or a
      list of path strings.

      These paths are relative to the file in which they are defined.
      For example specifying `settings.template_dir = "templates"` in
      `question1/TimerQuestion.py` will make the system look for templates in
      the `question1/templates/` directory.

      Any directories specified will be **added** to the search path for
      templates. Directories specified in a `Classroom` will be searched
      before those for a `Question` and template directories specified in
      an `Exam` will be looked at last.
      """)
