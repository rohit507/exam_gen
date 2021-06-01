import attr

from copy import *
from pprint import *

from .document import Document
from .has_user_setup import HasUserSetup
from .templated import TemplateSpec, Templated

from exam_gen.util.merge_dict import merge_dicts
from exam_gen.util.user_setup import setup_arg

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class HasContext(HasUserSetup, Templated, Document):

    parent_context = attr.ib(factory=dict, kw_only=True)
    """
    The variable context (possibly from a parent doc) that can be set in
    user_setup and is passed to both templates and sub-docs
    """

    result_context = attr.ib(default=None, init=False)
    """
    context returned after user_set up
    """

    final_context = attr.ib(default=None, init=False)
    """
    The context after parent and result are merged
    """

    def __pre_user_setup__(self):
        log = super(HasContext, self).__pre_user_setup__()
        log['context'] = deepcopy(self.parent_context)
        return log

    def __post_user_setup__(self, setup_vars):
        log_ = super(HasContext, self).__post_user_setup__(setup_vars)
        if setup_vars == None:
            self.result_context = dict()
        else:
            self.result_context = deepcopy(setup_vars)
        self.final_context = self.parent_context | self.result_context


        log_['context'] = deepcopy(self.final_context)
        return log_

    @setup_arg
    def ctxt(self) -> dict:
        """
        A dictionary of values returned by the `user_setup` functions of
        any parent documents.
        """
        return deepcopy(self.parent_context)

    def setup_build(self, build_info):

        log = super(HasContext, self).setup_build(build_info)

        for (name, memb) in self.questions.items():
            memb.parent_context = deepcopy(self.final_context)

        log['context'] = self.final_context
        return log

    def build_template_spec(self, build_info=None):

        spec = super().build_template_spec(build_info)

        # log.warning(pformat((type(self), self.final_context)))

        spec.context = merge_dicts(spec.context, self.final_context)

        return spec
