import attr
from pathlib import *
import inspect
import exam_gen.util.logging as logging
import exam_gen.classroom.roster_parser as roster

log = logging.new(__name__, level="DEBUG")

@attr.s
class Classroom():


    class_file = attr.ib(default=None,kw_only=True)
    """
    Set equal to `__file__` in cases where you're using a subdir for each
    class.
    """

    def _get_root_dir(self, builder):
        """
        If this classroom is defined in a sub-file of project directory
        work w/in that sub-directory.
        """
        proj_root = builder.root_dir
        self_root = Path(inspect.getfile(type(self)))

        if self.class_file != None:
             self_root = self.class_file

        elif self_root.parent.is_relative_to(proj_root):
            return self_root.parent
        else:
            return proj_root

    roster  = attr.ib(default=None)
    "obj that defines to find and parse a roster"

    def parse_roster(self, builder):
        """
        Returns a dict from student-id to student metadata.

        if the new classroom is created in a subfolder relative to the exam
        this will use that
        """
        root_dir = self._get_root_dir(builder)
        # print(rd)
        return self.roster.get_roster_data(builder,root_dir)

    answers = attr.ib(default=None)
    "defines where to find and how to parse student answers"

    grades = attr.ib(default=None)
    "defines how to parse grades"

    results = attr.ib(default=None)
    "defines how to print the results of grading an exam"
