# Custom Setup and Grading

Here we'll be adding a needlessly complicated problem that shows off a number
of advanced features and ways to interact with the `exam_gen` library.

Students will have to choose an assignment of variables and some constraints
to create a constraint satisfaction problem that meets various conditions.

!!! error "TODO: image in `assets/`"

## Initial Setup

  1. First we can create a new folder for our question and some initial files:

    ```console
    $ mkdir csp_question
    $ touch csp_question/question.py
    $ touch csp_question/exp.py
    $ touch csp_question/small_text.jn2.tex
    ```

  2. `exp.py` will contain some code for manipulating and printing boolean
    formulas. Put the following in `csp_question/exp.py`:

    ??? quote "Complete Current `csp_question/exp.py`"
        ```python linenums="1"
        import attr

        @attr.s
        class Var():
            name = attr.ib()

            def eval(self, vars):
                return _eval_exp(vars.get(self.name, self), vars)

            def print_tex(self):
                return r'\mathit{\mathsf{%s}}' % self.name

            def is_complex(self):
                return False

        @attr.s
        class Not():
            exp = attr.ib()

            def __init__(self, e):
                self.__attrs_init__(e)

            def eval(self, vars):
                val = _eval_exp(self.exp,vars)
                if isinstance(val, bool):
                    return not val
                elif isinstance(val, Not):
                    return val.exp
                else:
                    return val

            def print_tex(self):
                return  r'\neg{%s}' % _print_wrap_tex(self.exp)

            def is_complex(self):
                return False

        @attr.s(init=False)
        class And():
            exps = attr.ib()

            def __init__(self, *cmpnts):
                self.__attrs_init__(cmpnts)

            def eval(self, vars):
                result = list()
                for exp in self.exps:
                    val = _eval_exp(exp, vars)
                    if isinstance(val, bool):
                        if val == False:
                            return False
                    elif isinstance(val, And):
                        result += val.exps
                    else:
                        result.append(val)
                return result if len(self.exps) != 0 else True


            def is_complex(self):
                return len(self.exps) > 1

            def print_tex(self):
                if len(self.exps) == 0:
                    return _print_tex(True)
                elif len(self.exps) == 1:
                    return _print_tex(self.exps[0])
                else:
                    return r' \wedge '.join(map(_print_wrap_tex, self.exps))


        @attr.s(init=False)
        class Or():
            exps = attr.ib()

            def __init__(self, *cmpnts):
                self.__attrs_init__(cmpnts)

            def eval(self, vars):
                result = list()
                for exp in self.exps:
                    val = _eval_exp(exp, vars)
                    if isinstance(val, bool):
                        if val == True:
                            return True
                    elif isinstance(val, Or):
                        result += val.exps
                    else:
                        result.append(val)
                return result if len(self.exps) != 0 else False

            def is_complex(self):
                return len(self.exps) > 1

            def print_tex(self):
                if len(self.exps) == 0:
                    return _print_tex(False)
                elif len(self.exps) == 1:
                    return _print_tex(self.exps[0])
                else:
                    return r' \vee '.join(map(_print_wrap_tex,self.exps))

        def _eval_exp(exp, vars):
            if isinstance(exp, bool):
                return exp
            else:
                exp.eval(vars)

        def _print_tex(exp):
            if isinstance(exp, bool):
                return r'\mathsf{\mathit{%s}}' % ("True" if exp else "False")
            else:
                return exp.print_tex()

        def _print_wrap_tex(exp):
            if isinstance(exp, bool):
                return _print_tex(exp)
            elif exp.is_complex():
                return r'\left(%s\right)' % _print_tex(exp)
            else:
                return _print_tex(exp)
        ```

  1. Next we can initialize `csp_question/question.py` with:

    ???+ quote "Complete Current `csp_question/question.py`"
        ```python linenums="1"
        from exam_gen import *
        from .exp import *

        # Problem Variables
        w = Var("w")
        x = Var("x")
        y = Var("y")
        z = Var("z")

        vars = [w,x,y,z]

        # Problem Constraints
        exps = [ Not(w),
                 Or(x, Not(w)),
                 And(w, Not(Or(x, Not(z))), Or(y, z)),
                 Or(And(x, Not(w), y, Not(z)), And(Not(x), Not(y))),
                 And(Or(x, w, Not(y), Not(z)), Or(Not(w), z, y), Or(Not(x), w, y)),
                 Or( Not(w), x, And(z, Not(w))),
                 Or(y, Not(x))
               ]

        class CspQuestion(LatexDoc, MultipleChoiceQuestion):

            body.text = r'''
            From the options below choose:
            \begin{itemize}
              \item An assignment for \emph{every} variable
              \item At least two constraints
            \end{itemize}

            Such that all chosen constraints are satisfied.

            Extra credit points will be awarded for every constraint above 2 that is
            chosen, but no points will be awarded if even a single chosen constraint
            is not satisfied by the given assignment.
            '''

            # No need to shuffle this problem
            settings.grade.shuffle = False
        ```

  1. Then we can edit `exam.py` to import and use the new question.


    To add the new import:

    ```python linenums="8"
    from csp_question.question import *
    ```

    To add our new question to the question list:

    ```python linenums="20" hl_lines="6"
    questions = {
        'addition-question': SumQuestion,
        'poly-question': PolyQuestion,
        'graph-question': GraphQuestion,
        'matrix-question': MatrixQuestion,
        'csp-question': CspQuestion,
    }
    ```

    ??? quote "Complete Current `exam.py`"
        ```python linenums="1"
        #!/usr/bin/env -S pipenv run python3

        from exam_gen import *
        from addition_question import *
        from poly_question.question import *
        from graph_question.question import *
        from matrix_question.question import *
        from csp_question.question import *

        class NewExam(LatexDoc, Exam):

            classes = {
                'fake-class': Classroom.with_options(
                    roster=BCoursesCSVRoster.with_options(
                        file_name="class-1.csv"
                    )
                ),
            }

            questions = {
                'addition-question': SumQuestion,
                'poly-question': PolyQuestion,
                'graph-question': GraphQuestion,
                'matrix-question': MatrixQuestion,
                'csp-question': CspQuestion,
            }

            intro.text = r'''
            \emph{Example Exam Introduction}
            '''

            def user_setup(self, **kwargs):
                pass

        if __name__ == "__main__": run_cli(globals())
        ```

## Using Custom Question Templates

This question has a lot of options and spills over to multiple pages.
To fix this we'll overload the basic question template with one that has smaller
text.

  1. First we can fill `csp_question/small_text.jn2.tex` with the following:

    ???+ quote "Complete Current `csp_question/small_text.jn2.tex`"
        ```latex linenums="1" hl_lines="10 24"
        {% if nesting_depth == 1 %}
        {\large { Problem: {{ number }} } } \\
        {% elif nesting_depth == 2 %}
        {\large { Sub-problem: {{ number }} } } \\
        {% elif nesting_depth == 3 %}
        {\large { Sub-sub-problem: {{ number }} } } \\
        {% else %}
        {\large { Part: {{ number }} } } \\
        {% endif %}
        {\small
        {{ body.text }} \\
        {% if format == 'solution' %}
        \solution{ {{ solution.text }} } \\
        {% endif %}
        \begin{enumerate}[label=(\alph*)]
        {% for choice in choices %}
        \item {{choice.text}}
        {%- if format == 'solution' %} \\
        \solution{ {{ "correct" if choice.is_correct else "incorrect" }}
        {%- if choice.solution -%} {{ choice.solution }} {%- endif -%} }
        {%- endif -%}
        {%- endfor %}
        \end{enumerate}
        }
        ```

  2. And then override the default template by adding the following to
    `csp_question/question.py`:

    ```python linenums="41"
    # Alternate template so question will render on a single page.
    settings.template.embedded = "small_text.jn2.tex"
    ```

    The `settings.template.embedded` option controls which template is used when
    a question or exam is being rendered *within* another document.

    If we wanted to change the template being used when something is being
    rendered as a *separate, standalone document* we'd edit
    `settings.template.standalone`.

## Setting Up Choices at Runtime (in `user_setup`)

In order to get more control over the printing of choices, or to change them
based on the `rng` and `ctxt`, we will want to manipulate them within the
`user_setup` functions or other functions it calls.

  1. First let's make sure that no error is thrown when we make a number of
    choices and don't mark any as correct. Add the following to `CspQuestion`:

    ```python linenums="44"
    # Due to our custom grading function we won't mark any choices as
    # correct, so we need to supress the check to ensure at least one
    # correct choice
    settings.grade.supress_correct_choice_error = True
    ```

  1. Then we can add a new `user_setup` function to `CspQuestion`:

    ```python linenums="49" hl_lines="7 13"
    def user_setup(self, rng, ctxt):

        # When working with a question's choices or settings at runtime
        # (inside the `user_setup` or other funtions) you can't refer to
        # them directly, instead they're all properties of `self`.
        # See how we use `self.choice` here instead of just `choice`.
        self.choice.total_number = 2 * len(vars) + len(exps)

        choice_exps = dict()

        # Generate choices for each variable assignment
        for (i, v) in enumerate(vars):
            self.choice[2*i].text = r'Variable: $%s$' % (v.print_tex())
            self.choice[2*i + 1].text = r'Variable: $%s$' % (Not(v).print_tex())
            choice_exps |= {2*i: v,2*i+1: Not(v)}

        exp_start = 2 * len(vars)

        # Generate choices for each boolean expression
        for (i, e) in enumerate(exps):
            self.choice[exp_start + i].text = r' Constraint: $%s$' % (
                e.print_tex())
            choice_exps[exp_start + i] = e

        # Return the expressions (for use in `calculate_grade`)
        return {'choice_exps': choice_exps }
    ```

    Note how we use `#!python self` to refer to `choice` and `settings` (like
    in line 55).
    This is standard python-ism, the variables you have access to when defining
    a class are associated with the class as a whole.
    Inside functions you must refer to properties of a specific instance of that
    class via `#!python self`, as functions operate on instances instead of classes.

    Otherwise things work as usual, as with line 61 setting `#!py self.choice[n].text`
    just as we set `#!py choice[n].text` in earlier examples.

    !!! info ""
        `exam_gen` is designed so that while a class represents the general template for
        an exam or question, *each instance is the version of that exam or question that
        is generated for a* **specific** *student*.
        So when some aspect of your question depends on information that is unique to
        each student, like the student's unique `rng`, that needs to be set inside
        a function by way of `#!py self`.

        In general the library is designed to allow the separation of student specific
        information from properties of the question itself (the heavy use of templating
        is a big part of this) but that's not always feasible, hence being able to
        set properties directly.

## Defining a Custom Grading Function

While we'll discuss the autograding feature in more detail in another section,
this is a good place to show how custom grading works for multiple-choice-questions.

!!! error "TODO: link to section."

  1. Initialize some settings by adding the following:

    ```python linenums="76"
    # Specify that we'll be using a custom grading function
    settings.grade.style = "custom"

    # We will award between 0 and 2 points for this problem
    settings.grade.max_points = 2
    ```

  2. Define a `calculate_grade` function as follows:

    ```python linenums="82"
    def calculate_grade(self, ctxt, is_selected):
        # Extract assignments from student choices
        assignments = dict()
        for i in range(0, 2 * len(vars)):
            assignment = ctxt['choice_exps'][i]
            if is_selected[i] and isinstance(assignment, Var):
                assignments[assignment.name] = True
            elif is_selcted[i] and isinstance(assignment, Not):
                assignments[assignment.exp.name] = False

        # Extract Constraints that students chose
        constraints = list()
        for i in range(2 * len(vars), 2* len(vars) + len(exps)):
            if is_selected[i]:
                constraints.append(ctxt['choice_exps'][i])

        # Calculate and return score
        if len(constraints) <= 2:
            return 0 # Not enough contraints chosen
        else:
            score = 0
            for c in constraints:
                if c.eval(assignments) == True:
                    score += 1 # Point per Satisfied Constraint
                else:
                    return 0 # Unsatisfied Constraint = 0 Points
            return score
    ```

    This function is given the user context (`ctxt`) that `user_setup` returned
    earlier and an array (`is_selected`) that tells you whether the student
    selected the corresponding entry in (`choice`).

    `is_selected` is unshuffled before being given to you so each
    `is_selected[n]` corresponds directly to `choice[n]`.

    `calculate_grade` should return the number of points to be given to the
    student. No scaling of the result is done with respect to `max_points` so
    it's possible to give extra-credit this way.


??? quote "Complete Current `csp_question/question.py`"
    ```python linenums="1"
    from exam_gen import *
    from .exp import *

    # Problem Variables
    w = Var("w")
    x = Var("x")
    y = Var("y")
    z = Var("z")

    vars = [w,x,y,z]

    # Problem Constraints
    exps = [ Not(w),
             Or(x, Not(w)),
             And(w, Not(Or(x, Not(z))), Or(y, z)),
             Or(And(x, Not(w), y, Not(z)), And(Not(x), Not(y))),
             And(Or(x, w, Not(y), Not(z)), Or(Not(w), z, y), Or(Not(x), w, y)),
             Or( Not(w), x, And(z, Not(w))),
             Or(y, Not(x))
           ]

    class CspQuestion(LatexDoc, MultipleChoiceQuestion):

        body.text = r'''
        From the options below choose:
        \begin{itemize}
          \item An assignment for \emph{every} variable
          \item At least two constraints
        \end{itemize}

        Such that all chosen constraints are satisfied.

        Extra credit points will be awarded for every constraint above 2 that is
        chosen, but no points will be awarded if even a single chosen constraint
        is not satisfied by the given assignment.
        '''

        # No need to shuffle this problem
        settings.grade.shuffle = False

        # Alternate template so question will render on a single page.
        settings.template.embedded = "small_text.jn2.tex"

        # Due to our custom grading function we won't mark any choices as
        # correct, so we need to supress the check to ensure at least one
        # correct choice
        settings.grade.supress_correct_choice_error = True

        def user_setup(self, rng, ctxt):

            # When working with a question's choices or settings at runtime
            # (inside the `user_setup` or other funtions) you can't refer to
            # them directly, instead they're all properties of `self`.
            # See how we use `self.choice` here instead of just `choice`.
            self.choice.total_number = 2 * len(vars) + len(exps)

            choice_exps = dict()

            # Generate choices for each variable assignment
            for (i, v) in enumerate(vars):
                self.choice[2*i].text = r'Variable: $%s$' % (v.print_tex())
                self.choice[2*i + 1].text = r'Variable: $%s$' % (Not(v).print_tex())
                choice_exps |= {2*i: v,2*i+1: Not(v)}

            exp_start = 2 * len(vars)

            # Generate choices for each boolean expression
            for (i, e) in enumerate(exps):
                self.choice[exp_start + i].text = r' Constraint: $%s$' % (
                    e.print_tex())
                choice_exps[exp_start + i] = e

            # Return the expressions (for use in `calculate_grade`)
            return {'choice_exps': choice_exps }

        # Specify that we'll be using a custom grading function
        settings.grade.style = "custom"

        # We will award between 0 and 2 points for this problem
        settings.grade.max_points = 2

        def calculate_grade(self, ctxt, is_selected):
            # Extract assignments from student choices
            assignments = dict()
            for i in range(0, 2 * len(vars)):
                assignment = ctxt['choice_exps'][i]
                if is_selected[i] and isinstance(assignment, Var):
                    assignments[assignment.name] = True
                elif is_selected[i] and isinstance(assignment, Not):
                    assignments[assignment.exp.name] = False

            # Extract Constraints that students chose
            constraints = list()
            for i in range(2 * len(vars), 2* len(vars) + len(exps)):
                if is_selected[i]:
                    constraints.append(ctxt['choice_exps'][i])

            # Calculate and return score
            if len(constraints) <= 2:
                return 0 # Not enough contraints chosen
            else:
                score = 0
                for c in constraints:
                    if c.eval(assignments) == True:
                        score += 1 # Point per Satisfied Constraint
                    else:
                        return 0 # Unsatisfied Constraint = 0 Points
                return score
    ```

## Finishing Up

 1. Finally generate the new solution key with the following commands:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-solution:fake-class:erios
    ```

    !!! error "TODO: image in `assets/`"
