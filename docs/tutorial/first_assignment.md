# Your First Assignment

We'll be walking through the creation of a simple randomized assignment with
some multiple-choice questions, as well as importing student answers and
assigning grades.

## Setting up Your Development Environment

There are two main requirements to run `exam_gen`: LaTeX and `pipenv`.
Set each up on your machine as appropriate.

  - **[TeX Live](https://www.tug.org/texlive/):** Is needed to actually build
    the exams. Installing the full version (usually `texlive-full`) is
    recommended.
    - Ubuntu: `sudo apt install texlive-full`
    - Other Linux: Check your distro's package manager or see
      [here](https://www.tug.org/texlive/quickinstall.html).
    - Mac: [MacTeX](https://www.tug.org/mactex/) or install via homebrew.
    - Windows: Follow the instructions
      [here](https://www.tug.org/texlive/windows.html)

  - **[Pipenv](https://pipenv.pypa.io):** Hides a lot of python packing and
    dependency issues by creating a nice stable wrapper environment for our work.
    - Installation instructions are
      [here](https://pipenv.pypa.io/en/latest/install/#installing-pipenv).

With both of those ready to go, we can move on to making an assignment.

!!! Note "Windows Users"
    From here on out we'll be tailoring our instructions to unix-like systems.
    Windows users might need to edit the commands provided to make things work,
    but the library itself should be OS independent.

## Setting up the Project


  1. We'll create a new project directory called `new_exam` and move into it with:

     ```console
     $ mkdir new_exam
     $ cd new_exam
     ```

     This would also be a good time to set up version control (with `git init` or
     similar).

  2. Then we can add the `exam_gen` library to our project using pipenv:

     ```console
     $ pipenv install <repo_url>
     ```

     Right now `<repo_url>` would be `https://github.com/rohit507/exam_gen.git`
     but the project should probably be somewhere different soon.
     Once it's moved, that link should be directly embedded above.

  3. Finally we need to create `exam.py`, which is the most important file in
     any new project. We'll start by just creating a new file and making it
     executable.

     ```console
     $ touch exam.py
     $ chmod +x exam.py
     ```

     `exam.py` will contain a full description of our assignment.
     We'll describe how to create it in the next section.

## Creating an Initial `exam.py`

Open the editor of your choice and paste the following into `exam.py`:

```python linenums="1"
#!/usr/bin/env -S pipenv run python3

from exam_gen import *

class NewExam(LatexDoc, Exam):

    classes = {}

    questions = {}

    intro.text = r'''
    \emph{Example Exam Introduction}
    '''

    def user_setup(self, **kwargs):
        pass

if __name__ == "__main__": run_cli(globals())
```

Once you save, this constitutes a minimal description of an assignment.
One with no content and a tiny snippet of text as an introduction.

??? Info "Line-by-Line Breakdown of `exam.py`"

    ```python linenums="3"
    from exam_gen import *
    ```
    Importing our library. Simple enough, we can't get anything else done
    without this.

    ```python linenums="5"
    class NewExam(LatexDoc, Exam):
    ```

    Then we initialize our new assignment as a python class.

    This library uses classes to represents assignments (i.e. `Exam`) and
    questions within those assignments. Individual versions of those
    assignments (which are student specific) will be objects initialized from
    these classes.

    It's also worth noting what classes `#!python NewExam` inherits from.
    `LatexDoc` tells our backend that we're working in LaTeX and describes
    how to build new `.pdf` files from the text that's generated. `Exam`,
    on the other hand, describes various elements of the structure of an
    assignment which we'll go over later.

    ```python linenums="7"
        classes={}
    ```

    The `Exam` class pulls double duty in this system.
    It acts as the definition of a single exam's contents, but it also
    captures some grading and student-roster management info.

    Most of that roster-management is delegated to `Classrooms`, which we'll
    look at in more detail soon, but we need to store the set of classrooms we
    are going to use somewhere.

    For now we leave this list empty.

    ```python linenums="9"
        questions={}
    ```

    Each exam has to have some list of questions. It's empty for now, but we'll
    be adding to it later.

    ```python linenums="11"
        intro.text = r'''
        \emph{Example Exam Introduction}
        '''
    ```

    The biggest content element of an `Exam` is the introduction, which tends
    to have the rules, instructions, honor-code, etc.. This is how we specify
    what text should appear in that intro.

    Note how we're using the `r''' ... '''` string notation. This allows for
    multi-line strings where `'\'` and other special characters don't need to
    be escaped. Given how TeX has a truly painful number of stupid syntax
    quirks this is very useful.

    ```python linenums="15"
        def user_setup(self, **kwargs):
            pass
    ```

    This function can be filled in later to provide customization to each
    version of the exam. For now we leave it empty.

    ```python linenums="18"
    if __name__ == "__main__": run_cli(globals())
    ```

    This is an archaic python incantation. In short, one should read
    `#!python if __name__ == "__main__":` as "Do this if we're running this
    file as a script". Likewise `#!python globals()` is a function that
    returns all the variables in scope where it was called, including classes
    like `NewExam`. `#!python run_cli()` then searches through that list for
    a subclass of `Exam` to build assignments with.

    ```python linenums="1"
    #!/usr/bin/env -S pipenv run python3
    ```

    This is a unix hashbang, when an executable text file is run and starts with
    `#!some_command` then the file's contents will be passed to `some_command`
    as an argument.
    Since we use `pipenv` for build isolation this will automatically wrap any
    invocation of `./exam.py` with the appropriate environment.

    All together, this just lets us call `exam_gen`'s command line interface
    when we run the file as a script. Along with the `chmod +x exam.py` from
    earlier, this lets us run `./exam.py <arguments>` instead of having to
    manually call pipenv and python.

We can quickly test our setup by running `#!console ./exam.py` in our terminal. You should
see a result like this:

```
exam_gen build tool

Available Commands:
  <cmd_name> list          List major available build actions.
  <cmd_name> list --all    List all available build actions.

Replace <cmd_name> with however you invoke this tool.
(usually `./exam.py`,`pipenv run ./exam.py`,or `pipenv run python3 exam.py`)
```

We can also take a look at the various possible build commands available to
us by following the above instructions. (e.g. running
`#!console ./exam.py list --all`) Which should produce a result like:

```
build-exam       Build all the exams for each student.
build-solution   Build all the answer keys for each student.
cleanup          Clean all generated files. (e.g. 'rm -rf ~*')
parse-roster     parse the class rosters (incl. answer and score data if available)
```

None of those command do anything right now as they all depend on having a
roster of students available to parse and build exams for. So let's add that.

## Adding a Classroom and Roster to the Project

Classrooms are how we manage groups of students who take an instance of the
exams.
The core of each classroom is a roster of students that our library can parse.

  - Create new `class-1.csv` in the project directory with the following
    content:

    ```csv
    Name,Student ID,Email Address
    "Wilkins, Willa",49234720,awilkins@berkeley.edu
    "Smith, Abby",49232758,ysmith@berkeley.edu
    "Calderon, Reema",49233588,acalderon@berkeley.edu
    "Meza, Neave",49234574,emeza@berkeley.edu
    "Rios, Christine",49232540,erios@berkeley.edu
    "House, Sharon",49232926,nhouse@berkeley.edu
    "Ahmad, Ezmae",49234288,eahmad@berkeley.edu
    "Phelps, Mehdi",49233409,iphelps@berkeley.edu
    "Mcfarlane, Tracey",49232948,ymcfarlane@berkeley.edu
    "Decker, Adem",49234533,mdecker@berkeley.edu
    ```

    This is a roster of fake students in a version of the BCourses format that
    we'll be using for the tutorial.

  - In `exam.py` change line 7 to the following:

    ```python linenums="7"
        classes = {
            'fake-class': Classroom
        }
    ```

    This tells our system that there's a `Classroom` called `fake-class` that
    we'll be building assignments for.
    However left as it this would throw an error as each `Classroom` needs
    a roster of students.

  - To fix this we'll specify a roster based on `class-1.csv`.
    There are multiple ways to parse a roster so we'll be specifying the
    parser we'll use as well by changing line 8 to:

    ```python linenums="8"
            'fake-class': Classroom.with_options(
                roster=BCoursesCSVRoster.with_options(
                    file_name="class-1.csv"
                )
            ),
    ```

    Note how our roster is `BCoursesCSVRoster` rather than some more generic
    class. This subclass specifically describes how to parse rosters from
    BCourses, other formats would require other parsers. The dev guide will
    cover this in more detail.

??? Example "Complete Current `exam.py`"
    ```python linenums="1"
    #!/usr/bin/env -S pipenv run python3

    from exam_gen import *

    class NewExam(LatexDoc, Exam):

        classes = {
            'fake-class': Classroom.with_options(
                roster=BCoursesCSVRoster.with_options(
                    file_name="class-1.csv"
                )
            ),
        }

        questions = {}

        intro.text = r'''
        \emph{Example Exam Introduction}
        '''

        def user_setup(self, **kwargs):
            pass

    if __name__ == "__main__": run_cli(globals())
    ```

## Testing our Minimal Assignment


### Available Build Actions

To see what new commands we have available:

```console
$ ./exam.py list
```

??? Quote "Result of `./exam.py list`"
    ``` linenums="1" hl_lines="2 4"
    build-exam               Build all the exams for each student.
    build-exam:class-1       Build the exams for class 'class-1'.
    build-solution           Build all the answer keys for each student.
    build-solution:class-1   Build the answer keys for class 'class-1'.
    cleanup                  Clean all generated files. (e.g. 'rm -rf ~*')
    parse-roster             parse the class rosters (incl. answer and score data if available)
    ```

We now have build actions that cover an entire class's students.
We can break this down further with:

```console
$ ./exam.py list --all
```

??? Quote "Result of `./exam.py list --all`"
    ``` linenums="1" hl_lines="2-12 15-24"
    build-exam                          Build all the exams for each student.
    build-exam:class-1                  Build the exams for class 'class-1'.
    build-exam:class-1:acalderon
    build-exam:class-1:awilkins
    build-exam:class-1:eahmad
    build-exam:class-1:emeza
    build-exam:class-1:erios
    build-exam:class-1:iphelps
    build-exam:class-1:mdecker
    build-exam:class-1:nhouse
    build-exam:class-1:ymcfarlane
    build-exam:class-1:ysmith
    build-solution                      Build all the answer keys for each student.
    build-solution:class-1              Build the answer keys for class 'class-1'.
    build-solution:class-1:acalderon
    build-solution:class-1:awilkins
    build-solution:class-1:eahmad
    build-solution:class-1:emeza
    build-solution:class-1:erios
    build-solution:class-1:iphelps
    build-solution:class-1:mdecker
    build-solution:class-1:nhouse
    build-solution:class-1:ymcfarlane
    build-solution:class-1:ysmith
    cleanup                             Clean all generated files. (e.g. 'rm -rf ~*')
    parse-roster                        parse the class rosters (incl. answer and score data if available)
    parse-roster:class-1
    ```

We even have actions to build an exam or solution key for each individual
student.

### Testing Roster Parsing

To test roster parsing we can run:

```console
$ ./exam.py parse-roster
```

You should see `.  parse-roster:fake-class` on the terminal, but more
importantly, a `~data/` directory should have been created with a number of
subdirectories and files.

??? Quote "Result of `tree ~data`"
    ```
    ~data/
    └── class-fake-class
        ├── roster.yaml
        ├── student-acalderon
        │   └── data.yaml
        ├── student-awilkins
        │   └── data.yaml
        ├── student-eahmad
        │   └── data.yaml
        ├── student-emeza
        │   └── data.yaml
        ├── student-erios
        │   └── data.yaml
        ├── student-iphelps
        │   └── data.yaml
        ├── student-mdecker
        │   └── data.yaml
        ├── student-nhouse
        │   └── data.yaml
        ├── student-ymcfarlane
        │   └── data.yaml
        └── student-ysmith
            └── data.yaml
    ```

Looking at `~data/class-fake-class/roster.yaml` and the various `data.yaml`
files will show a somewhat pretty printed representation of the class and
student information. This will be useful for debugging later on.

### Testing A Minimal Build

We can clean up out previous work and build a single exam with:

```console
$ ./exam.py cleanup
$ ./exam.py build-exam:fake-class:erios
```

This will produce a number of files in `~data`, `~build`, and `~out`.

??? Quote "Result of `tree ~*`"
    ```
    ~build
    └── class-fake-class
        └── student-erios
            └── exam-exam
                ├── output.aux
                ├── output-intro.tex
                ├── output.log
                ├── output.out
                ├── output.pdf
                └── output.tex
    ~data
    └── class-fake-class
        ├── roster.yaml
        ├── student-acalderon
        │   └── data.yaml
        ├── student-awilkins
        │   └── data.yaml
        ├── student-eahmad
        │   └── data.yaml
        ├── student-emeza
        │   └── data.yaml
        ├── student-erios
        │   ├── data.yaml
        │   └── exam-exam
        │       ├── final-context-output-intro.yaml
        │       ├── final-context-output.yaml
        │       ├── finalize-log.yaml
        │       ├── initial-context-output-intro.yaml
        │       ├── initial-context-output.yaml
        │       ├── output-log.yaml
        │       ├── post-finalize-doc.yaml
        │       ├── post-init-doc.yaml
        │       ├── post-setup-doc.yaml
        │       ├── post-template-doc.yaml
        │       ├── pre-finalize-doc.yaml
        │       ├── pre-init-doc.yaml
        │       ├── pre-setup-doc.yaml
        │       ├── pre-template-doc.yaml
        │       ├── result-output-intro.tex
        │       ├── result-output.tex
        │       ├── setup-log.yaml
        │       ├── template-output-intro.jn2.tex
        │       ├── template-output.jn2.tex
        │       ├── template-result.yaml
        │       └── template-spec.yaml
        ├── student-iphelps
        │   └── data.yaml
        ├── student-mdecker
        │   └── data.yaml
        ├── student-nhouse
        │   └── data.yaml
        ├── student-ymcfarlane
        │   └── data.yaml
        └── student-ysmith
            └── data.yaml
    ~out
    └── exam-exam
        └── class-fake-class
            └── erios.pdf
    ```

Looking at the final output in `~out/exam-exam/class-fake-class/erios.pdf`
there's an exam with only the title page and our introduction text.

!!! error "TODO: Add image of result"

The logging and debug data in `~data/class-fake-class/student-erios/exam-exam/`
captures a lot of the intermediate state involved in building the exam, the
user guide will provide a deeper overview of this and how it can be used.

There is also a build directory in
`~build/class-fake-class/student-erios/exam-exam/` which is where we try to
provide an isolated environment for `pdflatex` or other external build tool.
This is also the working directory when user-provided code to generate files
is run.

## Adding a Question

  - File Manip
  - Templating
  - Solutions
  - User-Setup
  - RNG

## Adding a Multi-Part Question

  - Context

## Introducing Student Answers

## Introducing Instructor Scores

## Getting Grade Output

## Adding a Multiple Choice Question

## Autograding
