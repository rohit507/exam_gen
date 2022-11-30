# External and Generated Assets

With the project reorganized we can start adding external assets to our
assignment, as well as generating new assets on the fly with python libraries
we import.

## Adding an External File

`GraphQuestion` needs an empty graph for the students to use, so let's add one.

  1. Copy the image below into `poly_question/empty_grid.png`:

    !!! error "TODO: image is [https://rohit507.github.io/exam_gen/tutorial/assets/empty_grid.png]"



  2. Change the template for `GraphQuestion` to read as follows:

    ```python linenums="7"
    body.text = r'''
    Sketch the polynomial on this graph:

    \includegraphics[width=\textwidth]{empty_grid.png} \\ ~ \\
    '''
    ```

  1. Add `empty_grid.png` to the list of assets used by this sub-question:

    ```python linenums="13"
    settings.assets = ["empty_grid.png"]
    ```

    ??? quote "Complete Current `poly_question/graph_question.py`"
        ```python linenums="1"
        from exam_gen import *
        from .functions import *

        class GraphQuestion(LatexDoc, Question):
            metadata.name = "Graph Question"

            body.text = r'''
            Sketch the polynomial on this graph:

            \includegraphics[width=\textwidth]{empty_grid.png} \\ ~ \\
            '''

            settings.assets = ["empty_grid.png"]

            def user_setup(self, rng, **kwargs):
                pass
        ```

  1. We can now build the exam to see the grid:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    ```

    !!! error "TODO: image in `assets/`"

Files specified in `settings.assets` will be copied into the build directory
of the exam. This can include glob patterns, though the library will throw an
error if there's not at least one valid file per glob pattern.

??? example "Result of `tree ~build/class-fake-class/student-erios/exam-exam/`"
    ```tree hl_lines="2"
    ~build/class-fake-class/student-erios/exam-exam/
    ├── empty_grid.png
    ├── output.aux
    ├── output-intro.tex
    ├── output.log
    ├── output.out
    ├── output.pdf
    ├── output-questions[addition-question]-body.tex
    ├── output-questions[addition-question]-solution.tex
    ├── output-questions[addition-question].tex
    ├── output-questions[poly-question]-body.tex
    ├── output-questions[poly-question]-questions[factors]-body.tex
    ├── output-questions[poly-question]-questions[factors]-solution.tex
    ├── output-questions[poly-question]-questions[factors].tex
    ├── output-questions[poly-question]-questions[graph]-body.tex
    ├── output-questions[poly-question]-questions[graph]-solution.tex
    ├── output-questions[poly-question]-questions[graph].tex
    ├── output-questions[poly-question]-solution.tex
    ├── output-questions[poly-question].tex
    └── output.tex
    ```

## Generating Student-Specific Files

It would be nice to have the expected graph appear in the solution key, but
in order to do that we have to dynamically generate the image for each
student.

  1. The Python standard libraries and `exam_gen` don't have the facilities
    for generating new graphs. Instead we'll need to use the `matplotlib` and
    `numpy` libraries. Run the following commands to add them to the project:

    ```console
    $ pipenv install matplotlib numpy
    ```

    ??? example "Result of `pipenv install matplotlib numpy`"
        Note that your exact output may differ slightly.

        ```console
        $ pipenv install matplotlib numpy
        Installing matplotlib...
        Adding matplotlib to Pipfile's [packages]...
        ✔ Installation Succeeded
        Installing numpy...
        Adding numpy to Pipfile's [packages]...
        ✔ Installation Succeeded
        Installing dependencies from Pipfile.lock (c46356)...
        running exam_gen setup.py
          🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ 0/0 — 00:00:00
        To activate this project's virtualenv, run pipenv shell.
        Alternatively, run a command inside the virtualenv with pipenv run.
        ```

     Now it's possible to import `matplotlib` and `numpy` anywhere in our
     project.

  2. Let's do just that in `poly_question/functions.py` by adding:

     ```python linenums="19"
     import numpy as np
     import matplotlib.pyplot as plt
     ```

  3. We can then use these libraries in a function to generate a new plot of
    our function. Add the following to `poly_question/functions.py`:

    ```python linenums="22"
    def make_poly_graph(polynomial, out_file, bound=8, ticks=2):

        fig = plt.figure()
        ax = fig.subplots()
        x = np.linspace(bound, -bound, 100)
        y = sum([c * (x ** i) for (i, c) in enumerate(polynomial)])
        ax.plot(x,y)

        ax.set_xlim(-bound,bound)
        ax.set_ylim(-bound,bound)
        ax.set_xticks(range(-bound+ticks,bound,ticks))
        ax.set_yticks(range(-bound+ticks,bound,ticks))

        ax.spines.left.set_position('center')
        ax.spines.right.set_color('none')
        ax.spines.bottom.set_position('center')
        ax.spines.top.set_color('none')
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

        ax.grid(linestyle='--')
        ax.minorticks_on()

        fig.savefig(out_file)
    ```

    Don't worry about the contents of this function, all that's important is
    that it will print a graph of the provided polynomial to `out_file`.

    ??? quote "Complete Current `poly_question/functions.py`"
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

        import numpy as np
        import matplotlib.pyplot as plt

        def make_poly_graph(polynomial, out_file, bound=8, ticks=2):

            fig = plt.figure()
            ax = fig.subplots()
            x = np.linspace(bound, -bound, 100)
            y = sum([c * (x ** i) for (i, c) in enumerate(polynomial)])
            ax.plot(x,y)

            ax.set_xlim(-bound,bound)
            ax.set_ylim(-bound,bound)
            ax.set_xticks(range(-bound+ticks,bound,ticks))
            ax.set_yticks(range(-bound+ticks,bound,ticks))

            ax.spines.left.set_position('center')
            ax.spines.right.set_color('none')
            ax.spines.bottom.set_position('center')
            ax.spines.top.set_color('none')
            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')

            ax.grid(linestyle='--')
            ax.minorticks_on()

            fig.savefig(out_file)
        ```

  1. Finally we can change `poly_question\graph_question.py` to the following
    in order to generate and display the graph:

    ???+ example "Complete Current `poly_question\graph_question.py`"
        ```python linenums="1"
        from exam_gen import *
        from .functions import *

        class GraphQuestion(LatexDoc, Question):
            metadata.name = "Graph Question"

            body['exam'].text = r'''
            Sketch the polynomial on this graph:

            \includegraphics[width=\textwidth]{empty_grid.png} \\ ~ \\
            '''

            body['solution'].text = r'''
            Sketch the polynomial on this graph:

            \includegraphics[width=\textwidth]{solution.png} \\ ~ \\
            '''

            settings.assets = ["empty_grid.png"]

            def user_setup(self, ctxt, rng, **kwargs):

                # Recalculates the polynomial from the zeros in `ctxt` and plots it
                make_poly_graph(prod_z(ctxt['zeros']),"solution.png")
        ```

    !!! important ""
        `user_setup` is *always* run in the build directory associated with
        the particular student and document. The current directory
        in `user_setup` is the same directory where the final `.tex` files
        will end up and things you place there will be available to `pdflatex`
        and whatever other tools you need.

  1. Lastly we can run our build commands and see what is produced:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    ```

    !!! important "TODO: Image in `assets/`"

## Fixing the Scaling

This doesn't matter much since future steps will be using new problems anyway
but right now the graphs given to the students can swerve in and out of the
available drawing space.

The following edits fix this:

??? quote "Complete Current `poly_question/graph_question.py`"
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
    # find the derivative of a polynomial
    deriv_p = lambda p: list(map(lambda e : e[0] * e[1], enumerate(p)))[1:]
    # evaluate a polynomial at a point
    eval_p = lambda p, x: sum(map(lambda e : e[1] * (x ** e[0]), enumerate(p)))

    import numpy as np
    import matplotlib.pyplot as plt


    def make_poly_graph(out_file, *polys, bound=8, ticks=2):

        fig = plt.figure()
        ax = fig.subplots()
        x = np.linspace(bound, -bound, 100)
        for poly in polys:
            y = eval_p(poly, x)
            ax.plot(x,y)

        ax.set_xlim(-bound,bound)
        ax.set_ylim(-bound,bound)
        ax.set_xticks(range(-bound+ticks,bound,ticks))
        ax.set_yticks(range(-bound+ticks,bound,ticks))

        ax.spines.left.set_position('center')
        ax.spines.right.set_color('none')
        ax.spines.bottom.set_position('center')
        ax.spines.top.set_color('none')
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

        ax.grid(linestyle='--')
        ax.minorticks_on()

        fig.savefig(out_file)
    ```

??? quote "Complete Current `poly_question/question.py`"
    ```python linenums="1"
    from exam_gen import *
    from .functions import *
    from .graph_question import *
    from .factor_question import *
    from fractions import Fraction
    from math import floor
    import numpy

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

        def user_setup(self,ctxt , rng, **kwargs):

            # Make a list of 4 random integers, the zeros of our polynomial
            zeros = list(map(lambda _: rng.randint(-5,5), range(0,4)))

            # The polynomial such that each index is the coefficient of the
            # corresponding term.
            # (i.e. the polynomial is `poly[0] + poly[1]x + poly[2]x^2 ...` for a
            # given list `poly`)
            base_poly = prod_z(zeros)

            # get the highest magnitude term between the zeroes by going through
            # the different points in the base poly
            samples = numpy.linspace(min(zeros), max(zeros), 100)
            max_val = max(map(lambda n: abs(eval_p(base_poly,n)), samples))

            # Find a scaling factor that both looks nice and isn't a pain to use
            d_limit = 4
            scale = 0
            while scale == 0:
                scale = Fraction(7 / max_val).limit_denominator(d_limit)
                if scale * max_val > 7.5:
                    scale = Fraction(scale.numerator - 1, scale.denominator)
                d_limit += 2

            print(scale)

            # scale the polynomial appropriately
            poly = mul_c(base_poly, scale)

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
                'raw_poly': poly, # using the worse name here because the templates
                                  # don't need more clutter
                'zeros': zeros
            }
    ```


??? quote "Complete Current `poly_question/graph_question.py`"
    ```python linenums="1"
    from exam_gen import *
    from .functions import *

    class GraphQuestion(LatexDoc, Question):
        metadata.name = "Graph Question"

        body['exam'].text = r'''
        Sketch the polynomial on this graph:

        \includegraphics[width=\textwidth]{empty_grid.png} \\ ~ \\
        '''

        body['solution'].text = r'''
        Sketch the polynomial on this graph:

        \includegraphics[width=\textwidth]{solution.png} \\ ~ \\
        '''

        settings.assets = ["empty_grid.png"]

        def user_setup(self, ctxt, rng, **kwargs):

            # Grabs the polynomial from `ctxt` and plots it
            make_poly_graph("solution.png",ctxt['raw_poly'])
    ```

They're not critical if you're following the tutorial since we're going to
move onto other questions. However, they should probably be incorporated more
directly into the tutorial at some point.
