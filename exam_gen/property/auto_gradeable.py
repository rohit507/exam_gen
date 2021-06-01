import attr

from .gradeable import Gradeable
from .answerable import Answerable
from .has_settings import HasSettings

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class AutoGradeable(Gradeable, Answerable):

    def set_answer(self, answer):
        super(AutoGradeable, self).set_answer(answer)

    def set_points(self, points, comment=None):
        raise RuntimeError("Don't assign a points score directly for an "
                           "auto-gradable question, it will be calculated "
                           "when an answer is provided.")

    def __calc_grade_harness__(self):
        """
        Wraps the `calculate_grade` function for a child class.

        It should:
          - Short-circuit around `calculate_grade` if need be
          - Set up the appropriate parameters for calculating the grade
          - Take the result of the calc_grade function and properly
            assign it to `self._points`, `self._comment` and the like

        It will be run immidiately after an answer is written to `self._answer`.
        """
        raise NotImplementedError("Class needs a new `__calc_grade_harness__`")

    def calculate_grade(self, answer):
        raise NotImplementedError((
            "Overload the `calculate_grade` function in any autogradable "
            "class"))
