
import attr
import textwrap

from .field import *

from exam_gen.classroom.student import *

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class StudentSelect():
    """
    Associates records with students.

    Params:

      record_field: The field of the record we're going to be using as an
        identifier.

      student_field: The field of the student we'll match it to, available
        options are:

          - "ident": The base identifier
          - "name": The student's name in "Last, First" format (not reccomended)
          - "student_id" : The students id number (default)
          - "usersame" : The student's username.

        Other values will default to fields in "student_data", taken from the
        roster directly.
    """

    record_field = attr.ib()

    student_field = attr.ib(default="student_id")

    def __new__(cls, *args, **kwargs):
        """
        Sorta idempotent normalised new.
        """

        if len(args) == 1 and len(kwargs) == 0:
            if isinstance(args[0], cls):
                return args[0]
            elif isinstance(args[0], Iterable):
                args = args[0]
            elif isinstance(args[0], dict):
                args = []
                kwargs |= args

        return super(StudentSelect, cls).__new__(cls, *args, **kwargs)

    def __attrs_post_init__(self):

        self.record_field = FieldSelect(self.record_field)
        self.student_field = self._init_st_fld(self.student_field)

    @classmethod
    def _init_st_fld(cls, student_field):
        if student_field == "ident":
            return lambda s: s.ident
        elif student_field == "name":
            return lambda s: s.name
        elif student_field == "username":
            return lambda s: s.username
        elif student_field == "student_id":
            return lambda s: s.student_id
        else:
            f = FieldSelect(student_field)
            return lambda s, fs=f: fs.select(s.student_data)

    def match(self, student, record):
        """
        Check whether this student matches the given record.

        Overload this to implement more advanced behavior.
        """
        return self.student_field(student) == self.record_field.select(record)

    def select_student(self, students, record, supress_error = False):
        """
        Find a student that matches a given record.
        """

        for (key, student) in students.items():
            if self.match(student, record):
                return (key, student)

        if not supress_error:
            raise RuntimeError(
                textwrap.dedent(
                    """
                    No student found matching given record:

                      Record Field: {}

                      Record: {}
                    """
                    ).format(self.record_field, record))

        return None

    def select_records(self, student, records, merge_with=None):
        """
        Get the set of records associated with a given student.
        """

        merge_with = merge_with if merge_with else (lambda a, b: a)

        if isinstance(records, dict):
            out = dict()
            for (key, record) in records.items():
                if self.match(student, record):
                    out[key] = merge_with(record, out.pop(key, None))
            return out
        elif isinstance(records, Iterable):
            out = list()
            for record in records:
                if self.match(student, record):
                    out.append(record)
            return out
        else:
            raise RuntimeError("Records must be list or dict.")

    def partition(self, students, records, student_field=None, merge_with=None):
        """
        Go through a set of students and associate records with them.
        """

        student_dict = dict()
        student_field = (self._init_st_fld(student_field) if student_field
                         else self.student_field)

        if isinstance(students, dict):
            student_dict = students
        elif isinstance(students,Iterable):
            for student in student:
                key = student_field(student)
                student_dict[key] = student
        else:
            raise RuntimeError("Students must be provided as dict or iterable")

        record_dict = dict()

        for (key, student) in student_dict.items():
            record_dict[key] = self.select_records(student,
                                                   records,
                                                   merge_with=merge_with)

        return record_dict
