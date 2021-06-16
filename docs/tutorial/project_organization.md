# Project Organization

Right now `polynomial_question.py` is getting messy and needs to be cleaned up
and split into more reasonable pieces.
Future steps of the tutorial will also be easier if the project is set up in
a more reasonable way.

## Moving `polynomial_question.py` into a Sub-Directory

  1. First we'll create a new subdirectory for the problem:

    ```console
    $ mkdir poly_question
    ```

  2. And then move our current `polynomial_question.py` into it:

    ```console
    $ mv polynomial_question.py poly_question/question.py
    ```

  3. Finally we'll change the import statement in `exam.py` to reflect the
    new location of the question:

    ```python linenums="5"
    from poly_question.question import *
    ```

    ??? quote "Complete Current `exam.py`"
        ```python linenums="1"
        #!/usr/bin/env -S pipenv run python3

        from exam_gen import *
        from addition_question import *
        from poly_question.question import *

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
                'poly-question': PolyQuestion
            }

            intro.text = r'''
            \emph{Example Exam Introduction}
            '''

            def user_setup(self, **kwargs):
                pass

        if __name__ == "__main__": run_cli(globals())
        ```

  1. This would be a good time to run the various build commands and ensure
    nothing has changed:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    $ ./exam.py build-solution:fake-class:erios
    ```

## Splitting `poly_question/question.py` into Multiple Files

Even with the creation of a new directory our primary source file is still
cluttered. Let's split it into multiple files for ease of use.

  1. Create a new `poly_question/functions.py` with the following contents:

    ???+ quote "Complete Current `poly_question/functions.py`"
        ```python linenums="1"
        from functools import reduce
        from itertools import zip_longest, dropwhile

        # multiplies a polynomial by x^n
        mul_x = lambda p, n: ([0] * n) + p
        # multiples a polynomial by a constant
        mul_c = lambda p, c: [c * i for i in p]
        # sums two polynomials together
        sum_p = lambda a, b: [i + j for (i,j) in zip_longest(a,b, fillvalue=0)]
        # trims a polynomial of extraneous zeroes
        trim_p = lambda l: reversed(list(dropwhile(lambda x: x == 0, reversed(l))))
        # multiply polynomials together
        mul_p = lambda a, b: reduce(sum_p,[mul_x(mul_c(a,c),d)for(d,c)in enumerate(b)])
        # take a zero and give us the corresponding polynomial factor
        fact_z = lambda z: [- z, 1]
        # take a list of zeros and produce the polynomial
        prod_z = lambda zs: list(trim_p(reduce(mul_p, map(fact_z, zs))))
        ```

  2. Likewise a new `poly_question/graph_question.py` with the following:

    ???+ quote "Complete Current `poly_question/graph_question.py`"
        ```python linenums="1"
        from exam_gen import *
        from .functions import *

        class GraphQuestion(LatexDoc, Question):
            metadata.name = "Graph Question"

            body.text = r'''
            Sketch the polynomial on this graph:
            Placeholder
            '''

            def user_setup(self, rng, **kwargs):
                pass
        ```

    !!! Note ""
        Note how we use a python relative import on line 2, since
        `functions.py` is in the same sub-directory as this file.

        `#!python from poly_question.functions import *` would also work,
        as it's an absolute import specified relative to the root of the
        assignment.

  1. We can similarly split off `poly_question/factor_question.py` with the
    following:

    ???+ quote "Complete Current `poly_question/factor_question.py`"
        ```python linenums="1"
        from exam_gen import *
        from .functions import *

        class FactorQuestion(LatexDoc, Question):
            metadata.name = "Polynomial Factors"

            body.text = r'''
            What are its factors?
            '''

            solution.text = r'''
            The factors are:

            $${%- for factor in factors.values() -%}
            {
              {%- if factor.has_term -%}
                \left( x {{ factor.sign }} {{ factor.num }} \right)
              {%- else -%}
                x
              {%- endif -%}
            }
              {%- if factor.degree != 1 -%}
                 ^{ {{factor.degree}} }
              {%- endif -%}
            {%- endfor -%}
            $$
            '''

            def user_setup(self, ctxt, rng, **kwargs):

                # Format the factors so that they're also easier to print
                print_factors = dict()

                # the `zeros` value returned by the parent question is found here
                # in the `ctxt` parameter under `ctxt['zeroes']`
                for z in ctxt['zeros']:
                    if z not in print_factors:
                        print_factors[z] = {
                              'zero': z,
                              'degree': 1,
                              'has_term': z != 0, # do we even print a constant term?
                              'sign': "+" if z < 0 else "-",
                              'num': abs(z)
                            }
                    else:
                        print_factors[z]['degree'] += 1

                return {"factors": print_factors}
        ```

  1. Next remove `GraphQuestion` and `PolyQuestion` from
    `poly_question/question.py`.

  1. Instead we will import them from their new locations, with the following:

    ```python linenums="1"
    from exam_gen import *
    from .functions import *
    from .graph_question import *
    from .factor_question import *
    ```

    ??? quote "Complete Current `poly_question/question.py`"
        ```python linenums="1"
        from exam_gen import *
        from .functions import *
        from .graph_question import *
        from .factor_question import *

        class PolyQuestion(LatexDoc, Question):
            metadata.name = "Polynomial Question"

            body.text = r'''
            For the following polynomial:

            $$
            {%- for term in poly -%}
              {%- if not loop.first -%}{{term.sign}}{%- endif -%}
              { {{term.num}}{%- if term.degree != 0 -%}x{%- endif -%} }
              {%- if term.degree > 1 -%}^{ {{term.degree}} }{%- endif -%}
            {%- endfor -%}
            $$
            '''

            questions = {
                'graph': GraphQuestion,
                'factors': FactorQuestion
            }

            def user_setup(self, rng, **kwargs):

                # Make a list of 4 random integers, the zeros of our polynomial
                zeros = list(map(lambda _: rng.randint(-5,5), range(0,4)))

                # The polynomial such that each index is the coefficient of the
                # corresponding term.
                # (i.e. the polynomial is `poly[0] + poly[1]x + poly[2]x^2 ...` for a
                # given list `poly`)
                poly = prod_z(zeros)

                # Reorder the terms so the highest degree is first, and split it out
                # to make the templates easier to write.
                print_poly = list()
                for (degree, coeff) in reversed(list(enumerate(poly))):
                    if coeff != 0:
                        print_poly.append({
                              'degree': degree,
                              'coefficient': coeff,
                              'sign': "-" if coeff < 0 else "+",
                              'num': abs(coeff)
                            })


                return {
                    'poly': print_poly,
                    'zeros': zeros
                }
        ```

  1. Again, this would be a good time to run the various build commands and ensure
    nothing has changed:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    $ ./exam.py build-solution:fake-class:erios
    ```

## Using File Templates

Some of the templates we use in the questions are also proving unwieldy, so
we can move them into files.

  1. Create a file for the `FactorQuestion`'s `solution` variable by placing
    the following into `poly_question/factor_solution.jn2.tex`:

    ???+ quote "Complete Current `poly_question/factor_solution.jn2.tex`"
        ```latex linenums="1"
        The factors are:

        $$
        {%- for factor in factors.values() -%}
        {
          {%- if factor.has_term -%}
            \left( x {{ factor.sign }} {{ factor.num }} \right)
          {%- else -%}
            x
          {%- endif -%}
        }
          {%- if factor.degree != 1 -%}
            ^{ {{factor.degree}} }
          {%- endif -%}
        {%- endfor -%}
        $$
        ```

  1. We can then edit `factor_question.py` to make it use the template file
    rather than the inline code by removing the assignment to `solution.text`
    and replacing it with the following:

    ```python linenums="11"
    solution.file = "factor_solution.jn2.tex"
    ```

    ??? quote "Complete Current `poly_question/factor_question.py`"
        ```python linenums="1"
        from exam_gen import *
        from .functions import *

        class FactorQuestion(LatexDoc, Question):
            metadata.name = "Polynomial Factors"

            body.text = r'''
            What are its factors?
            '''

            solution.file = "factor_solution.jn2.tex"

            def user_setup(self, ctxt, rng, **kwargs):

                # Format the factors so that they're also easier to print
                print_factors = dict()

                # the `zeros` value returned by the parent question is found here
                # in the `ctxt` parameter under `ctxt['zeroes']`
                for z in ctxt['zeros']:
                    if z not in print_factors:
                        print_factors[z] = {
                              'zero': z,
                              'degree': 1,
                              'has_term': z != 0, # do we even print a constant term?
                              'sign': "+" if z < 0 else "-",
                              'num': abs(z)
                            }
                    else:
                        print_factors[z]['degree'] += 1

                return {"factors": print_factors}
        ```

  1. As usual, none of the actual contents of the assignment have changed
    so we can run the build commands to verify things still work:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    $ ./exam.py build-solution:fake-class:erios
    ```

!!! Note "Notes on Template Files"
    - You can use `*.file` anywhere you can use `*.text` to define the text
      of a template field.
        - This includes `intro` and `body`, as well as any other similar
          variables.
    - The library will search for the template file in the following order:
        1. The directory with the question/exam where it's specified.
        2. The directories of each parent question or exam, until it reaches
           the root of project.
        3. The set of templates provided with the `exam_gen` library.

    !!! ERROR "TODO: link to detailed search path description in user guide"
