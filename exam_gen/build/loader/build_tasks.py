import attr
import os

from pprint import *
from pathlib import *

from .roster_tasks import *
from exam_gen.build.data import BuildInfo
from exam_gen.property.answerable import distribute_answers
from exam_gen.property.gradeable import distribute_scores
from exam_gen.property.templated import build_template_spec
from exam_gen.util.file_ops import *

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")


def init_exam(exam_cls, build_info):
    """
    Assumes classroom is initialized and contains student_id
    """

    classroom = build_info.classroom
    student = classroom.students[build_info.student_id]
    exam_obj = exam_cls(student=student,
                      classroom=classroom,
                      parent_path=build_info.root_dir)

    dump_obj(exam_obj, path=(build_info.data_path,
                            build_info.pre_prefix +
                            build_info.init_prefix +
                            build_info.doc_file))

    exam_obj.init_questions()

    dump_obj(exam_obj, path=(build_info.data_path,
                            build_info.post_prefix +
                            build_info.init_prefix +
                            build_info.doc_file))

    return exam_obj

def setup_exam(exam_obj, build_info):
    dump_obj(exam_obj, path=(build_info.data_path,
                            build_info.pre_prefix +
                            build_info.setup_prefix +
                            build_info.doc_file))


    pwd = os.getcwd()

    os.chdir(build_info.build_path)

    setup_log = exam_obj.setup_build(build_info)

    setup_log['children'] = exam_obj.on_children(
        lambda n: n.setup_build(build_info))

    os.chdir(pwd)

    dump_yaml(setup_log, path=(build_info.data_path,
                               build_info.setup_prefix +
                               build_info.log_file))

    dump_obj(exam_obj, path=(build_info.data_path,
                            build_info.post_prefix +
                            build_info.setup_prefix +
                            build_info.doc_file))

def template_exam(exam_obj, build_info):

    dump_obj(exam_obj, path=(build_info.data_path,
                            build_info.pre_prefix +
                            build_info.template_prefix +
                            build_info.doc_file))


    pwd = os.getcwd()

    os.chdir(build_info.build_path)


    file_name = Path(exam_obj.settings.template.output +
                     "." +
                     exam_obj.settings.template.format_ext)

    template_spec = exam_obj.template_spec(file_name, build_info)

    dump_yaml(template_spec, path=(build_info.data_path,
                               build_info.template_prefix +
                               build_info.spec_file))

    result = build_template_spec(
        exam_obj.settings.template.output,
        template_spec,
        out_file = file_name,
        debug_dir = build_info.data_path)

    dump_yaml(template_spec, path=(build_info.data_path,
                               build_info.template_prefix +
                               build_info.result_file))

    os.chdir(pwd)

    dump_obj(exam_obj, path=(build_info.data_path,
                            build_info.post_prefix +
                            build_info.template_prefix +
                            build_info.doc_file))
    pass

def finalize_exam(exam_obj, build_info):

    dump_obj(exam_obj, path=(build_info.data_path,
                            build_info.pre_prefix +
                            build_info.finalize_prefix +
                            build_info.doc_file))


    pwd = os.getcwd()

    os.chdir(build_info.build_path)

    finalize_log = exam_obj.finalize_build(build_info)

    os.chdir(pwd)

    dump_obj(finalize_log, path=(build_info.data_path,
                               build_info.finalize_prefix +
                               build_info.log_file))

    dump_obj(exam_obj, path=(build_info.data_path,
                            build_info.post_prefix +
                            build_info.finalize_prefix +
                            build_info.doc_file))


def output_exam(exam_obj, build_info):

    out_log = exam_obj.output_build(build_info,
                                    output_file=build_info.student_id)

    dump_obj(out_log, path=(build_info.data_path,
                               build_info.output_prefix +
                               build_info.log_file))

def build_exam(exam_cls, class_name, student_id,  build_info, setup_only = False):

    build_info = build_info.where(
        data_path = build_info.exam_data_path(),
        build_path = build_info.exam_build_path(),
        out_path = build_info.exam_out_path(),
        is_standalone = True)

    os.makedirs(build_info.data_path, exist_ok = True)
    os.makedirs(build_info.build_path, exist_ok = True)
    os.makedirs(build_info.out_path, exist_ok = True)

    exam_obj = init_exam(exam_cls, build_info)

    if build_info.classroom.answers != None:
        if exam_obj.student.answer_data != None:
            distribute_answers(exam_obj, exam_obj.student.answer_data)

    if build_info.classroom.scores != None:
        if exam_obj.student.score_data != None:
            distribute_scores(exam_obj, exam_obj.student.score_data)

    setup_exam(exam_obj, build_info)

    if not setup_only:

        template_exam(exam_obj, build_info)

        finalize_exam(exam_obj, build_info)

        output_exam(exam_obj, build_info)

    return exam_obj
