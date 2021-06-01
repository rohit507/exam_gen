import attr

from copy import *
from pprint import *

from .document import Document
from .has_settings import HasSettings
from .templated import Templated

from exam_gen.util.excel_cols import excel_col
from exam_gen.util.with_options import WithOptions

import exam_gen.util.logging as logging

log = logging.new(__name__, level="WARNING")

@attr.s
class Numbered(Templated):

    _depth = attr.ib(default=0, kw_only=True)
    _numbering_depth = attr.ib(default=None, kw_only=True)
    _number = attr.ib(default="", kw_only=True)

    settings.new_value(
        'numbering_scheme',
        default='1a.',
        doc=
        """
        The scheme for numbering child questions in the exam or document.

        Each char in the string represents a sequence to use for each sub-level
        of the document.

          - `1`: Sequence of integers `1`,`2`,`3`, and so on.
          - `a`: Sequence of lower-case letters in excel column order.
            `a`,`b`,`c`, ... ,`aa`,`ab`,`ac`, etc..
          - `A`: as above but upper-case.

        Additionally `.` is a special character that tells when a period should
        be inserted as a separator. Also the sequence will repeat the

        For instance the default scheme `1a.` would give us a tree like:
        ```
          - 1
          - 2
            - 2a
            - 2b
              - 2b.1
          - 3
            - 3a
              - 3a.1
                - 3a.1a
                  - 3a.1a.1
        ```

        Note that this setting won't register any changes in `user_setup`
        """)

    def init_questions(self):

        super(Numbered, self).init_questions()

        if self._parent_doc == None:
            self.push_numbering()

    # def __attrs_post_init__(self):

    #     if hasattr(super(), '__attrs_post_init__'):
    #         super().__attrs_post_init__()


    def push_numbering(self):

        if self._numbering_depth == None or self._numbering_depth == "":
            self._numbering_depth = self.settings.numbering_scheme

        for (ind, (name, question)) in enumerate(self.questions.items()):

            self.questions[name].settings.numbering_scheme = (
                self.settings.numbering_scheme)

            self.questions[name]._numbering_depth = self._numbering_depth[1:]

            self.questions[name]._depth = self._depth + 1

            self.questions[name]._number = self._get_subq_number(ind)

            self.questions[name].push_numbering()



    def build_template_spec(self, build_info):

        spec = super(Numbered, self).build_template_spec(build_info)

        spec.context['number'] = self._number
        spec.context['nesting_depth'] = self._depth
        spec.context['numbering_depth'] = self._numbering_depth
        spec.context['numbering_scheme'] = self.settings.numbering_scheme

        return spec

    def _get_subq_number(self, ind):

        numbering_depth = self._numbering_depth

        prefix = ""

        while not numbering_depth[0].isalnum():

            prefix += numbering_depth[0]
            numbering_depth = numbering_depth[1:]

            if numbering_depth == "":
                numbering_depth = self.settings.numbering_scheme

        return self._number + prefix + excel_col(numbering_depth[0], ind)
