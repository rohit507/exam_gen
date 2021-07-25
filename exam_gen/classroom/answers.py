import attr
import csv

from pathlib import *
from copy import *

from .student import Student

from exam_gen.property.has_dir_path import HasDirPath
from exam_gen.property.answerable import AnswerData, distribute_answers

from exam_gen.util.with_options import WithOptions
from exam_gen.util.selectors import *

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class Answers(HasDirPath, WithOptions):

    exam = attr.ib(kw_only=True)

    def load_answers(self, students):
        """
        Load the answers from file, producing a dictionary from student id
        to AnswerData for that student
        """
        raise RuntimeError("Must implement in subclass")

@attr.s
class CSVAnswers(Answers):

    file_name = attr.ib()
    mapping = attr.ib()
    ident_column = attr.ib(converter=StudentSelect, default="Student ID")
    attempt_column = attr.ib(default=None)


    def __attrs_post_init__(self):

        if hasattr(super(),'__attrs_post_init__'):
            super().__attrs_post_init__()

        self.mapping = DocSelect(self.mapping, norm_field=CSVAnswers._norm_map_field)
        if self.attempt_column != None:
            self.attempt_column = FieldSelect(self.attempt_column)

    def load_answers(self, students):

        file_name = self.lookup_file(self.file_name)
        raw_answers = self.read_answers(file_name)
        return self.convert_answers(students, raw_answers)

    def read_answers(self, file_name):

        input_file = Path(file_name).open(mode='r')
        answer_list = list(csv.DictReader(input_file))

        return answer_list

    def convert_answers(self, students, answers):
        """
        Parse single submissions out to students and merge them
        """

        merge_attempts = lambda new, old: [new] if old == None else [new] + old

        student_attempts = self.ident_column.partition(students,
                                                       answers,
                                                       merge_with=merge_attempts)

        student_answers = dict()

        for (ident, attempts) in student_attempts.items():
            student_answers[ident] = self.unify_attempts(attempts)

        return student_answers

    def convert_attempt(self, attempt):
        """
        Convert a single submission into an answerdata using the mapping info
        """
        return self.mapping.select(
            attempt,
            supress_error=True,
            with_meta=lambda match, meta: AnswerData(match, **meta)
        )

    def unify_attempts(self, attempt_list):
        """
        Will combine all the submission attempts of the students keeping the
        most recent of each submitted answer.
        """

        if self.attempt_column == None and len(attempt_list) != 1:
            raise RuntimeError("Multiple Submissions the same student with no"
                               " attempt number column specified.")

        answer_data = None
        for attempt in attempt_list:
            new_data = AnswerData(
                children=self.convert_attempt(attempt),
                meta={'raw':attempt}
                )

            if self.attempt_column != None:
                new_data.meta['attempt_num'] = self.attempt_column.select(attempt)

            if answer_data != None:
                if new_data.meta['attempt_num'] < answer_data.meta['attempt_num']:
                    answer_data, new_data = (new_data, answer_data)

                new_data.meta['prev_attempt'] = answer_data

                answer_data = deepcopy(answer_data)

                answer_data.merge(deepcopy(new_data))

            else:

                answer_data = new_data

        return answer_data


    @staticmethod
    def _norm_map_field(field):
        """
        Normalizes a field in a mapping, allowing you to specify the format
        of the answer in a dict or tuple.
        """
        sel = field
        meta = dict()

        if isinstance(field, dict) and 'format' in field and 'field' in field:
            sel = field['field']
            meta['format'] = field['format']
        elif isinstance(field, Iterable) and len(field) == 2:
            sel = field[0]
            meta['format'] = field[1]

        return (sel, meta)

# StudentSel :: Record -> Student -> Bool

# Find students for each record

# Record -> (Answer | Score | Grade) Fmt -> (Answer | Score | Grade) Data

# foo = Answers(
#     identifier = "Student ID",
#     mapping = {
#         'prob1' : "Field Name",
#         'prob2' : { 'prob2a' : "New Field Name",
#                     'prob2b' : "New Field Name 2" },
#         }
#     )
