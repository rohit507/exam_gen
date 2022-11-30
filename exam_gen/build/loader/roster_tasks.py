import attr

from copy import *

from exam_gen.build.data import BuildInfo
from exam_gen.util.file_ops import *

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

__all__ = ['get_roster_data']

def get_roster_data(class_name, build_info, load_answers=False, load_scores=False):

    cd_path = build_info.class_data_path()

    classroom = build_info.classroom

    classroom.load_students()

    dump_obj(classroom, path=(cd_path,build_info.base_roster_file))

    if load_answers and classroom.answers != None:
        classroom.load_answers()
        dump_obj(classroom, path=(cd_path, build_info.answered_roster_file))

    if load_scores and classroom.scores != None:
        classroom.load_scores()
        dump_obj(classroom, path=(cd_path, build_info.scored_roster_file))

    for (student_id, student) in classroom.students.items():

        new_build_info = build_info.where(student_id = student_id,
                                          student = student)

        sd_path = new_build_info.student_data_path()

        dump_obj(student, path=(sd_path, new_build_info.student_data_file))

    return classroom
