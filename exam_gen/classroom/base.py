import attr

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class Classroom():

    class_name = attr.ib() # String

    roster  = attr.ib(default=None) # obj that defines where to find and parse a roster
    answers = attr.ib(default=None) # defines where to find and how to parse student answers
    grading = attr.ib(default=None) # defines how to format and output grades

    def parse_roster(self):
        """
        Returns a dict from student id to student metadata
        """
        pass

    def parse_answers(self):
        """
        returns a dict from student id to (a dict from question header to
        answer).
        """
        pass

    def print_grades(self, grades):
        """
        Param:

           grades: Dict from student id to (metadata, grades) tuple

        return: it prints things out, return None
        """
        pass

    pass
