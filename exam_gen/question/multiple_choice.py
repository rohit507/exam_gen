import attr
import textwrap
import functools

from copy import *
from pprint import *
from textwrap import *
from collections.abc import *
from numbers import *

from exam_gen.util.versioned_option import add_versioned_option
from exam_gen.property.templated import (
    __template_versioned_opts__,
    exam_format_key_func,
    template_spec_from_var
)

from exam_gen.property.has_settings import HasSettings
from exam_gen.property.has_user_setup import HasUserSetup
from exam_gen.property.has_context import HasContext
from exam_gen.property.auto_gradeable import AutoGradeable

from .base import Question, __exam_formats__

from exam_gen.util.excel_cols import excel_col
import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

def choice_key_func(self, key):
    if isinstance(key, int):
        return key
    else:
        raise RuntimeError(("{} Is not a valid index for a choice in a "
                            "multiple choice question").format(key))

__choices_versioned_opts__ = __template_versioned_opts__ | {
    'total_number':{'default':5, 'root_only':True},
    'capitalize_letters':{'default':True, 'root_only':True},
    'is_correct':{'default':False},
    }


choices_doc = textwrap.dedent(
    """
    Settings for individual choices

    TODO: futher explanation
    """)

exam_key_func = functools.partial(exam_format_key_func,
                             format_list=__exam_formats__)

@add_versioned_option(
    name = "choice",
    option_spec = __choices_versioned_opts__,
    doc = choices_doc,
    format_spec = [{'key_func': choice_key_func}, {'key_func': exam_key_func}]
    )
@attr.s
class MultipleChoiceQuestion(AutoGradeable, Question):

    settings.grade.new_value(
        "style", default="all_correct", doc=
        """
        How to grade this multiple choice question.

        Valid options are:
          - "all_correct": all the correct choices are selected and no
            incorrect choices are selected.
          - "any_correct": at least one correct choice is selected and no
            incorrect choice is selected.
          - "percent_correct": a score between 0 and `settings.grade.max_points`
            proportional to `(selected_correct_choices + unselected_wrong_choices) / total_choices`
          - "custom": defers to the user provided `calculate_grade` function.
            See the docs for more details.
        """)

    settings.grade.new_value(
        "shuffle", default=True, doc=
        """
        Determines whether the choices should be randomly shuffled before
        being given to the student.

        Valid Options are:
          - `True`: Shuffle all choices
          - `False`: Don't shuffle any choices
          - A list of choice numbers: Shuffle only those options amongst
            themselves. For instance `[0,2,3]` would shuffle those options but
            leaves options `[1,4,5]` static. You could get a permutation of
            `[3, 1, 2, 0, 4, 5]` but not `[1 , 2, 4, 0, 5]` since the latter
            moves `1` and `4` out of place.
        """)

    settings.grade.new_value(
        "supress_correct_choice_error", default=False, doc=
        """
        Supress the error that's raised when there's no correct choices
        provided to the student.
        """)

    settings.grade.new_value(
        "supress_incorrect_choice_error", default=False, doc=
        """
        Supress the error that's raised when there's no incorrect choices
        provided to the student.
        """)

    settings.grade.new_value(
        "supress_choice_equality_error", default=False, doc=
        """
        Supress the error that's raised when multiple choices have the same
        content.
        """)

    settings.template.embedded = "multiple_choice_embed.jn2"

    forward_map = attr.ib(factory=dict, init=False)
    forward_letter = attr.ib(factory=dict, init=False)
    reverse_map = attr.ib(factory=dict, init=False)
    reverse_letter = attr.ib(factory=dict, init=False)

    def gen_permutation(self):

        to_shuffle = self.settings.grade.shuffle

        if self.settings.grade.shuffle == False:
            to_shuffle = list()
        elif self.settings.grade.shuffle == True:
            to_shuffle = range(0, self.choice.total_number)

        rng = self.get_keyed_rng("choice_shuffle")

        result = rng.sample(to_shuffle, k=len(to_shuffle))

        for (orig, shuff) in zip(to_shuffle, result):
            self.forward_map[orig] = shuff
            self.reverse_map[shuff] = orig

        for i in range(0, self.choice.total_number):
            if i not in self.forward_map:
                self.forward_map[i] = i
                self.reverse_map[i] = i

    def gen_letter_maps(self):

        seq_char = 'A' if self.choice.capitalize_letters else 'a'

        for (orig, shuff) in self.forward_map.items():
            letter =  excel_col(seq_char, shuff)
            self.forward_letter[orig] = letter
            self.reverse_letter[letter] = orig

    def check_total_choices(self):

        choice_tree = self.choice.version_tree()

        def opt_set(opt):
            return (opt.text != None or opt.file != None)

        opt_map = dict()

        # Check if base options are set or if there's an invalid choice
        # number given
        for (key, var) in choice_tree.items():
            if key == None:
                opt_map[None] = opt_set(var)
            elif isinstance(key, str):
                opt_map[key] = opt_set(var)
            elif key >= self.choice.total_number:
                raise RuntimeError(
                    ("Trying to set choice number {} but "
                     "`choice.total_number is only {}. Try "
                     "increasing the number of choices").format(
                         key, self.choice.total_number))

        # do we have a base case template for choices?
        root_opt = None in opt_map or (
            all(map(lambda k: k in opt_map, __exam_formats__)))

        # if not make sure there's an explicit template provided for each
        # choice.
        if not root_opt:
            for ind in range(0, self.choice.total_number):
                if ind not in choice_tree:
                    raise RuntimeError(
                        ("Could not find explicit template for choice[{}] "
                         "try setting choice[{}].text, choice[{}].file or "
                         "setting choice.total_number to the correct value"
                        ).format(ind, ind, ind))

    def setup_build(self, build_info):
        log_ = super().setup_build(build_info)

        self.check_total_choices()
        self.gen_permutation()
        self.gen_letter_maps()
        self.validate_settings()
        if self.get_answer() != None:
            self.__calc_grade_harness__()

        return log_

    def normalize_answer(self, answer):

        conv_letter = lambda a: a.upper() if self.choice.capitalize_letters else a.lower()

        norm_letters = map(conv_letter, answer)
        num_answers = map(lambda a: self.reverse_letter[a], norm_letters)

        return list(num_answers)

    def __calc_grade_harness__(self):

        answer = self.normalize_answer(self.get_answer())

        grade_result = self.select_grading_func(answer)

        args = self.norm_grade_result(
            grade_result,
            self.settings.grade.max_points
        )

        if 'answer' not in args:
            args['answer'] = ', '.join(sorted(
                [self.forward_letter[i] for i in answer]))

        if 'correct' not in args:
            args['correct'] = ', '.join(sorted(
                [self.forward_letter[i]
                 for i in range(0,self.choice.total_number)
                 if self.choice[i].is_correct]))

        self._set_points(**args)

    def set_answer(self, answer):

        norm_letter = lambda s: s.strip().upper()

        if isinstance(answer, str):
            self._answer = list(map(norm_letter, answer.split(',')))
        elif isinstance(answer, list) and isinstance(answer[0], str):
            self._answer = list(map(norm_letter, answer))
        else:
            raise RuntimeError(
                 "Question answer is in unknown format, acceptable "
                 "formats are: comma separated string of choice letters, "
                 "list of choice letters")

    def select_grading_func(self, answer):
        if self.settings.grade.style == 'all_correct':
            return self.grade_all_correct(answer)
        elif self.settings.grade.style == 'any_correct':
            return self.grade_any_correct(answer)
        elif self.settings.grade.style == 'percent_correct':
            return self.grade_percent_correct(answer)
        elif self.settings.grade.style == 'custom':
            return self.grade_custom(answer)
        else:
            raise RuntimeError(
                "'{}' is not a valid grading style".format(
                    self.settings.grade.style))

    def grade_all_correct(self, answer):
        corr = ((self.count_false_positives(answer) == 0) and
                (self.count_false_negatives(answer) == 0))
        return 0 if not corr else self.settings.grade.max_points

    def grade_any_correct(self, answer):
        corr = ((self.count_correct(answer) >= 1) and
                (self.count_false_negatives(answer) == 0))
        return 0 if not corr else self.settings.grade.max_points

    def grade_percent_correct(self, answer):
        return (((self.choice.total_number
                  - self.count_false_positives(answer)
                  - self.count_false_negatives(answer))
                / self.choice.total_number)
                * self.settings.grade.max_points)

    def grade_custom(self, answer):
        is_answer = list()
        is_correct = list()
        for i in range(0, self.choice.total_number):
            is_answer.append(i in answer)
            is_correct.append(self.choice[i].is_correct)

        if self.final_context == None:
            raise RuntimeError("Can only calculate grade after `user_setup` "
                               "is run")

        return self.calculate_grade(
            self.final_context,
            is_answer
        )


    def norm_grade_result(self, result, max_points=1):
        args = dict()

        # Make inputs a tuple
        if isinstance(result, Iterable):
            result = tuple(result)
        else:
            result = (result,)

        # Extract point total
        if isinstance(result[0], Number):
            args['points'] = result[0]
            result = result[1:]
        elif isinstance(result[0], bool):
            args['points'] = max_points if result[0] else 0
            result = result[1:]

        # Extract dict
        if len(result) > 0 and isinstance(result[-1], dict):
            args = result[-1] | args
            result = result[:-1]

        # Extract comment
        if len(result) == 1 and 'points' in args:
            args['comment'] = result[0]
        elif len(result) == 0 and 'points' in args:
            pass
        else:
            raise RuntimeError("Invalid return for calculate_grade")

        return args

    def calculate_grade(self, ctxt, is_answer):
        """
        Function to overload when using a custom grade function.
        This should always return a number between 0 and max_points.
        The library will appropriately scale that value as needed.

        Params:

           ctxt: The context as returned by `user_setup`
           is_answer: a list of bools telling you whether each choice was
              selected. All the indices have been appropriately unshuffled.

        Returns:

           Any of the following:
             1) A boolean where `True` means `max_points` and `False` means `0`.
             2) A single number from `0` to `max_points`.
               (larger numbers will be treated as extra credit.)
             3) A dictionary with some of the following keys:
                - 'points': As option 2.
                - 'comment' : A comment on the answer.
                - 'answer': The student provided answer
                - 'correct': The correct answer.
             4) A tuple where the first element is either option 1 or 2, the
               next elements are either a comment, option 3, or both.
        """
        raise NotImplementedError(
            ("Must implement 'calculate_grade' if using a custom grading "
             "function."))

    def count_false_positives(self, answer):
        def is_fp(n): return (not self.choice[n].is_correct) and (n in answer)
        return count_true(is_fp, range(0, self.choice.total_number))

    def count_false_negatives(self, answer):
        def is_fn(n): return self.choice[n].is_correct and (n not in answer)
        return count_true(is_fn, range(0, self.choice.total_number))

    def count_correct(self):
        return count_true(lambda n: self.choice[n].is_correct,
                          range(0, self.choice.total_number))

    def count_incorrect(self):
        return count_true(lambda n: not self.choice[n].is_correct,
                          range(0, self.choice.total_number))

    def validate_settings(self):
        # ensure there's a correct answer false answer
        some_correct = False
        some_incorrect = False

        for ind in range(0,self.choice.total_number):
            if self.choice[ind].is_correct:
                some_correct = True
            else:
                some_incorrect = True

        if not some_correct and not self.settings.grade.supress_correct_choice_error:
            raise RuntimeError("Question has no correct answers.")
        if not some_incorrect and not self.settings.grade.supress_incorrect_choice_error:
            raise RuntimeError("Question has no incorrect answers.")

    def build_template_spec(self, build_info=None):

        spec = super().build_template_spec(
            build_info)

        # Add the hook to ensure we're not making giving the student a bunch of
        # identical_choices
        if not self.settings.grade.supress_choice_equality_error:
            spec.post_render_hook = functools.partial(
                post_render_choice_validation,
                type(self).__name__,
                copy(self.forward_letter))

        choices = list()

        for ind in range(0,self.choice.total_number):

            orig_ind = self.reverse_map[ind]

            cspec = template_spec_from_var(
                self.choice , versions=[orig_ind,
                               build_info.exam_format])

            cspec.context['index'] = orig_ind
            cspec.context['letter'] = self.forward_letter[orig_ind]
            cspec.context['choice_letters'] = copy(self.forward_letter)
            cspec.context['is_correct'] = self.choice[orig_ind].is_correct

            if self._answer != None:
                cspec.context['has_answer'] = True
                cspec.context['in_answer'] = orig_ind in self._answer

            choices.append(cspec)

        spec.subtemplates['choices'] = choices

        return spec

def post_render_choice_validation(name, let_map, return_val):
    for (i, ret_i) in enumerate(return_val['choices']):
        for (j, ret_j) in enumerate(return_val['choices']):
            if i != j and ret_i['text'].strip() == ret_j['text'].strip():
                raise RuntimeError(
                    ("Options {} and {} in MultipleChoiceQuestion {} "
                     "have identical contents:\n\n"
                     " Option {} w/ Letter {}:\n"
                     "{}\n\n"
                     " Option {} w/ Letter {}:\n"
                     "{}\n\n").format(i, j, name,
                                      i, let_map[i], ret_i['text'],
                                      j, let_map[j], ret_j['text']))

def count_true(fn, ls):
    return sum(map(lambda n: 0 if fn else 1, ls))
