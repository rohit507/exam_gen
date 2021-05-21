import attr

from exam_gen.property.traversable import *

from exam_gen.util.with_options import with_options

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class Personalized():
    """
    Classes that are initialized with information on a specific student.
    """

    student_id = attr.ib()
    """
    The student that this instance of the exam is for.
    """

    classroom = attr.ib()
    """
    The classroom object we're querying for information on a student.
    """

@attr.s
class PersonalDoc(Personalized,Traversable):
    """
    Will initialize all the different subdocs with the student_id and classroom
    information.

    This expects
    """

    def __attrs_post_init__(self):

        if hasattr(super(),'__attrs_post_init__'):
            super().__attrs_post_init__()

        def unit(*vargs, **kwargs): return None

        # updates the class information with the new parameters
        def step(self, **params):

            if issubclass(params['member'], Persomalized):
               obj = with_options(
                   params['member'],
                   student_id = self.student_id,
                   classroom = self.classroom)
               params['set_var'](obj)

        traversable.make_walk(setup = unit, step = step, finalize=unit)(self)
