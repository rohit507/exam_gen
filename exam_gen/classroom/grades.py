import attr

from pathlib import *
import csv

from .student import Student

from exam_gen.util.with_options import WithOptions
from exam_gen.property.has_dir_path import HasDirPath

from exam_gen.util.selectors import *

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class Grades(HasDirPath, WithOptions):

    exam = attr.ib()

    def print_grades(self, student_dict, out_dir):
        pass


@attr.s
class CSVGrades(Grades):
    """
    Mapping is a
    dict with entries as follows
    """

    file_name = attr.ib(default="grades.csv", kw_only=True)
    columns = attr.ib(factory=dict, kw_only=True)

    def print_grades(self, student_dict, out_dir):

        col_keys = list(self.columns.keys())

        out_file = Path(out_dir, self.file_name)

        out_file.parent.mkdir(parents=True, exist_ok=True)

        writer = csv.DictWriter(out_file.open('w'), fieldnames=col_keys)
        writer.writeheader()

        out_entries = dict()

        for (student_id, student) in student_dict.items():
            entry = self.gen_grade_record(col_keys, student)
            writer.writerow(entry)
            out_entries[student_id] = entry

        return out_entries

    def gen_grade_record(self, col_keys, student):

        fields = dict()

        for key in col_keys:
            fields[key] = self.parse_field(
                spec=self.columns[key].split('.'),
                student=student,
                grade_data=student.grade_data
            )

        return fields

    def parse_field(self, spec, student, grade_data, base_field=True):

        if not isinstance(spec, list):
            raise TypeError("Expected list")
        elif len(spec) == 0:
            raise RuntimeError("empty parse spec")
        elif len(spec) > 1:
            if spec[0] in grade_data.children:
                return self.parse_field(
                    spec[1:],
                    student,
                    grade_data.children[spec[0]],
                    base_field=False
                )
            else:
                raise RuntimeError("Could not find question "+spec[0]+".")
        elif base_field and hasattr(student,spec[0]):
            return getattr(student, spec[0])
        elif hasattr(grade_data,spec[0]):
            return getattr(grade_data, spec[0])
        else:
            raise RuntimeError("Could not find field {}.".format(spec[0]))
