# Project Setup and Organization

`exam_gen` projects have two major components: Exams and Classrooms

An **Exam** or assignment is a broad wrapper around the questions,
student instructions, grading mechanisms, and other textual elements that define
what a student reads and does when they're doing the task.

  - **Questions** are self-contained sections of the exam that have some text,
    scoring mechanisms, and/or sub-questions.

A **Classroom** defines a group of students who can interact with the assignment
in various ways. It has various sub-components that describe how to import, store,
organize, and export information about how each of those students interacted with
the exam.

  - A **Roster** that lists each student in the class. This is the only mandatory
    component of a classroom as students are needed to generate personalized exams.
  - The **Answers** component describes how to parse and imported student answers
    to exam questions for grading and evaluation.
  - Likewise, **Scores** will import the grades teachers assign to questions that
    cannot be graded automatically.
  - The **Grade** module will combine teacher provided scores and auto-grading
    to generate and export grades for allthe students.

In a project each of the highlighted elements above is represented by a python
class that acts as a configuration file that can be read and executed to
generate various outputs like **exam pdfs**, **grade spreadsheets**, and
**solution keys**.

## Environment Setup

The project environment is very simple to set up. The only core dependency is Pipenv:

  - **[Pipenv](https://pipenv.pypa.io):** Hides a lot of python packing and
    automates much of the dependency management process.

In addition each output format usually has its own requirements. See below
for the output format you're targeting:

??? info "LaTeX-based PDF Output"
    The only requirement for LaTeX pdf output is **[TeX Live](https://www.tug.org/texlive/)**.

    - **[TeX Live](https://www.tug.org/texlive/):** Needed to actually build
      the exams. Installing the full version (usually `texlive-full`) is
      recommended.
      - Ubuntu: `sudo apt install texlive-full`
      - Other Linux: Check your distro's package manager or see
        [here](https://www.tug.org/texlive/quickinstall.html).
      - Mac: [MacTeX](https://www.tug.org/mactex/) or install via homebrew.
      - Windows: Follow the instructions
        [here](https://www.tug.org/texlive/windows.html)

## Directory Setup

  1. Create a new directory (`<proj_dir>`) for your exam:

     ```console
     $ mkdir <proj_dir>
     ```

  1. **Within `<proj_dir>`** use pipenv to install this library:

    ```console
    $ pipenv install <repo_url>
    ```

    !!! note ""
        `<repo_url>` is currently `https://github.com/rohit507/exam_gen.git`
        but is likely to change. Any git repo containing this library will
        work.

  1. Save [this file](assets/exam.py) as `exam.py` in the project directory.
    The name can be changed but will require the other commands to be
    modified accordingly.

    ??? abstract "Full contents of `exam.py`"
        [|include_block("assets/exam.py")| indent(8) |]

  1. Ensure that `exam.py` is executable, otherwise replace `./exam.py` with
    `pipenv run python3 exam.py` in future steps.

    ```console
    $ chmod +x exam.py
    ```

  1. Test the setup with the following, ensure it produces a short help message:

   ```console
   $ ./exam.py
   ```

## Next Steps

  - Add classrooms and students using the instructions [here]().
  - Add questions using the instructions [here]().
  - Find other options and answers to questions [here](/quick_reference.html).

!!! error "fix links above"
