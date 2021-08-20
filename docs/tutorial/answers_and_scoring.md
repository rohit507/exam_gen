# Answers and Scoring

Here we'll go over loading student answers into the system and generating
grades.

## Class Reorganization

First though, let's reorganize our files to better separate one class's
information from everything else.

  1. Make a new directory for our fake class and move over our roster:

    ```console
    $ mkdir fake_class
    $ mv class-1.csv fake_class/
    ```

  1. We also can create a new file for this classroom's settings, instead of
    keeping them inline as part of `exam.py`:

    ```console
    $ touch fake_class/setup.py
    ```

  1. And load the following contents into that file:

    ???+ quote "Complete Current `fake_class/setup.py`"
        ```python linenums="1"
        from exam_gen import *
        import attr

        class FakeClassroom(Classroom):

            roster = BCoursesCSVRoster.with_options(
                file_name="class-1.csv"
            )
        ```

    Note how we're creating a new class `#!py FakeClassroom` that inherits from
    `#!py Classroom`.
    This is one way to overload the same settings that one can with `with_options`.

  1. We also need to update `exam.py` appropriately:

    First by adding an appropriate import statement:

    ```python linenums="9"
    from fake_class.setup import *
    ```

    Then by updating the list of classes to use `FakeClassroom` directly instead
    of configuring a new classroom on the fly with `with_options`:

    ```python linenums="13"
    classes = {
        'fake-class': FakeClassroom,
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
        from fake_class.setup import *

        class NewExam(LatexDoc, Exam):

            classes = {
                'fake-class': FakeClassroom,
            }

            questions = {
                'addition-question': SumQuestion,
                'poly-question': PolyQuestion,
                'graph-question': GraphQuestion,
                'matrix-question': MatrixQuestion,
                'csp-question': CspQuestion
            }

            intro.text = r'''
            \emph{Example Exam Introduction}
            '''

            def user_setup(self, **kwargs):
                pass

        if __name__ == "__main__": run_cli(globals())
        ```

 1. Test whether this works by building an exam as usual:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py build-exam:fake-class:erios
    ```

    At this point nothing substantive has changed, we've just been able to
    move all the class specific information into a subfolder.

## Loading Student Answers

For the next steps we're going to take student provided answers and import
them into the tool.
The user guide shows how to set up various automated testing tools for use with
this library.

!!! error "TODO: link to the user guide"

From here on out we'll be assuming that you followed the guide for
Canvas/BCourses and using the corresponding exported answer data.

  1. We have made an example answer sheet for use with our fake class roster.
    You should load it into `fake_class/exam_answers.csv` with the following
    contents:

    ??? quote "Complete Current `fake_class/exam_answers.csv`"
        ```csv linenums="1"
        name,sis_id,submitted,attempt,117606621: Problem 1: Sum of All Answers,0,"117606759: Problem 2A: Sketch the Polynomial (This text is visible to student) \n Note: This type of question is a bit wonky w/ multiple submissions. All files must be uploaded on your final submission of the exam, otherwise the proctors won't see them.",0,117606898: Problem 2B: What are the factors of the polynomial?,0,117607010: Problem 3: Masks of a bipartite graph,0,117607036: Problem 4: Independent columns,0,117607116: Problem 5: Constraint Satisfaction,0,n correct,n incorrect,score
        "House, Sharon",49232926,2021-07-12 20:01:01 UTC,1,519,0,,0,,0,"C,D,E",0,D,0,"B,D,F,H,I,J,N",0,2,5,0
        "Mcfarlane, Tracey",49232948,2021-07-12 19:59:47 UTC,1,593,0,,0,,0,"A,B,C",0,B,0,"A,D,F,G,I,J",0,2,5,0
        "Decker, Adem",49234533,2021-07-12 19:58:33 UTC,1,623,0,,0,,0,"A,D,E",0,D,0,"B,C,F,H,I,N",0,2,5,0
        "Rios, Christine",49232540,2021-07-12 19:57:17 UTC,1,638,0,,0,(x -1)(x +5)(x + 5)(x + 1),0,"A,B,C",0,D,0,"B,C,F,H,I,J",0,2,5,0
        "Meza, Neave",49234574,2021-07-12 19:56:08 UTC,2,,0,,0,,0,,0,D,0,"B,C,F,H,I,J",0,1,6,0
        "Meza, Neave",49234574,2021-07-12 19:55:15 UTC,1,4432,0,,0,,0,"A,B,D",0,,0,,0,2,5,0
        "Ahmad, Ezmae",49234288,2021-07-12 19:54:27 UTC,1,625,0,,0,x * (x + 3) ^2 * (x - 4),0,"B,C,D,E",0,D,0,"B,D,F,G,I,L,N",0,2,5,0
        "Wilkins, Willa",49234720,2021-07-12 19:51:25 UTC,2,508,0,,0,,0,"B,C,E",0,,0,"B,C,E,G,I,J,L,N",0,2,5,0
        "Wilkins, Willa",49234720,2021-07-12 19:50:15 UTC,1,112,0,,0,(x -3)(x +1),0,"B,C,E",0,B,0,"A,C,G,M,O",0,2,5,0
        "Calderon, Reema",49233588,2021-07-12 19:48:46 UTC,4,,0,,0,(x -3)^2 * x * (x + 3),0,,0,,0,"B,C,E,H,I,N",0,2,5,0
        "Calderon, Reema",49233588,2021-07-12 19:47:14 UTC,3,609,0,,0,,0,"A,B",0,D,0,,0,2,5,0
        "Calderon, Reema",49233588,2021-07-12 19:46:32 UTC,2,1234,0,,0,123,0,"B,E",0,,0,"N,O",0,3,4,0
        "Calderon, Reema",49233588,2021-07-12 19:45:55 UTC,1,112,0,,0,x^2 (x+3),0,"B,D,E",0,,0,"B,C,F",0,3,4,0
        ```

  2. We also need to specify relevant details about how to associate columns
    of the csy to problems in our exam. Add the following to `FakeClassroom`:

    ```python linenums="11"
    answers = CSVAnswers.with_options(
        file_name="exam_answers.csv",
        ident_column="sis_id",
        attempt_column="attempt",
        mapping={
            'graph-question': "Problem 3",
            'matrix-question': "Problem 4",
            'csp-question': "Problem 5"
        }
    )
    ```

    The `CSVAnswers` class here is used for decoding `csv` files, associating
    submissions with students, and associating columns with problems.

    Let's break down the various fields we set:

      - `file_name`: As expected this is the CSV with all the answers to read in.
        It's specified relative to where `FakeClassroom` is define. (i.e. in
        `fake_class/setup.py` so in the `fake_class/` folder.)
      - `ident_column`: This is the column with the student's unique identifier.
        Here's its saying that the `sis_id` column in the csv is how we
        distinguish between students.
      - `attempt_column`: This is the column that determines which submission
        attempt corresponds to each row of the column.
        It ensures the latest submission for each problem is the one that's
        graded.
      - `mapping`: This tells us how we should assign columns from the csv to
        specific problems. The key is the problem name and value is a unique
        substring of the column in the csv.

        We're only mapping the three multiple choice questions over since
        those are the only auto-gradable ones.

        See the user guide for details on how to map answers to nested
        questions and other complex cases.


    There's further ways to customize this mapping from `csv` to answers
    specified in the user guide.

    !!! error "TODO: link to user guide"

  1. Nothing much should change at this point but feel free to run a test build
    regardless.

## Generating Grades

Finally we need to specify how to get our grades back out.
Currently only a csv output format is supported.

  1. Add the following to `FakeClassroom` in `fake_class/setup.py`:

    ```python linenums="22"
    grades = CSVGrades.with_options(
        file_name="grades.csv",
        columns={
            'Student ID': 'student_id',
            'name': 'name',
            'Problem 1: Answer': 'addition-question.answer',
            'Problem 1: Correct Answer': 'addition-question.correct',
            'Problem 1: Total Weight': 'addition-question.total_weight',
            'Problem 1: Ungraded Points': 'addition-question.ungraded_points',
            'Problem 1: Weighted Points': 'addition-question.weighted_points',
            'Problem 1: Points': 'addition-question.points',
            'Problem 2A: Points': 'poly-question.graph.points',
            'Problem 2B: Points': 'poly-question.factors.points',
            'Problem 3: Points': 'graph-question.points',
            'Problem 4: Points': 'matrix-question.points',
            'Problem 5: Points': 'csp-question.points',
            'Total Weight': 'total_weight',
            'Points': 'weighted_points',
            'Percent Correct': 'percent_grade',
            'Percent Ungraded': 'percent_ungraded'
        }
    )
    ```

    This specifies how to dump grade information into a csv file, with the
    following fields:

      - `file_name`: The name of the file to be produced. It will end up in
        `~out/class-fake-class/` once it has been generated.
      - `columns`: This is way to specify each column of the output `grades.csv`.
        Each key in the dictionary is the column name and the value is a
        string specifying what information goes in that column.

    There are a few key-words in the specification string:

      - `student_id`: The student's identifier
      - `name`: The student's name
      - `precent_grade`: The percentage grade for the exam

    For each problem, or the test as a whole, you can specify certain
    information to print.

      - `<problem>.answer` : The student provided answer
      - `<problem>.correct` : The correct answer, if specified by the problem definition.
      - `<problem>.total_weight` : The weight of the problem in the exam.
      - `<problem>.ungraded_weight` : The weight of problems with no grade assigned
      - `<problem>.points` : The points given for the question.

    Where `<problem>` is the name of a problem in various `questions` values.
    Nested problems are delimited with `.`.

    More details on available specifiers can be found in the users guide.

    !!! error "TODO: link user_guide"


??? quote "Complete Current `fake_class/setup.py`"
    ```python linenums="1"
    from exam_gen import *
    import attr

    class FakeClassroom(Classroom):

        roster = BCoursesCSVRoster.with_options(
            file_name="class-1.csv"
        )

        answers = CSVAnswers.with_options(
            file_name="exam_answers.csv",
            ident_column="sis_id",
            attempt_column="attempt",
            mapping={
                'graph-question': "Problem 3",
                'matrix-question': "Problem 4",
                'csp-question': "Problem 5"
            }
        )

        grades = CSVGrades.with_options(
            file_name="grades.csv",
            columns={
                'Student ID': 'student_id',
                'name': 'name',
                'Problem 1: Answer': 'addition-question.answer',
                'Problem 1: Correct Answer': 'addition-question.correct',
                'Problem 1: Total Weight': 'addition-question.total_weight',
                'Problem 1: Ungraded Points': 'addition-question.ungraded_points',
                'Problem 1: Weighted Points': 'addition-question.weighted_points',
                'Problem 1: Points': 'addition-question.points',
                # 'Problem 1: Percent Grade': 'addition-question.percent_grade',
                # 'Problem 1: Percent Ungraded': 'addition-question.percent_ungraded',
                # 'Problem 2A: Answer': 'poly-question.graph.answer',
                # 'Problem 2A: Correct Answer': 'poly-question.graph.correct',
                # 'Problem 2A: Total Weight': 'poly-question.graph.total_weight',
                # 'Problem 2A: Ungraded Points': 'poly-question.graph.ungraded_points',
                # 'Problem 2A: Weighted Points': 'poly-question.graph.weighted_points',
                'Problem 2A: Points': 'poly-question.graph.points',
                # 'Problem 2B: Answer': 'poly-question.factors.answer',
                # 'Problem 2B: Correct Answer': 'poly-question.factors.correct',
                # 'Problem 2B: Total Weight': 'poly-question.factors.total_weight',
                # 'Problem 2B: Ungraded Points': 'poly-question.factors.ungraded_points',
                # 'Problem 2B: Weighted Points': 'poly-question.factors.weighted_points',
                'Problem 2B: Points': 'poly-question.factors.points',
                # 'Problem 3: Answer': 'graph-question.answer',
                # 'Problem 3: Correct Answer': 'graph-question.correct',
                # 'Problem 3: Total Weight': 'graph-question.total_weight',
                # 'Problem 3: Ungraded Points': 'graph-question.ungraded_points',
                # 'Problem 3: Weighted Points': 'graph-question.weighted_points',
                'Problem 3: Points': 'graph-question.points',
                # 'Problem 3: Percent Grade': 'graph-question.percent_grade',
                # 'Problem 3: Percent Ungraded': 'graph-question.percent_ungraded',
                # 'Problem 4: Answer': 'matrix-question.answer',
                # 'Problem 4: Correct Answer': 'matrix-question.correct',
                # 'Problem 4: Total Weight': 'matrix-question.total_weight',
                # 'Problem 4: Ungraded Points': 'matrix-question.ungraded_points',
                # 'Problem 4: Weighted Points': 'matrix-question.weighted_points',
                'Problem 4: Points': 'matrix-question.points',
                # 'Problem 4: Percent Grade': 'matrix-question.percent_grade',
                # 'Problem 4: Percent Ungraded': 'matrix-question.percent_ungraded',
                # 'Problem 5: Answer': 'csp-question.answer',
                # 'Problem 5: Correct Answer': 'csp-question.correct',
                # 'Problem 5: Total Weight': 'csp-question.total_weight',
                # 'Problem 5: Ungraded Points': 'csp-question.ungraded_points',
                # 'Problem 5: Weighted Points': 'csp-question.weighted_points',
                'Problem 5: Points': 'csp-question.points',
                # 'Problem 5: Percent Grade': 'csp-question.percent_grade',
                # 'Problem 5: Percent Ungraded': 'csp-question.percent_ungraded',
                'Total Weight': 'total_weight',
                'Points': 'weighted_points',
                'Percent Correct': 'percent_grade',
                'Percent Ungraded': 'percent_ungraded'
            }
        )

    # Alternate format,
    #
    # fake_classroom = Classroom.with_options(
    #     roster = BCoursesCSVRoster.with_options(
    #         file_name="class-1.csv"
    #     ),
    #     root_file = __file__
    # )
    ```

  1. Test this by generating the grades for this class:

    ```console
    $ ./exam.py cleanup
    $ ./exam.py calculate-grades:fake-class
    ```

    ??? example "Contents of `~out/class-fake-class/grades.csv`"
        ```
        Student ID,name,Problem 1: Answer,Problem 1: Correct Answer,Problem 1: Total Weight,Problem 1: Ungraded Points,Problem 1: Weighted Points,Problem 1: Points,Problem 1: Percent Grade,Problem 1: Percent Ungraded,Problem 2A: Answer,Problem 2A: Correct Answer,Problem 2A: Total Weight,Problem 2A: Ungraded Points,Problem 2A: Weighted Points,Problem 2A: Points,Problem 2B: Answer,Problem 2B: Correct Answer,Problem 2B: Total Weight,Problem 2B: Ungraded Points,Problem 2B: Weighted Points,Problem 2B: Points,Problem 3: Answer,Problem 3: Correct Answer,Problem 3: Total Weight,Problem 3: Ungraded Points,Problem 3: Weighted Points,Problem 3: Points,Problem 3: Percent Grade,Problem 3: Percent Ungraded,Problem 4: Answer,Problem 4: Correct Answer,Problem 4: Total Weight,Problem 4: Ungraded Points,Problem 4: Weighted Points,Problem 4: Points,Problem 4: Percent Grade,Problem 4: Percent Ungraded,Problem 5: Answer,Problem 5: Correct Answer,Problem 5: Total Weight,Problem 5: Ungraded Points,Problem 5: Weighted Points,Problem 5: Points,Problem 5: Percent Grade,Problem 5: Percent Ungraded,Total Weight,Points,Percent Correct,Percent Ungraded
        49234720,"Wilkins, Willa",,,0,0,0,,0,0,,,0,0,0,,,,0,0,0,,,,2,2,0,0,0.0,1.0,,,1,1,0,0,0.0,1.0,,,2,2,0,0,0.0,1.0,5,0,0.0,1.0
        49232758,"Smith, Abby",,,0,0,0,,0,0,,,0,0,0,,,,0,0,0,,,,2,2,0,0,0.0,1.0,,,1,1,0,0,0.0,1.0,,,2,2,0,0,0.0,1.0,5,0,0.0,1.0
        49233588,"Calderon, Reema",,,0,0,0,,0,0,,,0,0,0,,,,0,0,0,,,,2,2,0,0,0.0,1.0,,,1,1,0,0,0.0,1.0,,,2,2,0,0,0.0,1.0,5,0,0.0,1.0
        49234574,"Meza, Neave",,,0,0,0,,0,0,,,0,0,0,,,,0,0,0,,,,2,2,0,0,0.0,1.0,,,1,1,0,0,0.0,1.0,,,2,2,0,0,0.0,1.0,5,0,0.0,1.0
        49232540,"Rios, Christine",,,0,0,0,,0,0,,,0,0,0,,,,0,0,0,,"A, B, C","A, B, C",2,0,2.0,2.0,1.0,0.0,,,1,1,0,0,0.0,1.0,,,2,2,0,0,0.0,1.0,5,2.0,0.4,0.6
        49232926,"House, Sharon",,,0,0,0,,0,0,,,0,0,0,,,,0,0,0,,"C, D, E","B, D, E",2,0,2.0,2.0,1.0,0.0,,,1,1,0,0,0.0,1.0,,,2,2,0,0,0.0,1.0,5,2.0,0.4,0.6
        49234288,"Ahmad, Ezmae",,,0,0,0,,0,0,,,0,0,0,,,,0,0,0,,"B, C, D, E","C, D, E",2,0,2.0,2.0,1.0,0.0,,,1,1,0,0,0.0,1.0,,,2,2,0,0,0.0,1.0,5,2.0,0.4,0.6
        49233409,"Phelps, Mehdi",,,0,0,0,,0,0,,,0,0,0,,,,0,0,0,,,,2,2,0,0,0.0,1.0,,,1,1,0,0,0.0,1.0,,,2,2,0,0,0.0,1.0,5,0,0.0,1.0
        49232948,"Mcfarlane, Tracey",,,0,0,0,,0,0,,,0,0,0,,,,0,0,0,,"A, B, C","A, C, D",2,0,2.0,2.0,1.0,0.0,,,1,1,0,0,0.0,1.0,,,2,2,0,0,0.0,1.0,5,2.0,0.4,0.6
        49234533,"Decker, Adem",,,0,0,0,,0,0,,,0,0,0,,,,0,0,0,,"A, D, E","A, D, E",2,0,2.0,2.0,1.0,0.0,,,1,1,0,0,0.0,1.0,,,2,2,0,0,0.0,1.0,5,2.0,0.4,0.6
        ```

Good job!

!!! error "TODO: link final example zip file"
