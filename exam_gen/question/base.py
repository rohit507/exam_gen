import attr

from pprint import *

from exam_gen.property.has_metadata import HasMetadata
from exam_gen.property.personalized import PersonalDoc
from exam_gen.property.has_user_setup import HasUserSetup
from exam_gen.property.has_settings import HasSettings
from exam_gen.property.has_context import HasContext
from exam_gen.property.has_rng import HasRNG
from exam_gen.property.answerable import Answerable
from exam_gen.property.gradeable import Gradeable
from exam_gen.property.numbered import Numbered
from exam_gen.property.templated import (
    Templated,
    add_template_var,
    TemplateSpec,
    template_spec_from_var)

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")


__exam_formats__ = ['exam', 'solution']

@add_template_var('body', __exam_formats__, doc=
                  """
                  The body text of the question
                  """)
@add_template_var('solution', __exam_formats__, doc=
                  """
                  The text of the solution
                  """)
@attr.s
class Question(Numbered,
               PersonalDoc,
               HasMetadata,
               HasRNG,
               HasContext,):
    """
    The top level question class that others will inherit from. Note that
    this can support multiple sub-components.
    """

    metadata.new_value(
        "name", default="Example Question",
        doc="""
        The name of the question as it will appear in the template
        """)

    metadata.new_value(
        "author", default='''J. Doe \& B. Smith''',
        doc="""
        The authors of this specific question.
        """)

    settings.template.embedded = "question_embed.jn2"

    def build_template_spec(self, build_info=None):

        spec = super().build_template_spec(build_info)

        spec.subtemplates['body'] = template_spec_from_var(
            self.body,
            versions=[build_info.exam_format])

        spec.subtemplates['solution'] = template_spec_from_var(
            self.solution,
            versions=[build_info.exam_format])

        return spec

    def user_setup(self, *vargs, **kwargs):
        pass
