import attr

from exam_gen.property.has_metadata import HasMetadata
from exam_gen.property.personalized import Personalized
from exam_gen.property.has_user_setup import HasUserSetup
from exam_gen.property.has_context import HasContext
from exam_gen.property.templated import Templated, add_template_var, TemplateSpec

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

__exam_formats__ = ['exam', 'solution']

@add_template_var('intro', __exam_formats__, doc=
                  """
                  The introduction and instruction text for the exam as a whole.
                  """)
@attr.s
class Exam(HasMetadata,
           Templated,
           Personalized,
           HasContext):
    """
    Base class for all concrete exams, should be overridden when defining
    a new exam.
    """

    classes = attr.ib(factory=dict, init=False)
    """
    The dict of classes, with students and stuff, that we can perform operations
    over.

    !!! Important
        This must be set in the class definition, not at runtime or at init.
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

    metadata.new_value("semester", default="Fall xx", doc=
        """
        The date of the exam.

        !!! note ""
            Can be changed in `user_setup`.
        """)

    use_class_root = True
    """
    Ensure that we're using the class file location as root of the search path
    """

    def __attrs_post_init__(self):

        if hasattr(super(),'__attrs_post_init__'):
            super().__attrs_post_init__()

        for (name, class_init) in self.classes.items():
            self.classes[name] = class_init(exam=self)

    def build_template_spec(self, build_info=None):

        spec = super().build_template_spec(build_info)

        spec.context |= attr.asdict(self.student)

        spec.context |= self.metadata.value_dict

        spec.context |= self.final_context


        intro_template = self.intro.text
        intro_ctxt = self.intro.ctxt if self.intro.ctxt else dict()
        if self.intro.file != None:
            intro_template = Path(self.intro.file)

        spec.subtemplates['intro'] = TemplateSpec(intro_template,
                                                  context=intro_ctxt)

        for (name, question) in self.questions.items():
            spec.subtemplates[name] = question.template_spec(
                build_info=build_info)

        return spec

    # [Raw string literal format](https://www.journaldev.com/23598/python-raw-string)




    # use_class_root = attr.ib(default=True, init=False)

    # def init_root_seed(self):
    #     """
    #     Get a root seed based on the student data's root seed parameter
    #     """
    #     return self.classroom.get_data(self.student_id)['root_seed']

    # def start_build(self, data_dir, build_dir, **build_settings):
    #     """
    #     Pre-question part of the build process. Generally runs the user init
    #     sets up questions, etc...
    #     """

    #     (sup_out, sub_log) = super().start_build_files(
    #         outputs, data_dir, build_dir, **build_settings)

    #     log_data = dict()
    #     outputs = dict()
    #     return (outputs, log_data)

    # def subdoc_build_files(self):
    #     pass

    # def finish_build_filed(self):
    #     pass



    # def user_setup(self):
    #     """
    #     Test Docs
    #     """
    #     return dict()
