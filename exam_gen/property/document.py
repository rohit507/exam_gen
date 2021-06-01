import attr

from copy import *
from pprint import *

from exam_gen.util.with_options import WithOptions

import exam_gen.util.logging as logging

log = logging.new(__name__, level="WARNING")

@attr.s
class Document(WithOptions):
    """
    Root class for exams, questions, and the like.
    Mainly this specifies that there's a list of questions that can be
    included and set for all the children.
    """

    _parent_doc = attr.ib(default=None, kw_only=True)

    questions = {}

    def __attrs_post_init__(self):

        if hasattr(super(Document, self), '__attrs_post_init__'):
            super(Document, self).__attrs_post_init__()

        questions = dict()

        if hasattr(type(self),'questions'):
            questions = deepcopy(getattr(type(self), 'questions'))

        self.questions = questions


    def init_document(self, doc_class, **kwargs):
        """
        Overloading this, with calls to super, allows for modification of
        the member class being initialized with new options.

        This shouldn't do much more than pass options needed at init through
        to child entities or propagate settings information down.

        Example of how you'd use `super()` in a child class:

        ```
        @classmethod
        def init_document(cls, doc_class, **kwargs):

            new_class = # modify doc_class / return new class

            doc_obj = super().init_document(
                new_class,
                added_arg = "example",
                **kwargs)

            return # modify doc_obj / return new object
        ```

        Done like this, `init_questions` will happily recurse down the tree
        of options.

        Note: unlike `setup_build`, `pwd` isn't guaranteed to be the same as
        the build directory so don't manipulate any files w/o an absolute path.
        """
        doc_obj = doc_class(**kwargs)
        doc_obj.init_questions()
        return doc_obj

    def init_questions(self):
        """
        Just runs through all the questions in the document and initializes
        them as needed.

        Meant to be used sometime before `setup_build`.
        """


        for (name, question_class) in self.questions.items():

            log.debug("%s \n %s", type(self), self.questions.keys())

            self.questions[name] = self.init_document(
                question_class,
                parent_doc = self
            )

    def on_children(self, fun):

        log = dict()
        for (name, question) in self.questions.items():

            log[name] = (fun(question), question.on_children(fun))

        return log
