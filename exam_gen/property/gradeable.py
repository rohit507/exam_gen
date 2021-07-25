import attr

from copy import *

from .document import Document
from .has_settings import HasSettings
from .templated import Templated

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")


@attr.s(init=False)
class GradeData():
    points = attr.ib(default=None)
    children = attr.ib(factory=dict)
    comment = attr.ib(default=None, kw_only = True)

    answer  = attr.ib(default=None, kw_only=True)
    correct = attr.ib(default=None, kw_only=True)

    ungraded_points = attr.ib(default=0, init=False)
    weighted_points = attr.ib(default=0, init=False)
    total_weight = attr.ib(default=0, init=False)

    def __getitem__(self,key):
        """
        Lets us retrieve child grades in a convinient matter
        """
        return self.children[key]

    @property
    def percent_grade(self):
        if self.total_weight == 0:
            return 0
        return (self.weighted_points / self.total_weight)

    @property
    def percent_ungraded(self):
        if self.total_weight == 0:
            return 0
        return (self.ungraded_points / self.total_weight)

    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            if isinstance(args[0], GradeData):
                kwargs = attr.asdict(args[0], recurse=False)
                args=[]
            elif isinstance(args[0], dict) and 'children' not in kwargs:
                kwargs['children'] = args[0]
                args = []

        if len(args) == 2 and 'comment' not in kwargs:
            kwargs['comment'] = args[1]
            args = [args[0]]

        return self.__attrs_init__(*args, **kwargs)

    def __attrs_post_init__(self):

        if hasattr(super(),'__attrs_post_init__'):
            super().__attrs_post_init__()

        for (name, child) in self.children.items():
            self.children[name] = GradeData(child)
        if self.comment == None:
            self.comment = list()
        elif not isinstance(self.comment, list):
            self.comment = [self.comment]

    def merge(self, other):

        other = GradeData(other)

        if other.grade != None:
            self.grade = other.grade
            self.comment += other.comment
            if other.answer: self.answer = other.answer
            if other.correct: self.correct = other.correct

        for (name, child) in other.children.items():
            if name in self.children:
                self.children[name] = self.children[name].merge(child)
            else:
                self.children[name] = child

        return self


@attr.s
class Gradeable(Templated):

    _grade_data = attr.ib(default=None, init=False)

    _weight = attr.ib(default=None, kw_only=True)
    # _points = attr.ib(default=None, init=False)
    # _comment = attr.ib(default=None, init=False)

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
        The weight of this problem relative to others in exam. If `None`, this
        is assumed to be the same as `settings.grade.max_points`.
        """)

    def __attrs_post_init__(self):
        if hasattr(super(Gradeable,self), '__attrs_post_init__'):
            super(Gradeable,self).__attrs_post_init__()

        # stupid way of sneaking an init parameter into the settings
        if self._weight != None:
            self.settings.grade.weight = self._weight

        # need this for a semi-responsive default setting
        if self.settings.grade.weight == None:
            self.settings.grade.weight = self.settings.grade.max_points

    def _set_points(self, points, comment=None, **kwargs):

        if len(self.questions) > 0:
            raise RuntimeError("Cannot assign grade to doc with sub-questions")

        if points > self.settings.grade.max_points:
            raise RuntimeError("Assigned grade larger than max_points allowed")

        if comment != None: kwargs['comment'] = comment

        grade_data = GradeData(points, **kwargs)

        self.grade_data = grade_data

    def set_points(self, points, comment=None, **kwargs):
        self._set_points(points, comment, **kwargs)

    @property
    def grade_data(self):

        kwargs = dict()

        if self._grade_data != None:

            kwargs = attr.asdict(self._grade_data, recurse=False)
            kwargs.pop('total_weight')#, None)
            kwargs.pop('weighted_points')# , None)
            kwargs.pop('ungraded_points')# , None)
        else:
            kwargs['points'] = 0

        grade_data = GradeData(**kwargs)

        grade_data.total_weight = self.total_weight
        if self.ungraded:
            grade_data.weighted_points = 0
            grade_data.ungraded_points = self.total_weight
        else:
            grade_data.weighted_points = self.weighted_grade
            grade_data.ungraded_points = 0

        return grade_data

    @grade_data.setter
    def grade_data(self, other):
        if self._grade_data == None:
            self._grade_data = other
        else:
            self._grade_data = self._grade_data.merge(grade_data)


    @property
    def ungraded(self):
        return self._grade_data == None

    @property
    def percent_grade(self):
        """
        returns a grade from between 0 and 1
        """
        points = 0
        if not self.ungraded:
            points = self._grade_data.points

        return (points / self.settings.grade.max_points)

    @property
    def weighted_grade(self):
        """
        returns a grade after weighting
        """
        return (self.settings.grade.weight * self.percent_grade)

    @property
    def total_weight(self):
        return self.settings.grade.weight

    def build_template_spec(self, build_info):

        spec = super(Gradeable, self).build_template_spec(
            build_info)

        grade_data = collect_grades(self)

        if grade_data.percent_ungraded != 1:
            spec.context['grade'] = attr.asdict(grade_data, recurse=True)

        return spec

def distribute_scores(obj , grades):
    """
    Takes a document and splits out all the grade information in an
    `GradeData` to it's children.
    """

    # Check if valid
    if not isinstance(obj, Document):
        raise RuntimeError("Can't distribute grades to non-document")

    # for convinience allow the user to supply grades or points directly
    grades = GradeData(grades)

    # Copy out basic grades
    if isinstance(obj, Gradeable):
        obj.set_points(
            grades.points,
            comment=grade.comment,
            answer=grade.answer,
            correct=grade.correct,
        )
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
    grade_data = None

    if isinstance(obj, Gradeable): # Leaves have existing grades
        grade_data = deepcopy(obj.grade_data)

    elif isinstance(obj, Document): # Other documents will not
        grade_data = GradeData()

    else:
        raise RuntimeError("Can't gather grades from non-document")

    # Add children to the calculation if any
    for (name, sub_q) in obj.questions.items():
        sub_data = collect_grades(sub_q)
        grade_data.children[name] = sub_data

        grade_data.total_weight += sub_data.total_weight
        grade_data.ungraded_points += sub_data.ungraded_points
        grade_data.weighted_points += sub_data.weighted_points

    return grade_data
