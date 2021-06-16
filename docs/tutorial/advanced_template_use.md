# Advanced Template Use

In this section of the tutorial we'll be fleshing out our implementation of
`SumQuestion` and turning it into something that could plausibly be in an
assignment.

## Generating Problem Parameters

We're going to give each student a randomized addition problem where
they have to sum up 5 numbers.

  1. We can start generating the variables for a problem by adding the following
    to `addition_question.py`:

    ```python linenums="26"
    def generate_question_params(self, rng):

        result = dict()

        # How many numbers will the student have to sum up?
        num_vars = 4

        # Generate each element
        var_list = list()
        for ind in range(0, num_vars):
            var_list.append(rng.randint(0,20))

        # return the parameters for the problem
        return {'vars': var_list,
                'num_vars': num_vars,
                'total': sum(var_list)
        }
    ```

  1. On its own, the above does nothing so let's make sure that we get the
    results of `generate_question_params` into the context available for our
    template variables by adding the following to `user_setup`:

    ```python linenums="24"
       ctxt_vars['problem'] = self.generate_question_params(rng)
    ```

    ??? Quote "Complete Current `addition_question.py`"
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

                ctxt_vars['problem'] = self.generate_question_params(rng)

                return ctxt_vars

            def generate_question_params(self, rng):

                result = dict()

                # How many numbers will the student have to sum up?
                num_vars = 4

                # Generate each element
                var_list = list()
                for ind in range(0, num_vars):
                    var_list.append(rng.randint(0,20))

                # return the parameters for the problem
                return {'vars': var_list,
                        'num_vars': num_vars,
                        'total': sum(var_list)
                }
        ```

  - Then we can run our usual build command:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    ```

  - The new lines in `final-context-output-questions[addition-question]-body.yaml`
    show that we've managed to correctly add new variables to the
    template:

    ```yaml linenums="12"
    problem:
      num_vars: 4
      total: 33
      vars:
      - 1
      - 14
      - 6
      - 12
    ```

## Generating Solution Keys

  1. That isn't enough to actually display our problem in the test itself.
    For that we need to edit the templates in `addition_question.py`:

    ```python linenums="6"
    body.text = r'''
    Solve the following equation:

       $${{ problem.vars[0] }} + {{ problem.vars[1] }} +
         {{ problem.vars[2] }} + {{ problem.vars[3] }} = \_\_$$
    '''

    solution.text = " The total is {{ problem.total }}."
    ```

  1. With those changes we can run our usual build command and look at the
    resulting pdf:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    ```

    !!! Error "TODO: add images, should be `assets/cust_and_rand_part5`"

  1. We can also generate the solution key with the following command:

    ```console
    $ ./exam.py build-solution:fake-class:erios
    ```

    And look at the result in `~out/exam_solution/class-fake-class/erios.pdf`:

    !!! Error "TODO: Add image `assets/aut_and_rand_part5_sols`"

## Loops in Templates

We can have more complex operations in the templates themselves like allowing
variability in the number of variables in each equation or the number of
equations in total.

  1. Let's first change the number of variables in the each equation by
    editing the following line in `generate_question_params`:

    ```python linenums="33"
    num_vars = rng.randint(3,8)
    ```

  1. Now our template can't handle the full length of the problem, so let's use
    some of [jinja2's for loops](https://jinja.palletsprojects.com/en/3.0.x/templates/#for)
    to make this work:

    ```python linenums="6"
    body.text = r'''
    Solve the following equation:

       $${% for v in problem.vars -%}{{ v }}
         {%- if not loop.last %} + {% endif -%}
         {%- endfor %} = \_\_$$
    '''
    ```

    ??? Info "Template Constructs"

        - Control flow statements like `if` and `for` are usually found within
          `#!jinja2 {%` and `#!jinja2 %}`, unlike printed statements which are found within `{{` and `}}`
        - Within a loop it's possible to access the `loop` magic variable, which can
          be used to determine whether you should print a separator like `+` here.
        - Dashes at the beginning or end of jinja statements, like `{%-` or `-%}`
          are used to delete whitespace. Here we use them to prevent printing
          unnessesary newlines.

  1. We can then build the exam and solutions with these changes:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    $ ./exam.py build-solutions:fake-class:erios
    ```

    !!! Error "TODO: images are in `assets/`"

## Nesting and Complex Problem Structure

We can even build a more complex problem by multiplying the number of
sub-problems. You should probably not do this in an actual assignment.

  1. Generate multiple sub-problems by modifying `user_setup`:

    ```python linenums="20"
    def user_setup(self, rng, **kwargs):

        ctxt_vars = dict()
        ctxt_vars['problem'] = list()
        ctxt_vars['total'] = 0

        for i in range(0,10):
            sub = self.generate_question_params(rng)
            ctxt_vars['problem'].append(sub)
            ctxt_vars['total'] += sub['total']

        return ctxt_vars
    ```

  2. Then we can tweak the templates by adding another loop:

    ```python linenums="6"
    body.text = r'''
    Solve the following equations:

    {% for eq in problem %}
       $${% for v in eq.vars -%}{{ v }}
         {%- if not loop.last %} + {% endif -%}
         {%- endfor %} = \_\_$$
    {% endfor %}

    What is the sum of all of their answers?
    '''

    solution.text = " The total is {{ total }}."
    ```

??? Quote "Complete Current `addition_question.py`"
    ```python linenums="1"
    from exam_gen import *

    class SumQuestion(LatexDoc, Question):
        metadata.name = "Basic Addition Question"

        body.text = r'''
        Solve the following equations:

        {% for eq in problem %}
           $${% for v in eq.vars -%}{{ v }}
             {%- if not loop.last %} + {% endif -%}
             {%- endfor %} = \_\_$$
        {% endfor %}

        What is the sum of all of their answers?
        '''

        solution.text = " The total is {{ total }}."

        def user_setup(self, rng, **kwargs):

            ctxt_vars = dict()
            ctxt_vars['problem'] = list()
            ctxt_vars['total'] = 0

            for i in range(0,10):
                sub = self.generate_question_params(rng)
                ctxt_vars['problem'].append(sub)
                ctxt_vars['total'] += sub['total']

            return ctxt_vars

        def generate_question_params(self, rng):

            result = dict()

            # How many numbers will the student have to sum up?
            num_vars = rng.randint(4,8)

            # Generate each element
            var_list = list()
            for ind in range(0, num_vars):
                var_list.append(rng.randint(0,20))

            # return the parameters for the problem
            return {'vars': var_list,
                    'num_vars': num_vars,
                    'total': sum(var_list)
            }
    ```

  1. As usual, we can build our exams and look at the results:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    $ ./exam.py build-solutions:fake-class:erios
    ```

    !!! Error "TODO: Add images from `assets/`"

## Advanced Solution Text

Now, the current solution key isn't as useful as it could be. In part because
it doesn't tell us the different answers to each sub-problem. There are
two ways to fix this, in the template itself or setting different versions of
the template variable.

### Using Library Level Formats

The is a library level mechanism for switching out
template variables. You can index into template variables like `body`, `solution`
or `intro` with the same syntax used for dictionaries. Each format lets you
directly set the parameter for that format.

For instance setting `#!python body['exam'].text` defines the template when
we're building exams, and `#!python body['solution'].text` defines the template
when building a solution.

  1. For example we could change `body.text` in `addition_question.py` to read:

    ```python linenums="6" hl_lines="1 13"
    body['exam'].text = r'''
    Solve the following equations:

    {%- for eq in problem -%}
       $${% for v in eq.vars -%}{{ v }}
         {%- if not loop.last %} + {% endif -%}
         {%- endfor %} = \_\_$$
    {%- endfor -%}

    What is the sum of all of their answers?
    '''

    body['solution'].text = r'''
    Solve the following equations:

    {%- for eq in problem -%}
       $${% for v in eq.vars -%}{{ v }}
         {%- if not loop.last %} + {% endif -%}
         {%- endfor %} = \solution{ {{ eq.total }} }$$
    {%- endfor -%}

    What is the sum of all of their answers?
    '''
    ```

  2. And then build our solution key to get:

    ```console
    $ ./exam.py build-solutions:fake-class:erios
    ```

    !!! Error "Todo: image in `assets/`"

### Detecting Exam Format in Templates

Another way to detect whether this is a solution or not is to look at the
`format` variable using the template itself. It will be set to
`#!python 'exam'` if we're building in exam form and `#!python 'solution'`
if we're building a solution key.

  1. For instance we could change `body.text` in `addition_question.py` to read:

    ```python linenums="6" hl_lines="4"
    body.text = r'''
    Solve the following equations:

    {%- if format == 'solution' -%}
    {%- for eq in problem -%}
       $${% for v in eq.vars -%}{{ v }}
         {%- if not loop.last %} + {% endif -%}
         {%- endfor %} = \solution{ {{ eq.total }} }$$
    {%- endfor -%}
    {%- else -%}
    {%- for eq in problem -%}
       $${% for v in eq.vars -%}{{ v }}
         {%- if not loop.last %} + {% endif -%}
         {%- endfor %} = \_\_$$
    {%- endfor -%}
    {%- endif -%}

    What is the sum of all of their answers?
    '''
    ```

  1. And then build our solution key to get:

    ```console
    $ ./exam.py build-solutions:fake-class:erios
    ```

    !!! Error "Todo: image in `assets/`"

!!! Note ""
    It's also possible to use LaTeX macros to do this, `#!latex \solution{}` is
    one such mechanism, but that's easier to mess up. Changes to the LaTeX
    templates being used at the document and question level are more likely
    to have solution information being improperly shown. Better to avoid having
    the solutions appearing in the raw `.tex` files at all.
