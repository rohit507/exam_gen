# Notes

This is just a scratchpad for notes taken during the development process. All the
stuff here should be eventually moved somewhere else in these docs.

## Development / Infrastructure

  - We're using [`pipenv`](https://pipenv.pypa.io/en/latest/install/#next-steps) to
    do environment and dependency management for this project.
    - Installing `pipenv` took running `sudo apt install pipenv` on Ubuntu.
      - Other install options are found
        [here](https://pipenv.pypa.io/en/latest/install/#installing-pipenv).
    - Open shell in project directory with `pipenv shell`
    - Install a package with `pipenv install <pip-package>`
    - Run a command with `pipenv run <command>`
    - **Note:** If you're inside a `pipenv shell` you can drop the `pipenv run` prefix
      from all of the commands here that have them.

  - Currently, the package is set up to have a single executable that can manage
    most of the actual work of running things.
    - If acting as a user install the package with `pip3 install <location>`
      (maybe `sudo`?)  Then `exam-gen` will be avilable on the command line.
    - If working as a developer then you'll have `exam-gen` readily available
      in `pipenv run` or `pipenv shell`.
      - I recnoment just using `pipenv shell`
      - Alternately you can have a simultaneous global "install" with
        `pip3 install --dev -e ./` but that's contraindicated


  - When updating deps as a developer, make sure the setup.py and pipfiles are
    synced with `pipenv run pipenv-setup sync` after running `pipenv lock`,
    `pipenv sync` or `pipenv update`.

  - We're using [`mkdocs`](https://www.mkdocs.org) for documentation.
    - We're using [`mkdocstrings`](https://github.com/pawamoy/mkdocstrings) to include
      generated docstrings in the mkdocs output.
      - Look at [this page](https://pawamoy.github.io/mkdocstrings/usage/) for more
        detailed usage directions.
    - The theme is [`mkdocs-material`](https://squidfunk.github.io/mkdocs-material/).
    - Run doc server with `pipenv run mkdocs serve` and open
      <http://127.0.0.1:8000/>.
    - Build a static stite with `pipenv run mkdocs build`, results will be placed
      in the `site/` directory.
    - deploy to github with `pipenv run mkdocs gh-deploy`

  - Using best practices taken from
    [the sourcery.ai blog](https://sourcery.ai/blog/python-best-practices/):
    - Import Sort: `pipenv run isort`
    - PEP 8 Convention Check: `pipenv run flake8`
    - Static Type Check: `pipenv run mypy`
    - Tests and Coverage: `pipenv run pytest --cov --cov-fail-under=100`

  - We're using the instructions
    [here](https://setuptools.readthedocs.io/en/latest/userguide/quickstart.html)
    to setup `setuptools` and the core python packaging infrastucture.


  - new examproject
    - `pipenv --python 3.9`
    - `pipenv install <exam_gen>` or `pipenv install -e <exam_gen>`


## Useful Python Facts

  - `inspect.getargspec` can get you get all sorts of information about the arguments
    of a function that's passed to it. Including: Arity, param names, keyword args,
    defaults, and more.
    - This will be super useful for ensuring that there's consistency of parameters
      and a coherent argument structure for `init` and other user interface functions
      as we mixin a bunch of different classes.

  - We should be able to use the `__init_subclass_` mechanism to implement the sort of
    auto-collating settings system that I would like. Especially given how nice it
    would be have the sort of auto-documenting structure that I want.
    - Take the following example

            class Bar():

              bars = []

              def __init_subclass__(cls, **kwargs):
                super().__init_subclass__(**kwargs)
                cls.bars = cls.bars + [cls.bar]

            class Foo(Bar):
                bar = "A"

            class Buzz(Foo):
                bar = "B"

            class Bing(Foo):
                bar = "C"

            print(Foo.bars)
            print(Buzz.bars)
            print(Bing.bars)

    - With output:

            ['A']
            ['A','B']
            ['A','C']

    - Instead of accumulating a set of strings like in the above example, you could
      gather up information on the settings that were previously available.
    - Plus the `__init_subclass__` function gives you a nice place to both generate and
      set the doc string for an object (via `__doc__`).
    - Honestly part of me is wondering whether I should use this mechanism for a lot of
      feature accumulation and overloading mechanisms in the library, rather than just
      for settings management.
      - It's trivially simple and super powerful.
      - It's just a monoid that we can sum down the inheritance heirarchy.
    - Oh wait, I just tried adding this:

            class Bloop(Buzz,Bing):
                bar = "D"

            print(Bloop.bars)

    - And got :

            ['A','B','D']

    - Which means that the system can't really handle multiple inheritance as is.
    - I'm better off using some other introspection to go through parent classes
      and using some other hook for class init to set things up.
    - Yup, that's it. We use `__bases__` as the structure to get the parent classes
      and `__init_subclass__` as the init hook.

## Using a build tool

A bunch of the dependency management stuff has a rather build tool like
structure. I mean, take a look at a question we might write:

```py
class NewQuestion(Question):

   metadata.name = "Addition Question"
   metedata.authors = ["Fry, Phillp J", "Farnsworth, Philo"]

   question_template = File("templates/blabla.html")
   solution_template = File("templates/blabla-solution.html")

   sub_problems = [
      Subprob1,
      (Subprob2, {'param1': 123, 'param2':"FOO"}),
   ]

   def setup(rng, parent_vars, metadata):
       return something()

   @generate_file("graph.pdf", requires=["graph_data.csv"])
   def graph(self, user_vars):
       some_code_here()

   @generate_file("graph_data.csv")
   def graph_data(self, user_vars):
       some_code_here()
```

Where you an specify files and tasks that should be created when the problem
is being rendered.

Also useful, if you have some way of dependency change tracking, is using the
build system to manage the internal structure of the question/template/problem
and

### doit

Right now, it looks like [`doit`](https://github.com/pydoit/doit) is the ideal
python library to use to provide an actual build system like interface to
`exam_gen`.

It's rather imperfect in that it doesn't allow the direct definition of rules,
so we'll have to explicitly generate all the possible actions on every run,
but that's a damn sight better than having to do file dependencies and things
ourselves.

I guess it's important we focus on the stuff about generating proper YAML
dumps and loads, since that's going to be key in making sure that a build system
style works at all.

### invoke

Alternately we build on top of [`invoke`](http://docs.pyinvoke.org/) which
doesn't have any handling of file dependencies, but is otherwise a lot closer
to the structure we want.

If we use `invoke`, then we'll have to implement a lot of the file system
management stuff ourselves, as well as a bunch of the caching but the
fundamental dependency resolution should be a lot better, and a lot easier to
handle.

In order to do more effective partial invocations we'd need some method to
keep to track of when files (and corresponding data-targets) where last used,
when they chnaged and a bunch of other things that are important. There's
a library called `dagger` that can do this, but it'd still take too much effort.

Either way, invoke is probably our best bet by far to actually have a nice cli
frontend for the exam generation stuff.


## Internal/Implementation Documentation

Okay, so in order to get the nice behavior I want for mkdocs the docstrings
of tables should look like the following:

```markdown
<table markdown="1">
<tr markdown="block">
<th markdown="1">
Month **test**
</th>
<th markdown="1">
Savings
</th>
</tr>

<tr markdown="block">
<td markdown="1">
January
</td>
<td markdown="block">

  - list
  - other list

!!! Todo
    Here's an admonition
</td>
/tr>

</table>
```

Note how everything happens at the same indentation level, and how nested
markdown blocks are not further indented.

In an ideal world we'd be able to tell whether the contents of block have
span or block level markdown code, but for now we'll just use the existence
of newlines as a proxy.

That way we can at least try to spit out the more human readable markdown
format when it's possible. Otherwise, if there's block level code then we can
produce the (uglier) table version.

## Wrapt for nicer interface to validation and stuff.

So there's a library `wrapt` (with instructions
[here](https://wrapt.readthedocs.io/en/latest/wrappers.html)) that would let
us wrap the various settings objects in a proxy type with some custom
attributes.

I think it would be super nice looking to do it this way, but impl complexity
cost is probably too high. Alas.

## Thoughts on architecture/components

  - Templates:
      - File(...): named tuple that we use to denote this is a file ref not a
        raw string.
  - Multi_Templates:
      - members
  -


## Things To Do

  - TODO: Figure out what the `options.install_requires` actually means.
  - TODO: Remove unneccesary dependencies from `Pipfile.lock`.
  - TODO: Actually-set-up/Verify that the git pre-commit hook works.
  - TODO: Move the notes from above somewhere appropriate within the docs or the code
  - TODO: Once the next version of `attrs` comes out, update the dependency to
    use the version in pipi
