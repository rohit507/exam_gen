import attr

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class Student():

    ident = attr.ib()

    name = attr.ib()
    username = attr.ib()
    root_seed = attr.ib(default=None)

    student_data = attr.ib(default=None)
    answer_data = attr.ib(default=None)
    score_data = attr.ib(default=None)
    grade_data = attr.ib(default=None)
