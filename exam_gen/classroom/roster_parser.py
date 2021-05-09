import csv
import os
import attr
from copy import copy, deepcopy
from pathlib import *
import exam_gen.util.logging as logging
from exam_gen.mixins.random_gen import create_seed

log = logging.new(__name__, level="DEBUG")

@attr.s
class RosterParser():

    file_name = attr.ib()
    ident_field = attr.ib(default='username', kw_only=True)
    """
    The field of the student information that should be used as the unique
    identifier in the roster, folder names, and everywhere else.
    """

    roster_tweaks = attr.ib(factory=dict, kw_only=True)
    """
    Use roster tweaks to change the value of some parameter for a student.
    """

    def get_roster_data(self, builder, root_dir):
        """
        Expected result should have 'name', 'sid', 'username', and 'root_seed'
        fields for each student.

        !!! Note
            While `read_roster_data`'s output should have 'sid's as keys
            the dict output from this function will use whatever field is
            specified by `self.ident_field`. (default: `'username'`)

            This gives us somewhat more readable file and directory names in
            most cases.
        """
        raw_data = self.read_roster_data(builder, root_dir)
        modified_data = dict()
        for (_, data) in raw_data.items():

            ident = data[self.ident_field]

            if ident in self.roster_tweaks:
                data = dict(data, **roster_tweaks[ident])

            root_seed = self.gen_student_seed(builder, data)

            if 'root_seed' not in data:
                data['root_seed'] = root_seed

            data['ident'] = ident

            modified_data[ident] = deepcopy(data)

        return modified_data

    def gen_student_seed(self, builder, student_data):
        return create_seed(student_data['sid'], student_data['name'])

    def read_roster_data(self, builder, root_dir):
        """
        Should read the data from the roster and format it in a dict
        where each key is a student's identifier (sid) and the values are
        a dictionary of metadata about the student.

        The student data should be a dictionary with, at minimum, the following
        fields:

          - 'name' : student's name
          - 'sid'  : student's unique (usually numeric) identifier
          - 'username'  : student's unique (usually string) username

        Any additional fields in student information will just be passed
        forward to future steps.
        """
        assert False, "Should be overriden in subclass"

@attr.s
class BCoursesCSVRoster(RosterParser):
    """
    A roster parser for the bcourses csv roster format.
    """

    domain = attr.ib(default='berkeley.edu', kw_only=True)

    def read_roster_data(self, builder, root_dir):
        input_data = Path(root_dir) / self.file_name
        input_file = input_data.open(mode='r')

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

            outputs[sid] = student

        return outputs
