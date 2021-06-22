import attr

from .document import Document
from .has_settings import HasSettings
from .templated import Templated

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class AnswerData():
    """
    Available data about the answers for a document or sub-document
    """
    answer = attr.ib(default=dict)
    children = attr.ib(factory=dict)
    format = attr.ib(default=None, kw_only=True)
    meta = attr.ib(factory=dict, kw_only=True)

    def __new__(cls, *args, **kwargs):
        if len(args) == 1:
            if isinstance(args[0], cls):
                return args[0]
            elif isinstance(args[0], dict) and 'children' not in kwargs:
                kwargs['children'] = args[0]
                args = list()

        return super(AnswerData, cls).__new__(cls, *args, **kwargs)

    def __attrs_post_init__(self):
        for (name, child) in self.children.items():
            self.children[name] = AnswerData(child)

    def merge(self, other):

        other = AnswerData(other)

        self.meta |= other.meta

        if other.answer != None:
            self.answer = other.answer
            self.format = other.format

        for (name, child) in other.children.items():
            if name in self.children:
                self.children[name] = self.children[name].merge(child)
            else:
                self.children[name] = AnswerData(child)

@attr.s
class Answerable(Templated):

    _answer = attr.ib(default=None, init=False)

    settings.new_group(
        "answer", doc=
        """
        Settings about answers
        """)

    settings.answer.new_value(
        "format", default=None, doc=
        """
        An identifier string that describes how an answer should be formatted.
        """)

    def set_answer(self, answer, format = None):
        """
        Set the answer for this document to something.
        """
        self._answer = self.normalize_answer(answer, format)

    def get_answer(self):
        return self._answer

    def normalize_answer(self, answer, format = None):
        """
        Overload this to convert answers into a single format on a per-question
        basis. Ideally to make future auto-grading and printing possible.
        """
        return answer

    def template_answer(self, answer, build_info):
        """
        Used to turn the answer returned by `normalize_answer` and `get_answer`
        into a dict or string that is inserted into the template. Return
        `none` if no answer should appear in the template.

        Overload to change how this works. If you are looking up files that
        are named in the answer then consider using
        `build_info.classroom.answers` to finding the correct directory for
        the corresponding classroom.
        """
        return answer

    def build_template_spec(self, build_info):

        spec = super(Answerable, self).build_template_spec(build_info)

        answer = self.template_answer(self.get_answer(), build_info)

        if answer != None:
            spec.context['answer'] = answer

        return spec

def distribute_answers(obj , answers):
    """
    Takes a document and splits out all the answer information in an
    `AnswerData` to it's children.
    """

    # Check if valid
    if not isinstance(obj, Document):
        raise RuntimeError("Can't distribute answers to non-document")

    # for convenience allow users to pass in raw dictionaries by converting
    # it into an answer data, or single value.
    answers = AnswerData(answers)

    # Copy out basic answers
    if isinstance(obj, Answerable):
        obj.set_answer(answers.answer)
        if answers.format != None:
            obj.settings.answer.format = answers.format
    elif answer.answer != None:
        raise RuntimeError("Trying to set answer on non-answerable doc.")

    # apply to children
    for (name, sub_q) in obj.questions.items():
        if name in answers.children:
            distribute_answers(sub_q, answers.children[name])

    # get extra keys and throw error if any
    extra = [k for k in answers.children.keys() if k not in obj.questions]
    if len(extra) != 0:
        raise RuntimeError(
            "Tried to supply answers for non-existent children : ".format(
                extra
            ))
