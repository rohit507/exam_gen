import attr

from pprint import *

from exam_gen.property.has_metadata import HasMetadata
from exam_gen.property.personalized import PersonalDoc
from exam_gen.property.has_user_setup import HasUserSetup
from exam_gen.property.has_settings import HasSettings
from exam_gen.property.has_context import HasContext
from exam_gen.property.has_rng import HasRNG
from exam_gen.property.numbered import Numbered
from exam_gen.property.templated import (
    Templated,
    add_template_var,
    TemplateSpec,
    template_spec_from_var)

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

__exam_formats__ = ['exam', 'solution']

@add_template_var('intro', __exam_formats__, doc=
                  """
                  The introduction and instruction text for the exam as a whole.
                  """)
@attr.s
class Exam(Numbered,
           PersonalDoc,
           HasMetadata,
           HasRNG,
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


    metadata.new_value("assignment", default="Example Assignment", doc=
        """
        The name of the assignment.

        !!! note ""
            Can be changed in `user_setup`.
        """
        )

    metadata.new_value("date", default="12-12-2012", doc=
        """
        The date of the exam.

        !!! note ""
            Can be changed in `user_setup`.
        """)


    metadata.new_value("course", default="TEST 101", doc=
        """
        The name of the course as it should appear in the corresponding template
        fields.

        !!! note ""
            Can be changed in `user_setup`.
        """)

    metadata.new_value("teacher", default=r'''J. Doe \& B. Smith''', doc=
        """
        The name(s) of the instructors

        !!! note ""
            Can be changed in `user_setup`.
        """)


    metadata.new_value("semester", default="Fall xx", doc=
        """
        The date of the exam.

        !!! note ""
            Can be changed in `user_setup`.
        """)


    settings.template.standalone = "exam.jn2"

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

        spec.subtemplates['intro'] = template_spec_from_var(
            self.intro,
            versions=[build_info.exam_format])

        return spec

    # [Raw string literal format](https://www.journaldev.com/23598/python-raw-string)
