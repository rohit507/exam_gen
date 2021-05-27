import attr

from .document import Document
from .has_settings import HasSettings

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class GradeData():
    points = attr.ib(default=None)
    children = attr.ib(factory=dict)
    comment = attr.ib(default=None, kw_only = True)

    ungraded_points = attr.ib(default=None, init=False)
    weighted_points = attr.ib(default=None, init=False)
    total_weight = attr.ib(default=None, init=False)

    @property
    def percent_grade(self):
        return (self.weighted_points / self.total_weight)

    @property
    def percent_ungraded(self):
        return (self.ungraded_points / self.total_weight)

    @staticmethod
    def normalise(data):
        if isinstance(data, GradeData):
            return data
        elif isinstance(data, dict):
            return GradeData(children=data)
        else:
            return GradeData(grade=data)


    def merge(self, other):

        other = GradeData.normalize(other)

        if other.grade != None:
            self.grade = other.grade
            self.format = other.format

        for (name, child) in other.children.items():
            if name in self.children:
                self.children[name] = GradeData.normalise(
                    self.children[name]).merge(child)
            else:
                self.children[name] = GradeData.normalize(child)


@attr.s
class Gradeable(HasSettings, Document):

    _weight = attr.ib(default=None, kw_only=True)
    _points = attr.ib(default=None, init=False)
    _comment = attr.ib(default=None, init=False)

    settings.new_group(
        "grade", doc=
        """
        Settings covering how grades are managed for this problem.
        """)

    settings.grade.new_value(
        "max_points", default=1, doc=
        """
        The maximum number of points that can be assigned to problem
        """)

    settings.grade.new_value(
        "weight", default=None, doc=
        """
        The weight of this problem relative to others in exam. If none, this
        is assumed to be the same as `settings.grade.max_points`.
        """)

    def __attrs_post_init__(self):
        if hasattr(super(), '__attrs_post_init__'):
            super().__attrs_post_init__()

        # stupid way of sneaking an init parameter into the settings
        if self._weight != None:
            self.settings.grade.weight = self._weight

        # need this for a semi-responsive default setting
        if self.settings.grade.weight == None:
            self.settings.grade.weight = self.settings.grade.max_points

    def set_points(self, points, comment=None):

        if len(self.questions) > 0:
            raise RuntimeError("Cannot assign grade to doc with sub-questions")

        if points != None:
            self._points = points

        if self._points > self.settings.grade.max_points:
            raise RuntimeError("Assigned grade larger than max_points allowed")

        if comment != None:
            self._comment = comment

    @property
    def ungraded(self):
        return self._points == None

    @property
    def percent_grade(self):
        """
        returns a grade from between 0 and 1
        """
        return (self._points / self.settings.grade.max_points)

    @property
    def weighted_grade(self):
        """
        returns a grade after weighting
        """
        return (self.settings.grade.weight * self.percent_grade)

    @property
    def total_weight(self):
        return self.settings.grade.weight

def distribute_scores(obj , grades):
    """
    Takes a document and splits out all the grade information in an
    `GradeData` to it's children.
    """

    # Check if valid
    if not isinstance(obj, Document):
        raise RuntimeError("Can't distribute grades to non-document")

    # for convinience allow the user to supply grades or points directly
    grades = GradeData.normalize(grades)

    # Copy out basic grades
    if isinstance(obj, Gradeable):
        obj.set_points(grades.points, comment=grade.comment)
    elif grades.points != None:
        raise RuntimeError("Trying to set grade on non-gradeable doc.")

    # apply to children
    for (name, sub_q) in obj.questions.items():
        if name in grades.children:
            distribute_grades(sub_q, grades.children[name])

    # get extra keys and throw error if any
    extra = [k for k in grades.children.keys() if k not in obj.questions]
    if len(extra) != 0:
        raise RuntimeError(
            "Tried to supply grades for non-existent children : ".format(
                extra
            ))

def collect_grades(obj):
    """
    Goes through a document and gathers the grade info from all the
    sub-elements, keeping track of grade and weight
    """

    grade_data = GradeData()

    # check if valid
    if not isinstance(obj, Document):
        raise RuntimeError("Can't gather grades from non-document")

    if isinstance(obj, Gradeable):
        grade_data.points = obj._points
        grade_data.comment = obj._comment

    # Either sum up the information from the sub-questions
    if len(obj.questions) != 0:
        grade_data.ungraded_points = 0
        grade_data.weighted_points = 0
        grade_data.total_weight = 0

        for (name, sub_q) in obj.questions.items():
            sub_data = collect_grades(sub_q)
            grade_data.children[name] = sub_data

            grade_data.total_weight += sub_data.total_weight
            grade_data.ungraded_points += sub_data.ungraded_points
            grade_data.weighted_points += sub_data.weighted_points

    # or just use the leaf question's data
    else:
        grade_data.total_weight = obj.total_weight
        if obj.ungraded:
            grade_data.weighted_points = 0
            grade_data.ungraded_points = obj.total_weight
        else:
            grade_data.weighted_points = obj.weighted_grade
            grade_data.ungraded_points = 0

    return grade_data
