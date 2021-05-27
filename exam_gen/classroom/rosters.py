import attr
import csv

from pathlib import *

from .student import Student

from exam_gen.property.has_dir_path import HasDirPath
from exam_gen.util.with_options import WithOptions
from exam_gen.util.stable_hash import stable_hash

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class Roster(HasDirPath, WithOptions):

    file_name = attr.ib()
    exam = attr.ib()
    tweaks = attr.ib(factory=dict, kw_only=True)
    students = attr.ib(factory=dict, init=False)


    def load_roster(self):

        file_name = self.lookup_file(self.file_name)

        base_roster = self.read_roster(file_name)

        for (ident, student) in base_roster.items():

            if ident in self.tweaks:
                student = self.tweak_entry(ident, student, self.tweaks[ident])

            if student.root_seed == None:
                student.root_seed = self.student_seed(student)

            self.students[ident] = student

        return self.students

    def read_roster(self, file_name):
        """
        Read in the roster file and produce a dict of students (the py object)
        where each key is a student ID.

        These must have the mandatory fields set.
        """
        raise NotImplementedError(
            "Should be implemented in specific sub-classes of `Roster` "
            "that are format specific")

    def tweak_entry(self, student_id, student_obj, tweak_entry):
        """
        Modifies a single student entry with whatever tweak data is provided.
        """
        if 'root_seed' in tweak_entry:
            student_obj.root_seed = tweak_entry['root_seed']

        if 'name' in tweak_entry:
            student_obj.name = tweak_entry['name']

        if 'username' in tweak_entry:
            student_obj.username = tweak_entry['username']

        student_obj.student_data |= tweak_entry

        return student_obj

    def student_seed(self, student_obj):
        """
        """
        return stable_hash(student_obj.ident,
                           student_obj.name,
                           student_obj.username)

@attr.s
class BCoursesCSVRoster(Roster):

    domain = attr.ib(default="berkeley.edu", kw_only=True)

    def read_roster(self, file_name):

        input_file = Path(file_name).open(mode='r')
        roster_list = list(csv.DictReader(input_file))
        outputs = dict()

        for student in roster_list:
            (username, domain) = student['Email Address'].split('@')

            if domain != self.domain:
                username = student['Email Address']
            sid = student['Student ID']
            name = student['Name']

            student['name'] = name
            student['sid'] = sid
            student['username'] = username

            outputs[username] = Student(ident=username,
                                        name=name,
                                        username=username,
                                        student_data=student)
        return outputs
