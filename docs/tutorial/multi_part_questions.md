# Multi-Part Questions

Now we'll take a look at multi-part questions as well as some advanced features
of the `exam_gen` library.

## Initial Setup

Let's first set up a new question for this section of the tutorial.

  1. Create a new file `polynomial_question.py` with the following contents:

    ```python linenums="1"
    from exam_gen import *

    class PolyQuestion(LatexDoc, Question):
        metadata.name = "Polynomial Question"

        body.text = r'''
        For this polynomial: Placeholder Text
        '''

        def user_setup(self, rng, **kwargs):
            pass
    ```

  1. And edit the `questions` variable in `exam.py` so that it reads as follows:

    ```python linenums="17" hl_lines="3"
        questions = {
            'addition-question': SumQuestion,
            'poly-question': PolyQuestion
        }
    ```

    ??? quote "Complete Current `exam.py`"
        ```python linenums="1" hl_lines="19"
        #!/usr/bin/env -S pipenv run python3

        from exam_gen import *
        from addition_question import *
        from polynomial_question import *

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

  1. From there we can build the exam and see the new question:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    ```

    !!! ERROR "Todo: image in `assets/`"

## Adding Sub-Questions

Now we can add some placeholders for the subquestions as well.

  1. Edit `polynomial_question.py` by adding the following before the
     declaration of `#!python PolyQuestion`:

     ```python linenums="3"
     class GraphQuestion(LatexDoc, Question):
         metadata.name = "Graph Question"

         body.text = r'''
         Sketch the polynomial on this graph:
         Placeholder
         '''

         def user_setup(self, rng, **kwargs):
             pass

     class FactorQuestion(LatexDoc, Question):
         metadata.name = "Polynomial Factors"

         body.text = r'''
         What are its factors?
         '''

         def user_setup(self, rng, **kwargs):
             pass
     ```

    !!! Note ""
        This has to come before the line with `#!python class PolyQuestion(..):`
        due to how python loads classes. Both `GraphQuestion` and
        `FactorQuestion` need to already exist before we define `PolyQuestion`.

  1. As well as adding a `questions` variables (just like in `exam.py`) to
     `#!python PolyQuestion` as follows:

     ```python linenums="31"
     questions = {
         'graph': GraphQuestion,
         'factors': FactorQuestion
     }
     ```

    ??? Quote "Complete Current `polynomial_question.py`"

        ```python linenums="1"
        from exam_gen import *

        class GraphQuestion(LatexDoc, Question):
            metadata.name = "Graph Question"

            body.text = r'''
            Sketch the polynomial on this graph:
            Placeholder
            '''

            def user_setup(self, rng, **kwargs):
                pass

        class FactorQuestion(LatexDoc, Question):
            metadata.name = "Polynomial Factors"

            body.text = r'''
            What are its factors?
            '''

            def user_setup(self, rng, **kwargs):
                pass

        class PolyQuestion(LatexDoc, Question):
            metadata.name = "Polynomial Question"

            body.text = r'''
            For the following polynomial: Placeholder Text
            '''

            questions = {
                'graph': GraphQuestion,
                'factors': FactorQuestion
            }

            def user_setup(self, rng, **kwargs):
                pass
        ```

  1. From there we can build the exam and see the new question:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    ```

    !!! ERROR "Todo: image in `assets/`"

## Generating Problem Data in the Parent

For this question to work, both the subquestions need to refer to the same
polynomial. We can't generate a new one for each section. This is where
the other use of `user_setup` comes in.

In addition to providing variables to templates those variables are made
available to child problems as well.

  1. To start, we're just going to add some imports and a few functions that
    let us manipulate polynomials. The exact contents aren't particularly
    important for this tutorial, so don't worry too much about them.

    For now add the following to the start of `polynomial_question.py`:

    ???+ Example "Support Code"
    ```python linenums="2"
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

  1. Using those helpers we can then write the start of our `user_setup` for
    the problem as a whole. So add the following to `polynomial_question.py`:

    ```python linenums="61" hl_lines="27"
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

    The latter half of that code just unpacks the terms of the polynomial so
    that the template can access them under the `poly` variable.

    Also important is the highlighted line, where we add the list of zeroes
    to the context. Our child questions will be able to access the full context
    we return here (just as the template can) so anything they need to know
    should be stuffed in there as well.

  1. Finally, we can make use of those reformatted polynomial variables in
    our template by changing `body.text`:

    ```python linenums="44"
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
    ```

    ??? Quote "Complete Current `polynomial_question.py`"

        ```python linenums="1"
        from exam_gen import *
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

        class GraphQuestion(LatexDoc, Question):
            metadata.name = "Graph Question"

            body.text = r'''
            Sketch the polynomial on this graph:
            Placeholder
            '''

            def user_setup(self, rng, **kwargs):
                pass

        class FactorQuestion(LatexDoc, Question):
            metadata.name = "Polynomial Factors"

            body.text = r'''
            What are its factors?
            '''

            def user_setup(self, rng, **kwargs):
                pass

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

  1. Build the current version of exam with:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    ```

    !!! Error "TODO: immage in `assets/`"

## Using Problem Data in the Children

This gives us the setup of the problem but the sub-problems, especially
`FactorQuestion`, need to know information generated in the parent in order
to render.

In this case, there's a `ctxt` parameter made available to `user_setup` that
contains all the data returned by the `user_setup` of the parent.

  1. We will need to print a nicer form of the factored polynomial based on
     the zeroes of that polynomial.

     Edit the `user_setup` of `FactorQuestion` as follows:

     ```python linenums="38"
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

     Now how in the declaration for `user_setup` we have an additional parameter
     `ctxt`. That we can use to get values from the parent question.

  1. We also need to change the solution template to use the newly generated
    values by editing `polynomial_question.py`:

    ```python linenums="38"
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
    ```

    ??? Quote "Complete Current `polynomial_question.py`"

        ```python linenums="1"
        from exam_gen import *
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

        class GraphQuestion(LatexDoc, Question):
            metadata.name = "Graph Question"

            body.text = r'''
            Sketch the polynomial on this graph:
            Placeholder
            '''

            def user_setup(self, rng, **kwargs):
                pass

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

 1. We can then generate the new solution key with the following commands:
   ```console
   $ ./exam.py cleanup
   $ ./exam.py build-solution:fake-class:erios
   ```

   !!! error "TODO: image in `assets/`"

In the next section we'll see how problems can use images and graphs, as well
as external files and libraries in general.
