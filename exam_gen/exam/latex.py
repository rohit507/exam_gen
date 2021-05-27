import attr

from .base import Exam

from exam_gen.property.format.latex import LatexDoc

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class LatexExam(LatexDoc, Exam):
    pass
