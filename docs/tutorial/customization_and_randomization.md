# Customizing and Randomizing Questions

We'll be adding some additional customization to the question itself in this
section of the tutorial, starting from basic use of context variables about
the exam and student, through to randomizing the question's values itself.

## Using Templates for Customization

The core of `exam_gen` is built around the `jinja2` library, a templating
library designed for HTML but usable for pretty much any text. Most of the text
one has to specify for a question or an exam is actually a template which can
be modified at runtime.

!!! Info ""
    **Jinja2's template format has comprehensive documentation available
    [here](https://jinja.palletsprojects.com/en/3.0.x/templates/)**

  - We can show this by editing `addition_question.py` so the body will read:

    ```python linenums="6"
        body.text = r'''
        Hello \texttt{ {{ student['Email Address'] }} },

        Welcome to question number {{ number }}.
        '''
    ```

    !!! Important "Important Things to Notice"

        1. Statements between `{{` and `}}` are expressions that will be
           replaced with their values.
        2. `student['Email Address']` and `number` (the question number) are
           variables the template will have access to when it's rendered.
        3. We need to use a space to separate LaTeX's `{`s from jinja's `{{`
           as with the `\texttt{ {{` on line 7.

  - Generate the exams for different students and see how the different exams
    each have the appropriate student's email address.

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    ```

    You'll find them in `~out/exam-exam/class-fake-class/`.

??? Example "Complete Current `addition_question.py`"
    ```python linenums="1"
    from exam_gen import *

    class SumQuestion(LatexDoc, Question):
        metadata.name = "Basic Addition Question"

        body.text = r'''
        Hello \texttt{ {{ student['Email Address'] }} },

        Welcome to question number {{ number }}.
        '''

        solution.text = "Placeholder text for the solution of the question."
    ```

## Finding Available Template Variables

In order to assist in writing templates `exam_gen` dumps the available variables
for each template it renders into the appropriate folder in `~data`.

If you look in `~data/class-fake-class/student-erios/exam-exam` you'll find a
number of intermediate files that we generate as a template is created.

??? Quote "Result of `tree ~data/class-fake-class/student-erios` w/ explanation."
    ``` linenums="1" hl_lines="4-8 10-14 24-28 30-34"
        ~data/class-fake-class/student-erios/
        ├── data.yaml
        └── exam-exam
            ├── final-context-output-intro.yaml
            ├── final-context-output-questions[addition-question]-body.yaml
            ├── final-context-output-questions[addition-question]-solution.yaml
            ├── final-context-output-questions[addition-question].yaml
            ├── final-context-output.yaml
            ├── finalize-log.yaml
            ├── initial-context-output-intro.yaml
            ├── initial-context-output-questions[addition-question]-body.yaml
            ├── initial-context-output-questions[addition-question]-solution.yaml
            ├── initial-context-output-questions[addition-question].yaml
            ├── initial-context-output.yaml
            ├── output-log.yaml
            ├── post-finalize-doc.yaml
            ├── post-init-doc.yaml
            ├── post-setup-doc.yaml
            ├── post-template-doc.yaml
            ├── pre-finalize-doc.yaml
            ├── pre-init-doc.yaml
            ├── pre-setup-doc.yaml
            ├── pre-template-doc.yaml
            ├── result-output-intro.tex
            ├── result-output-questions[addition-question]-body.tex
            ├── result-output-questions[addition-question]-solution.tex
            ├── result-output-questions[addition-question].tex
            ├── result-output.tex
            ├── setup-log.yaml
            ├── template-output-intro.jn2.tex
            ├── template-output.jn2.tex
            ├── template-output-questions[addition-question]-body.jn2.tex
            ├── template-output-questions[addition-question].jn2.tex
            ├── template-output-questions[addition-question]-solution.jn2.tex
            ├── template-result.yaml
            └── template-spec.yaml
    ```

    The files relevant to template rendering are highlighted and can be split along
    two axes.

    The first axis, based on the latter half of the filename, corresponds to the
    template being rendered:

      - `*-output.*` : The template for `NewExam` as a whole, the final output of
        the build process.
        - `*-output-intro.*` : The template for `NewExam.intro`, the introduction
          text we specify on lines 2-22 of `exam.py`. (Starting with
          `#!py intro.text = r'''`)
        - `*-output-questions[addition-question].*` : The template for
          `SumQuestion`.
            - `*-output-questions[addition-question]-body.*` : The template we specify
              for `SumQuestion.body` in `addition_question.py` in lines 6-10.
            - `*-output-questions[addition-question]-solution.*` : The template we
              specify for `SumQuestion.solution` in `addition_question.py` in line 12.

    The tree structure here is intentional. Each template can access variables from
    its parents and the parents can use final *post-rendering* results from its
    children.

    The second axis, based on the prefix of the filename, tells us what actual data
    is in the file:

      - `template-*.jn2.tex` : The raw, un-rendered template used for this portion
        of the assignment.
      - `initial-context-*.yaml` : The initial variables available to this template
        before child templates are rendered. These are all made available to child
        templates unless they're overridden by those child templates.
      - `final-context-*.yaml` : These are the variables available to each template
        when they're rendered. **The are the variables you can use in the
        templates**, along with their values for *this particular build*. We'll
        break this down further in a moment.
      - `result-*.tex` : This is final result of each template after the variables
        in `final-context-*.yaml` are applied to `template-*.jn2.tex`.

We can look in `final-context-output-questions[addition-question]-body.yaml` to
see what variables we can use when setting `#!python body.text`.

???+ Quote "Contents of `final-context-output-questions[addition-question]-body.yaml`"
    ```yaml linenums="1"
    assignment: Example Assignment
    author: J. Doe \& B. Smith
    course: TEST 101
    date: 12-12-2012
    format: exam
    index: 0
    name: Basic Addition Question
    nesting_depth: 1
    number: '1'
    numbering_depth: a.
    numbering_scheme: 1a.
    semester: Fall xx
    student:
      Email Address: erios@berkeley.edu
      Name: Rios, Christine
      Student ID: '49232540'
      answer_data: null
      grade_data: null
      ident: erios
      name: Rios, Christine
      root_seed: d6f585da
      score_data: null
      sid: '49232540'
      student_data:
        Email Address: erios@berkeley.edu
        Name: Rios, Christine
        Student ID: '49232540'
        name: Rios, Christine
        sid: '49232540'
        username: erios
      username: erios
    teacher: J. Doe \& B. Smith
    ```

Each of the fields above is available for use in the `body.text` template as
part of the context dictionary passed to our templating engine.

In general, you can refer to the base level variables directly. For example:

  - `#!jinja {{ teacher }}` will use the value on line 32 and be rendered as
    `#!tex J. Doe \& B. Smith`.
  - `#!jinja {{ name }}` refers to the name of the questions and will use the
    value on line 7 to render as `#!tex Basic Addition Question`.

Nested values can be referenced with both attribute notation
`#!jinja {{ foo.bar }}` or item lookup notation `#!jinja {{foo['bar']}}`
when applicable.  For example:

  - `#!jinja {{ student.ident }}` and `#!jinja {{ student['ident'] }}` both
    will render as `#!tex erios` based on line 19.
  - On the other hand, as `#!python "Email Address"` has a space in it, we
    can only use `#!jinja {{ student['Email Address'] }}` to refer to the
    value on line 14. `#!jinja {{ student.Email Address }}` is not syntactically
    valid.

The full explanation on how to refer to context variables is found
[here](https://jinja.palletsprojects.com/en/3.0.x/templates/#variables) along
with a bunch of additional template formatting tools like conditionals, loops,
and basic arithmetic.

## Using `user_setup` to Add New Variables

It'll also be useful to add new variables that our templates can use.
The primary way to do this is by defining a `user_setup` function.

  - Add the following to the end of `addition_question.py`:

    ```python linenums="14"
       def user_setup(self, **kwargs):

           ctxt_vars = dict()

           ctxt_vars['test_vars'] = {
               'test_str': 'Hello, testing \textbf{TESTING}',
               'test_int': 1234
           }

           return ctxt_vars
    ```

    This is the `user_setup` function that can be defined for every `Exam` and
    `Question`, and is the primary way in which all of these elements can be
    customized.

    The `user_setup` function should always return a dictionary with values that
    are then added to the template context.

  - Build a new test with these changes:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    ```

  - There won't be any changes to the actual `.pdf` file, but we can take a
    look at `final-context-output-questions[addition-question]-body.yaml` to
    see a few new lines:

    ```yaml linenums="33"
    test_vars:
      test_int: 1234
      test_str: "Hello, testing \textbf{TESTING}"
    ```

    Meaning we can now use `#!jinja {{ test_vars.test_int }}` and
    `#!jinja {{ text_vars.test_str }}` in our `body` template.

  - So let's try that, by changing our `addition_question.py` as follows:

    ```python linenums="6"
        body.text = r'''
        Hello \texttt{ {{ student['Email Address'] }} },

        Here's some test text {{ test_vars.test_str }}. \\
        And the test integer: ${{test_vars.test_int }}$.
        '''
    ```

  - And building a new test, as usual:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    ```

    !!! ERROR "TODO: Add image of result. Should be in `assets/` already."

  - Whoops, looks like we have some formatting issues. We're not getting proper
    bold text for "TESTING".

    !!! ERROR "TODO: Add image of latex error, should be in `assets/`"

    This is because of the following line:

    ```python linenums="20"
            'test_str': 'Hello, testing \textbf{TESTING}',
    ```

     Python is interpreting `\t` as a tab rather than the literal slash and
     `t` character. We can fix this by making this line a raw string:

    ```python linenums="20"
            'test_str': r'Hello, testing \textbf{TESTING}',
    ```

    !!! ERROR "TODO: Add images of the result, should be in `assets/`"

??? Example "Complete Current `addition_question.py`"
    ```python linenums="1"
    from exam_gen import *

    class SumQuestion(LatexDoc, Question):
        metadata.name = "Basic Addition Question"

        body.text = r'''
        Hello \texttt{ {{ student['Email Address'] }} },

        Here's some test text {{ test_vars.test_str }}. \\
        And the test integer: ${{test_vars.test_int }}$.
        '''

        solution.text = "Placeholder text for the solution of the question."

        def user_setup(self, **kwargs):

            ctxt_vars = dict()

            ctxt_vars['test_vars'] = {
                'test_str': r'Hello, testing \textbf{TESTING}',
                'test_int': 1234
            }

            return ctxt_vars
    ```

## Using the student-specific RNG

One of the key reasons to have this library at all is to allow the creation of
custom exams for each student as well as custom answer keys.

The main way to do this is by using the student specific rng to generate
or permute problems and answers, for a quick example we'll just tweak the user
setup to use the provided rng.

  - First we need to change the definition of `user_setup` to pull out the
    provided random umber generator.

    ```python linenums="16"
        def user_setup(self, rng, **kwargs):
    ```

    Note that the parameter has to be named 'rng' and the value will have type
    `#!python random.Random` (a builtin python type with docs
    [here](https://docs.python.org/3/library/random.html)).

  - And we can then replace our `test_int` variable with a new random one:

    ```python linenums="21"
            'test_int': rng.randint(0,1000)
    ```

    The number generated here is unique to each student and stable through
    multiple runs of the build system. Any fixed sequence of calls to the rng
    will be always product the same outputs for each student.

    !!! ERROR "TODO: Insert example images, shoudl be in `assets/`"

??? Example "Complete Current `addition_question.py`"
    ```python linenums="1"
    from exam_gen import *

    class SumQuestion(LatexDoc, Question):
        metadata.name = "Basic Addition Question"

        body.text = r'''
        Hello \texttt{ {{ student['Email Address'] }} },

        Here's some test text {{ test_vars.test_str }}. \\
        And the test integer: ${{test_vars.test_int }}$.
        '''

        solution.text = "Placeholder text for the solution of the question."

        def user_setup(self, rng, **kwargs):

            ctxt_vars = dict()

            ctxt_vars['test_vars'] = {
                'test_str': r'Hello, testing \textbf{TESTING}',
                'test_int': rng.randint(0,1000)
            }

            return ctxt_vars
    ```

In the next section we'll turn this proof-of-concept into an actual exam
question with some more advanced use of templates and `user_setup`.
