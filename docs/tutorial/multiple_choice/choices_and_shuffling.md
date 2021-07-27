# Shuffling Question Choices

This time we'll be examining a slightly more complex question where
we want finer grained control of the options presented to the student.

!!! error "TODO: image in `assets/`"

## Initial Setup

  1. First we can create a new file and folder for our question:

    ```console
    $ mkdir matrix_question
    $ touch matrix_question/question.py
    ```

  2. Then, as before, add a basic stub we can expand later. Start by writing
    the following into `matrix_question/question.py`:

    ???+ quote "Complete Current `graph_question/question.py`"
        ```python linenums="1"
        from exam_gen import *

        class MatrixQuestion(LatexDoc, MultipleChoiceQuestion):
            # We're using the nicematrix package to add column labels to our matrix.
            settings.latex.header_includes = r'''
            \usepackage{nicematrix}
            '''

            # Core problem text
            body.text = r'''
            Which pairs of columns on the following matrix are \emph{not} independent?

            \NiceMatrixOptions{code-for-first-row= \color{blue}}
            $$\begin{bNiceMatrix}[first-row]
            C_0 & C_1    & C_2 & C_3 & C_4 \\
            {% for r in range(0,4) -%}
            {%- for c in range(0,5) -%}{{ matrix[c][r] }}
            {%- if not loop.last %} & {% endif %}{% endfor %} \\
            {% endfor %}
            \end{bNiceMatrix}$$

            Choose the single best option.
            '''

            def user_setup(self, rng, ctxt):
                return self.gen_matrix_data(rng)

            def gen_matrix_data(self, rng):
                # Generate some independent cols
                i_cols = [[rng.randint(-20,20) for _ in range(0,4)] for _ in range(0,3)]
                # Pick a few columns for our output matrix
                o_base = rng.sample([0,0,1,1,2], k=5)
                mults = list(range(-3,4))
                mults.remove(0)
                const_mul = lambda : rng.sample(mults,k=1)
                o_cols = [[c * j for j in i_cols[i]] for i in o_base for c in const_mul()]
                # Get our two pairs of dependent columns
                c_ans = [[c for c in range(0,5) if o_base[c] == i] for i in [0,1]]
                # Make an incorrect answer
                i_ans = rng.sample(range(0,5),2)
                while (i_ans in c_ans):
                    i_ans = rng.sample(range(0,5),2)
                # return all that info
                return {
                    'matrix': o_cols,
                    'dependent_cols': c_ans,
                    'independent_col': i_ans
                    }
        ```

    This time we're providing some of the setup code as it's not too relevant
    to the point of this example.

  1. As before, change `exam.py` to include our new question by importing
    the correct file and updating our question list, as follows:

    To add the new import:

    ```python linenums="7"
    from matrix_question.question import *
    ```

    To add our new question to the question list:

    ```python linenums="11" hl_lines="4"
    questions = {
        'addition-question': SumQuestion,
        'poly-question': PolyQuestion,
        'graph-question': GraphQuestion,
        'matrix-question': MatrixQuestion,
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
            }

            intro.text = r'''
            \emph{Example Exam Introduction}
            '''

            def user_setup(self, **kwargs):
                pass

        if __name__ == "__main__": run_cli(globals())
        ```

## Basic Setup

  1. We can start first by setting an alternate style of grading for this
    question. Add the following to `MatrixQuestion`:

    ```python linenums="52"
    # Set the style of grade appropriately
    settings.grade.style = "all_correct"
    ```

    The `#!python "all_correct"` option will only give  a student points for this
    question if the select *all* of the correct choices and none of the incorrect
    ones.
    In this case we're only going to mark a single option as correct, so everything
    functions like a normal multiple choice problem with a single answer.

  2. As before, we're going to stick with `5` total choices. So add:

    ```python linenums="55"
    choice.total_number = 5
    ```

## Differentiating Answer Choices

Before move on, it's worth examining what context we return from `user_setup`
so that we can know what variables are accessible from the choice templates:

  - `matrix`: This is just the base matrix for the problem in `#!python matrix[col][row]` form.
  - `depdendent_cols`: This is a list of pairs of depdendent columns, such that
     for any `i`, `dependent_cols[i][0]` and `dependent_cols[i][1]` are two
     columns who are dependent on each other.
  - `independent_cols`: Is a *single* pair of columns which aren't dependent on
    on each other.

With what we can set each of the choices.

  1. We'll start by setting a default template for all of the choices, basically
    setting the `.text` property for all the options. Add the following:

    ```python linenums="57"
    # Set the default text for all choices
    choice.text = r'''
    $C_{{ dependent_cols[index][0] }}$ and $C_{{ dependent_cols[index][1] }}$
    '''
    ```

    As with the previous problem, we're using `index` here to differentiate
    between each of the available options. For `#!python choice[0]` the `index` is set
    to `#!python 0`, for `#!python choice[1]` it's set to `#!python 1`, and so on.

  2. With the default taken care of, we can set an option for the independent
    column. So set `#!python choice[2]` by adding:

    ```python linenums="62"
    # Set individual choices that the default isn't good for
    choice[2].text = r'''
    $C_{{ independent_col[0] }}$ and $C_{{ independent_col[1] }}$
    '''
    ```

    At this point, we know choice `0` and `1` are correct and `2` is incorrect.

  1. Here's where we'll set up a combined option. Add the following:

    ```python linenums="67"
    # We can use the `choice_letters` variable to refer to other choices
    choice[3].text = r'''
    Both {{ choice_letters[0] }} and {{ choice_letters[1] }}.
    '''
    choice[3].is_correct = True
    ```

    Notice how we use the `#!python choice_letters` variables to turn the
    choice numbers we work with (`0` and `1`) into the letters that students
    taking the exam will see.

    Importantly this works even with shuffling. If you examine multiple
    student exams the letters in this option will be different as the options
    get shuffled around.

  1. Now we can add the obligatory last option:

    ```python linenums="73"
    choice[4].text = r'''
    All of the above
    '''
    ```

  1. Finally we can specify that we should only shuffle the first three options
  with the following:

  ```python linenums="77"
  # Chose which options to shuffle, leave others in their place
  settings.grade.shuffle = [0,1,2]
  ```

  While `#!python True` and `#!python False` turn shuffling on and off globally,
  you can also specify a list of options to shuffle. In this case just the first
  three.

??? quote "Complete Current `matrix_question/question.py`"
    ```python linenums="1"
    from exam_gen import *

    class MatrixQuestion(LatexDoc, MultipleChoiceQuestion):


        # We're using the nicematrix package to add column labels to our matrix.
        settings.latex.header_includes = r'''
        \usepackage{nicematrix}
        '''

        # Core problem text
        body.text = r'''
        Which pairs of columns on the following matrix are \emph{not} independent?

        \NiceMatrixOptions{code-for-first-row= \color{blue}}
        $$\begin{bNiceMatrix}[first-row]
        C_0 & C_1    & C_2 & C_3 & C_4 \\
        {% for r in range(0,4) -%}
        {%- for c in range(0,5) -%}{{ matrix[c][r] }}
        {%- if not loop.last %} & {% endif %}{% endfor %} \\
        {% endfor %}
        \end{bNiceMatrix}$$

        Choose the single best option.
        '''

        def user_setup(self, rng, ctxt):
            return self.gen_matrix_data(rng)

        def gen_matrix_data(self, rng):
            # Generate some independent cols
            i_cols = [[rng.randint(-20,20) for _ in range(0,4)] for _ in range(0,3)]
            # Pick a few columns for our output matrix
            o_base = rng.sample([0,0,1,1,2], k=5)
            mults = list(range(-3,4))
            mults.remove(0)
            const_mul = lambda : rng.sample(mults,k=1)
            o_cols = [[c * j for j in i_cols[i]] for i in o_base for c in const_mul()]
            # Get our two pairs of dependent columns
            c_ans = [[c for c in range(0,5) if o_base[c] == i] for i in [0,1]]
            # Make an incorrect answer
            i_ans = rng.sample(range(0,5),2)
            while (i_ans in c_ans):
                i_ans = rng.sample(range(0,5),2)
            # return all that info
            return {
                'matrix': o_cols,
                'dependent_cols': c_ans,
                'independent_col': i_ans
                }

        # Set the style of grade appropriately
        settings.grade.style = "all_correct"

        choice.total_number = 5

        # Set the default text for all choices
        choice.text = r'''
        $C_{{ dependent_cols[index][0] }}$ and $C_{{ dependent_cols[index][1] }}$
        '''

        # Set individual choices that the default isn't good for
        choice[2].text = r'''
        $C_{{ independent_col[0] }}$ and $C_{{ independent_col[1] }}$
        '''

        # We can use the `choice_letters` variable to refer to other choices
        choice[3].text = r'''
        Both {{ choice_letters[0] }} and {{ choice_letters[1] }}.
        '''
        choice[3].is_correct = True

        choice[4].text = r'''
        All of the above
        '''

        # Chose which options to shuffle, leave others in their place
        settings.grade.shuffle = [0,1,2]
    ```

## Finishing Up

 1. Finally generate the new solution key with the following commands:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-solution:fake-class:erios
    ```

    !!! error "TODO: image in `assets/`"
