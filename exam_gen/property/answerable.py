import attr

from .document import Document
from .has_settings import HasSettings
from .templated import Templated

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class AnswerData():
    answer = attr.ib(default=None)
    children = attr.ib(factory=dict)
    format = attr.ib(default=None, kw_only=True)

    @staticmethod
    def normalise(data):
        if isinstance(data, AnswerData):
            return data
        elif isinstance(data, dict):
            return AnswerData(children=data)
        else:
            return AnswerData(answer=data)


    def merge(self, other):

        other = AnswerData.normalize(other)

        if other.answer != None:
            self.answer = other.answer
            self.format = other.format

        for (name, child) in other.children.items():
            if name in self.children:
                self.children[name] = AnswerData.normalise(
                    self.children[name]).merge(child)
            else:
                self.children[name] = AnswerData.normalize(child)



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

    def set_answer(self, answer):
        self._answer = answer

    def get_answer(self):
        return self._answer

    def build_template_spec(self, build_info):

        spec = super(Answerable, self).build_template_spec(
            build_info)

        if self._answer != None:
            spec.context['answer'] = self._answer

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
    answers = AnswerData.normalize(answers)

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
