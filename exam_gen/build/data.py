import attr

from pathlib import *
from copy import *

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class BuildInfo():
    """
    Information about the build process

    !!! todo "Todo: Write up attribute information"
    """


    # Info about current build
    student_id = attr.ib(default=None, kw_only=True)
    student = attr.ib(default=None, kw_only=True)

    class_name = attr.ib(default=None, kw_only=True)
    classroom = attr.ib(default=None, kw_only=True)

    is_standalone = attr.ib(default=False, kw_only=True)
    exam_format = attr.ib(default=None, kw_only=True)
    settings = attr.ib(factory=dict, kw_only=True)

    # paths for the *current* build task, not constants to build paths.
    data_path = attr.ib(default=None, kw_only=True)
    build_path = attr.ib(default=None, kw_only=True)
    out_path = attr.ib(default=None, kw_only=True)

    # constants defining build environments and file_names
    data_dir = attr.ib(default='~data', kw_only=True)
    build_dir = attr.ib(default='~build', kw_only=True)
    out_dir = attr.ib(default='~out', kw_only=True)

    class_prefix = attr.ib(default='class-', kw_only=True)
    student_prefix = attr.ib(default='student-', kw_only=True)
    exam_prefix = attr.ib(default='exam-', kw_only=True)
    question_prefix = attr.ib(default='question-', kw_only=True)

    base_roster_file = attr.ib(default='roster.yaml', kw_only=True)
    answered_roster_file = attr.ib(default='answered-roster.yaml', kw_only=True)
    scored_roster_file = attr.ib(default='scored-roster.yaml', kw_only=True)
    graded_roster_file = attr.ib(default='graded-roster.yaml', kw_only=True)

    pre_prefix = attr.ib(default='pre-', kw_only=True)
    post_prefix = attr.ib(default='post-', kw_only=True)

    init_prefix = attr.ib(default='init-', kw_only=True)
    setup_prefix = attr.ib(default='setup-', kw_only=True)
    finalize_prefix = attr.ib(default='finalize-', kw_only=True)
    template_prefix = attr.ib(default='template-', kw_only=True)
    output_prefix = attr.ib(default='output-', kw_only=True)

    doc_file = attr.ib(default='doc.yaml', kw_only=True)
    log_file = attr.ib(default='log.yaml', kw_only=True)
    spec_file = attr.ib(default='spec.yaml', kw_only=True)
    result_file = attr.ib(default='result.yaml', kw_only=True)

    student_data_file = attr.ib(default='data.yaml', kw_only=True)
    grade_data_file = attr.ib(default='grade-data.yaml', kw_only=True)

    root_dir = attr.ib(default = None, init=False)

    build_settings = attr.ib(factory=dict, kw_only = True)

    def base_data_path(self):
        return Path(self.root_dir, self.data_dir)

    def class_data_path(self):
        return Path(self.base_data_path(),
                    self.class_prefix + self.class_name)

    def student_data_path(self):
        return Path(self.class_data_path(),
                    self.student_prefix + self.student_id)

    def exam_data_path(self):
        return Path(self.student_data_path(),
                    self.exam_prefix + self.exam_format)

    def question_data_path(self):
        return Path(self.student_data_path(self.class_name, self.student_id),
                    self.question_prefix + self.question_format)

    def base_build_path(self):
        return Path(self.root_dir, self.build_dir)

    def class_build_path(self):
        return Path(self.base_build_path(),
                    self.class_prefix + self.class_name)

    def student_build_path(self):
        return Path(self.class_build_path(),
                    self.student_prefix + self.student_id)

    def exam_build_path(self):
        return Path(self.student_build_path(),
                    self.exam_prefix + self.exam_format)

    def question_build_path(self):
        return Path(self.student_build_path(),
                    self.question_prefix + self.question_format)

    def base_out_path(self):
        return Path(self.root_dir, self.out_dir)

    def class_out_path(self):
        return Path(self.base_out_path(),
                    self.class_prefix + self.class_name)

    def exam_out_path(self):
        return Path(self.base_out_path(),
                    self.exam_prefix + self.exam_format,
                    self.class_prefix + self.class_name)

    def question_out_path(self):
        return Path(self.base_out_path(),
                    self.question_prefix + self.question_format,
                    self.class_prefix + self.class_name)

    def where(self, **kwargs):
        """
        Create a new copy of this object with some attributes changed.

        Parameters are identical to the parameters of `BuildInfo.__init__`.
        """

        new = deepcopy(self)
        for (k,v) in kwargs.items():
            setattr(new, k, v)

        return new
