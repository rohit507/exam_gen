import attr

import exam_gen.util.logging as logging
from copy import *
import textwrap
import functools

from exam_gen.student_inst import *
from exam_gen.mixins.user_setup import *
from exam_gen.mixins.random_gen import *
from random import Random

log = logging.new(__name__, level="DEBUG")

@attr.s
class UserSetupDoc(BuildableDoc, UserSetup):

    def start_build_files(
            self,
            outputs,
            data_dir,
            build_dir,
            build_settings):

        (out, log) = super().start_build_files(
            outputs, data_dir, build_dir, build_settings)

        log['user_setup'] = self._run_user_setup()
        return (out, log)

@attr.s
class ContextDoc(UserSetupDoc):

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
        log = super().__pre_user_setup__()
        log['context'] = deepcopy(self.parent_context)
        return log

    def __post_user_setup__(self, setup_vars):
        log = super().__post_user_setup__(setup_vars)
        if setup_vars == None:
            self.result_context = dict()
        else:
            self.result_context = deepcopy(setup_vars)
        self.final_context = self.parent_context | self.result_context
        log['context'] = deepcopy(self.final_context)
        return log

    @setup_arg
    def ctxt(self) -> dict:
        """
        A dictionary of values returned by the `user_setup` functions of
        any parent documents.
        """
        return deepcopy(self.parent_context)

    def subdoc_build_files(
            self,
            set_name,
            doc_name,
            doc_obj,
            outputs,
            data_dir,
            build_dir,
            build_settings):
        """
        Copy the context from our own user setup to each sub-document before
        their build operations are run.
        """

        if isinstance(doc_obj, ContextDoc):
            doc_obj.parent_context = deepcopy(self.final_context)

        return super(set_name,
                     doc_name,
                     doc_obj,
                     outputs,
                     data_dir,
                     build_dir,
                     build_settings)

@attr.s
class RNGSourceDoc(UserSetupDoc):

    root_seed = attr.ib(default = None, kw_only=True)
    """
    The seed that the different RNGs for this document will derive from
    """

    rng_source = attr.ib(default = None, init=False)
    """
    The rng source object that we're going to be using
    """

    def init_root_seed(self):
        raise RuntimeError("No method to get root seed")

    def get_keyed_rng(self, *keys):

        if self.root_seed == None:
            self.root_seed = self.init_root_seed()

        return Random(create_seed(self.root_seed,*keys))


    @setup_arg
    def rng(self) -> Random:
        """
        A repeatable random number generator that will always produce the same
        sequence of outputs for any given student, exam pair.
        """
        return self.get_keyed_rng('user_setup')

    def subdoc_build_files(
            self,
            set_name,
            doc_name,
            doc_obj,
            outputs,
            data_dir,
            build_dir,
            build_settings):
        """
        Set the random seeds of each sub document
        """

        if isinstance(doc_obj, RNGSourceDoc):
            doc_obj.root_seed = create_seed(self.root_seed, set_name, doc_name)

        return super(set_name, doc_name, doc_obj, outputs,
                     data_dir, build_dir, build_settings)

@attr.s
class TemplateDoc(BuildableDoc):
    """
    Associates and propagates a template environment and searchpath
    """

    template_env = attr.ib(default = None, init = False)
    """
    The Jinja2 template environment this document uses
    """

    template_path = attr.ib(default = None, kw_only = True)
    """
    Lower priority template lookup from parents
    """

    template_lookup = attr.ib(default = None, init = False)
    """
    Class specific template lookup object
    """

    def instance_template_path(self):
        """
        Get the template path for this instance
        """
        pass

    def apply_file_template(self):
        pass

    def apply_string_template(self):
        pass


    pass
