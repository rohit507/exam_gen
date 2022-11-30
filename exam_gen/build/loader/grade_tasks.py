import attr

from copy import *

from exam_gen.build.data import BuildInfo
from exam_gen.util.file_ops import *
from .roster_tasks import *
from .build_tasks import *
from exam_gen.property.gradeable import collect_grades

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

def calculate_grades(class_name, build_info):

    classroom = get_roster_data(
        class_name,
        build_info,
        load_scores = True,
        load_answers = True
    )

    for (student_id, student) in classroom.students.items():


        print("Grading Student: {}".format(student_id))

        student_bld = build_info.where(
            student_id = student_id,
            student = student
        )

        exam_obj = build_exam(
            classroom.exam,
            class_name,
            student_id,
            student_bld,
            setup_only = True
        )

        grade_data = collect_grades(exam_obj)

        sd_path = student_bld.student_data_path()

        dump_obj(grade_data, path=(sd_path, student_bld.grade_data_file))

        classroom.assign_grades(student_id, grade_data)

    classroom.print_grades(build_info.class_out_path())

    return classroom
