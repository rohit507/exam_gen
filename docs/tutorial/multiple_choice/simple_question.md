# Simple Multiple Choice Example

For our first example we'll start with a multiple choice question about
the properties of a graph.

!!! error "TODO: image in `assets/`"

## Initial Setup

  1. First we can create a new file and folder for our question:

    ```console
    $ mkdir graph_question
    $ touch graph_question/question.py
    ```

  2. Then, as before, add a basic stub we can expand later. Start by writing
    the following into `graph_question/question.py`:

    ???+ quote "Complete Current `graph_question/question.py`"
        ```python linenums="1"
        from exam_gen import *

        class GraphQuestion(LatexDoc, MultipleChoiceQuestion):
            pass
        ```
    Note how on line 3 we inherit from `MultipleChoiceQuestion` rather than
    just `Question`, it's this change which gives us access to most of the new
    features we're going to use.

  3. Now we can change `exam.py` to include our new question by importing
    the correct file and updating our question list, as follows:

    To add the new import:

    ```python linenums="6"
    from graph_question.question import *
    ```

    To add our new question to the question list:

    ```python linenums="18" hl_lines="4"
    questions = {
        'addition-question': SumQuestion,
        'poly-question': PolyQuestion,
        'graph-question': GraphQuestion,
    }
    ```

    ??? quote "Complete Current `exam.py`"
        ```python linenums="1"
        #!/usr/bin/env -S pipenv run python3

        from exam_gen import *
        from addition_question import *
        from poly_question.question import *
        from graph_question.question import *

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
            }

            intro.text = r'''
            \emph{Example Exam Introduction}
            '''

            def user_setup(self, **kwargs):
                pass

        if __name__ == "__main__": run_cli(globals())
        ```

  1. Finally run a quick test:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    ```

    Note that, unlike usual, this should produce an error:

    ???+ example "Result of `./exam.py build-exam:fake-class:erios`"
        Note that your exact output may differ slightly.

        ```console hl_lines="20"
        $ ./exam.py build-exam:fake-class:erios
        .  build-exam:fake-class:erios
        TaskError - taskid:build-exam:fake-class:erios
        PythonAction Error
        Traceback (most recent call last):
          File "~/.local/share/virtualenvs/example_exam-B_yRD-c_/lib/python3.9/site-packages/doit/action.py", line 437, in execute
            returned_value = self.py_callable(*self.args, **kwargs)
          File "~/Workspace/exam_gen/exam_gen/build/loader/build_tasks.py", line 169, in build_exam
            setup_exam(exam_obj, build_info)
          File "~/Workspace/exam_gen/exam_gen/build/loader/build_tasks.py", line 57, in setup_exam
            setup_log['children'] = exam_obj.on_children(
          File "~/Workspace/exam_gen/exam_gen/property/document.py", line 99, in on_children
            log[name] = (fun(question), question.on_children(fun))
          File "~/Workspace/exam_gen/exam_gen/build/loader/build_tasks.py", line 58, in <lambda>
            lambda n: n.setup_build(build_info))
          File "~/Workspace/exam_gen/exam_gen/question/multiple_choice.py", line 198, in setup_build
            self.validate_settings()
          File "~/Workspace/exam_gen/exam_gen/question/multiple_choice.py", line 388, in validate_settings
            raise RuntimeError("Question has no correct answers.")
        RuntimeError: Question has no correct answers.
        ```
    This is because the `MultipleChoiceQuestion` class adds a number of checks
    against common mistakes, in this case a question that doesn't have any
    correct answers.

## Options for Multiple Choice Questions

We'll start by looking at some of the core settings available to the
`MultipleChoiceQuestion` class. Keep in mind that these are only a subset of
what's available with more visible in <>.

!!! Error "Replace <> with link to appropriate user guide page"

  1. Add the following to the definition for `GraphQuestion`:

    ```python linenums="5"
    # Ensure we have the latex libraries we need
    settings.latex.header_includes = r"""
    \usepackage{tikz}
    \usetikzlibrary{shapes, decorations, patterns, arrows, chains,
      fit, calc, positioning}
    """
    ```

    This option, `settings.latex.header_includes`, is actually from `LatexDoc`
    and allows you to specify packages that ought to be imported and other
    commands to place in the header area (before `#!latex \begin{document}`) of
    the final latex document.

    Note that the final `.tex` file will have all the header includes from all
    sub-documents without filtering out duplicates.

  1. Specify the maximum number of points that this question is assigned in
    the exam by adding:

    ```python linenums="12"
    # Set the number of points for this problem
    settings.grade.max_points = 2
    ```

    !!! error "TODO: link to user_guide with further detail"

  1. Specify the grading style for this question by adding:

    ```python linenums="15"
    # Set the style of grade appropriately
    settings.grade.style = "percent_correct"
    ```

    The `#!python "percent_correct"` option will, when we introduce auto-grading
    in more detail, grade students on how many options they correctly
    categorized. So they get credit for options they correctly marked as true
    as ones they correctly marked as false.

    !!! error "TODO: link to user_guide with further detail"

  1. Next we can tell the library to shuffle the available choices by adding:

    ```python linenums="18"
    # Chose which options to shuffle
    settings.grade.shuffle = True
    ```

    This will just randomize the positions of all the options presented to the
    student. Setting this variable to `False` will leave their order unchanged.

    !!! error "TODO: link to user_guide with further detail"


## Question Body and Context

  1. The body of the problem, to be added to `GraphQuestion`:

    ```python linenums="21"
    # Set the problem
    body.text = r'''
    We define a mask of a bipartite graph as a set of vertices in one
    bi-partition whose edges connect to \emph{all} the vertices in the
    other bi-partition.

    \begin{center}
    \begin{tikzpicture}[thick,
      every node/.style={draw, circle, fill, inner sep=1.5pt},
      shorten >= 3pt,shorten <= 3pt
    ]

    \begin{scope}[start chain=going below,node distance=7mm]
    \foreach \i in {1,2,...,6}
      \node[on chain] (l\i) [label=left: $l_\i$] {};
    \end{scope}

    \begin{scope}[xshift=4cm,yshift=-0.5cm,start chain=going below,node distance=7mm]
    \foreach \i in {1,2,...,5}
      \node[on chain] (r\i) [label=right: $r_\i$] {};
    \end{scope}

    {% for (ln, rn) in edges %}
    \draw (l{{ln}}) -- (r{{rn}});
    {% endfor %}

    \end{tikzpicture}
    \end{center}

    Which of the following options are valid masks of the above graph?
    Choose all correct answers.
    '''
    ```

    This expects a list of left-right pairs names `edges` as part of the context.

    Note how we're using the `tikz` Latex library here, hence our need to add it
    to the `header_includes` from earlier.

  1. Next we add a quick helper function to take a premade graph and some possible
    choices for the question and permute the various vertices involved.

    ```python linenums="54"
    def gen_bigraph(self, rng):
        # We're just going to shuffle the vertices on a fixed bi-graph
        l_verts, r_verts = (6, 5)
        edges = [(1,2), (1,4), (2,1), (2,3), (3,5), (4,2), (4,4),
                 (5,3), (6,3), (6,4), (6,5)]
        masks = [('l',6,2,1),('l',2,4,6),('l',1,4,3),('r',2,3,5),('r',4,3,5)]
        non_masks = [('l',5,4,2), ('l',5,6,2),('r',1,4,5)]

        permute_l = {k+1:v for (k,v) in enumerate(rng.sample(range(1,l_verts+1),l_verts))}
        permute_r = {k+1:v for (k,v) in enumerate(rng.sample(range(1,r_verts+1),r_verts))}

        def permute_mask(side, a, b, c):
            permute = permute_l if side == 'l' else permute_r
            verts = sorted([permute[v] for v in [a,b,c]])
            return (side, verts[0], verts[1], verts[2])

        return {'edges': [(permute_l[l], permute_r[r]) for (l,r) in edges]
               ,'masks': [permute_mask(*m) for m in masks]
               ,'non_masks': [permute_mask(*m) for m in non_masks]
        }
    ```

    The three return value are:
      - `'edges'`: The list of pairs as expected by the body template
      - `'masks'`: Possible correct answers to the question
      - `'non-masks'`: Possible incorrect answers to the question

  1. We also need to add a `user_setup` function that will get the appropriate
    results from `gen_bigraph` and format them into a nicer context.

    ```python linenums="75"
    def user_setup(self, rng, ctxt):

        graph_data = self.gen_bigraph(rng)

        masks = rng.sample(graph_data['masks'], 3)
        non_masks = rng.sample(graph_data['non_masks'], 2)

        return {
            'edges': graph_data['edges'],

            # Concat correct and incorrect answers, so correct ones are in
            # indices [0,1,2] and incorrect ones are in [3,4]
            'potential_masks': masks + non_masks,
        }
    ```

## Specifying Choices

The key to manipulating choices in a `#!python MultipleChoieQuestion` is the
`#!python choice` variable. (`#!python self.choice` if you're in `user_setup` or
another function.)

  1. Add the following to `GraphQuestion` to specify that there are 5 total
    options for students to choose from:

    ```python linenums="90"
    choice.total_number = 5
    ```

    The `choice.total_number` variables lets you which you specify how many
    different choices are provided for the question. In general one ought
    set this first, before trying to manipulate any choices directly.

  2. Next we can set the actual text for all the choice by adding:

    ```python linenums="92"
    choice.text = r'''
    ${% for i in [1,2,3] -%}
    {{potential_masks[index][0]}}_{{potential_masks[index][i]}}
    {%- if not loop.last -%}, {% endif -%}
    {%- endfor %}$
    '''
    ```

    When used like this `choice` works like `body` or `solution`, where you
    can assign templates as either a raw string (via `choice.text`) or as
    as pointer to a file (via `choice.file`).

    This particular version, where we're assigning a template to all the choices
    at once adds a special variable called `index`.
    The `index` variable will have the value `0` when called for choice `0`,
    `1` for choice `1`, and so on..

    Here we index into the list `potential_masks`, that we created in
    `user_setup`, to get each separate option for the problem.

  1. Finally we need to specify which options are correct by adding:

    ```python linenums="99"
    for i in [0,1,2]:
        choice[i].is_correct = True
    ```

    The `is_correct` property of a choice is how you an specify whether the
    system should see it as true or false.

    Also note how we can index into the choices as if they were a list, as
    with `#!python choice[i]` here, and work with each of them individually.
    This also works with other parameters like `#!python choice[i].text` but
    the next section of the tutorial will examine that in more depth.


??? quote "Complete Current `graph_question/question.py`"
    ```python linenums="1"
    from exam_gen import *

    class GraphQuestion(LatexDoc, MultipleChoiceQuestion):

        # Ensure we have the latex libraries we need
        settings.latex.header_includes = r"""
        \usepackage{tikz}
        \usetikzlibrary{shapes, decorations, patterns, arrows, chains,
          fit, calc, positioning}
        """

        # Set the number of points for this problem
        settings.grade.max_points = 2

        # Set the style of grade appropriately
        settings.grade.style = "percent_correct"

        # Chose which options to shuffle
        settings.grade.shuffle = True

        # Set the problem
        body.text = r'''
        We define a mask of a bipartite graph as a set of vertices in one
        bi-partition whose edges connect to \emph{all} the vertices in the
        other bi-partition.

        \begin{center}
        \begin{tikzpicture}[thick,
          every node/.style={draw, circle, fill, inner sep=1.5pt},
          shorten >= 3pt,shorten <= 3pt
        ]

        \begin{scope}[start chain=going below,node distance=7mm]
        \foreach \i in {1,2,...,6}
          \node[on chain] (l\i) [label=left: $l_\i$] {};
        \end{scope}

        \begin{scope}[xshift=4cm,yshift=-0.5cm,start chain=going below,node distance=7mm]
        \foreach \i in {1,2,...,5}
          \node[on chain] (r\i) [label=right: $r_\i$] {};
        \end{scope}

        {% for (ln, rn) in edges %}
        \draw (l{{ln}}) -- (r{{rn}});
        {% endfor %}

        \end{tikzpicture}
        \end{center}

        Which of the following options are valid masks of the above graph?
        Choose all correct answers.
        '''

        def gen_bigraph(self, rng):
            # We're just going to shuffle the vertices on a fixed bi-graph
            l_verts, r_verts = (6, 5)
            edges = [(1,2), (1,4), (2,1), (2,3), (3,5), (4,2), (4,4),
                     (5,3), (6,3), (6,4), (6,5)]
            masks = [('l',6,2,1),('l',2,4,6),('l',1,4,3),('r',2,3,5),('r',4,3,5)]
            non_masks = [('l',5,4,2), ('l',5,6,2),('r',1,4,5)]

            permute_l = {k+1:v for (k,v) in enumerate(rng.sample(range(1,l_verts+1),l_verts))}
            permute_r = {k+1:v for (k,v) in enumerate(rng.sample(range(1,r_verts+1),r_verts))}

            def permute_mask(side, a, b, c):
                permute = permute_l if side == 'l' else permute_r
                verts = sorted([permute[v] for v in [a,b,c]])
                return (side, verts[0], verts[1], verts[2])

            return {'edges': [(permute_l[l], permute_r[r]) for (l,r) in edges]
                   ,'masks': [permute_mask(*m) for m in masks]
                   ,'non_masks': [permute_mask(*m) for m in non_masks]
            }

        def user_setup(self, rng, ctxt):

            graph_data = self.gen_bigraph(rng)

            masks = rng.sample(graph_data['masks'], 3)
            non_masks = rng.sample(graph_data['non_masks'], 2)

            return {
                'edges': graph_data['edges'],

                # Concat correct and incorrect answers, so correct ones are in
                # indices [0,1,2] and incorrect ones are in [3,4]
                'potential_masks': masks + non_masks,
            }

        choice.total_number = 5

        choice.text = r'''
        ${% for i in [1,2,3] -%}
        {{potential_masks[index][0]}}_{{potential_masks[index][i]}}
        {%- if not loop.last -%}, {% endif -%}
        {%- endfor %}$
        '''

        for i in [0,1,2]:
            choice[i].is_correct = True

    ```

## Final Testing

 1. We can then generate the new solution key with the following commands:

    !!! info ""
        We're using `acelderon` instead of `erios` this time, in order to
        make the shuffling of the choices more evident.

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-solution:fake-class:acalderon
    ```

    !!! error "TODO: image in `assets/`"
