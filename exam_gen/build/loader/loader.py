
import attr
import inspect
import textwrap
import functools

from copy import *
from pprint import *
from pathlib import *

from ..data import BuildInfo

from doit.cmd_base import TaskLoader2
from doit.task import dict_to_task

from .task_generators import *
from .roster_tasks import *
from .build_tasks import *
from .grade_tasks import *

from exam_gen.util.with_options import WithOptions
from exam_gen.util.file_ops import *

import exam_gen.util.logging as logging

log = logging.new(__name__, level="WARNING")

@attr.s
class BuildLoader(TaskLoader2, WithOptions):

    exam = attr.ib()
    """
    The root exam we're to be building
    """

    build_info = attr.ib(factory=BuildInfo, kw_only=True)

    proj_root = attr.ib(init=False)
    cmd = attr.ib(init=False)
    pos_args = attr.ib(init=False)

    @proj_root.default
    def _init_proj_root(self):
        return Path(inspect.getsourcefile(self.exam)).parent

    def __attrs_post_init__(self):
        if hasattr(super(), '__attrs_post_init__'):
            super().__attrs_post_init__()

        self.build_info.root_dir = self.proj_root

    def setup(self, opt_values): pass

    def load_doit_config(self):
        return {'verbosity': 2,
                'default_tasks':['_help_msg']}

    def load_tasks(self, cmd, pos_args):
        self.cmd = cmd
        self.pos_args = pos_args
        tasks = list()
        tasks += self.help_task()
        tasks += self.clean_task()
        tasks += self.roster_parse_tasks()
        tasks += self.build_exam_tasks()
        tasks += self.build_solution_tasks()
        tasks += self.calculate_grade_tasks()
        return tasks

    def help_task(self):

        def print_msg(): print(textwrap.dedent(
            """
            exam_gen build tool

            Available Commands:
              <cmd_name> list          List major available build actions.
              <cmd_name> list --all    List all available build actions.

            Replace <cmd_name> with however you invoke this tool.
            (usually `./exam.py`,`pipenv run ./exam.py`,or `pipenv run python3 exam.py`)
            """
        ))

        return [dict_to_task({
            'name': '_help_msg',
            'actions': [print_msg]
            })]

    def clean_task(self):
        return [dict_to_task({
            'name': 'cleanup',
            'actions': [functools.partial(
                delete_folders,
                self.build_info.data_dir,
                self.build_info.build_dir,
                self.build_info.out_dir)],
            'doc': "Clean all generated files. (e.g. 'rm -rf ~*')"
            })]

    def roster_parse_tasks(self):

        classes = {k:
                   self.build_info.where(class_name = k,
                                         classroom = class_init(
                                             exam=self.exam,
                                             parent_path=self.proj_root))
                   for (k,class_init) in self.exam.classes.items()}

        def drop_return(a,b):
            get_roster_data(a,b)
            return None

        return build_task_group(
            task_prefix = "parse-roster",
            task_doc = ("parse the class rosters (incl. answer and score data "
                        "if available)"),
            group_data = classes,
            run_task = drop_return)

    def calculate_grade_tasks(self):

        classes = {k:
                   self.build_info.where(
                       class_name = k,
                       exam_format = "grades",
                       classroom = class_init(
                           exam=self.exam,
                           parent_path=self.proj_root
                       )
                   )

                   for (k,class_init) in self.exam.classes.items()}

        def drop_return(a,b):
            calculate_grades(a,b)
            return None

        return build_task_group(
            task_prefix = "calculate-grades",
            task_doc = ("Calculates the grades for the classroom."),
            group_data = classes,
            run_task = drop_return)

    def build_exam_tasks(self):

        exam_data = dict()

        build_info = self.build_info.where(exam_format = "exam")

        for (class_name, class_init) in self.exam.classes.items():

            class_obj = class_init(exam = self.exam,
                                   parent_path = self.proj_root)

            class_bld = build_info.where(class_name = class_name,
                                         classroom = class_obj)

            class_obj = get_roster_data(
                class_name,
                class_bld
            )

            exam_data[class_name] = dict()

            for (student_id, student) in class_obj.students.items():

                student_bld = class_bld.where(student_id = student_id,
                                              student = student)

                exam_data[class_name][student_id] = student_bld

        def drop_return(*vargs, **kwargs):
            build_exam(*vargs, **kwargs)
            return None

        return build_all_class_tasks(
            task_prefix = "build-exam",
            exam_data = exam_data,
            run_task = functools.partial(drop_return, self.exam),
            task_doc = "Build all the exams for each student.",
            subtask_doc = "Build the exams for class '{}'.")


    def build_solution_tasks(self):

        exam_data = dict()

        build_info = self.build_info.where(exam_format = "solution")

        for (class_name, class_init) in self.exam.classes.items():

            class_obj = class_init(exam = self.exam,
                                   parent_path = self.proj_root)

            class_bld = build_info.where(class_name = class_name,
                                         classroom = class_obj)

            class_obj = get_roster_data(
                class_name,
                class_bld,
                load_answers=True
            )

            exam_data[class_name] = dict()

            for (student_id, student) in class_obj.students.items():

                student_bld = class_bld.where(student_id = student_id,
                                              student = student)

                exam_data[class_name][student_id] = student_bld

        def drop_return(*vargs, **kwargs):
            build_exam(*vargs, **kwargs)
            return None

        return build_all_class_tasks(
            task_prefix = "build-solution",
            exam_data = exam_data,
            run_task = functools.partial(drop_return, self.exam),
            task_doc = "Build all the answer keys for each student.",
            subtask_doc = "Build the answer keys for class '{}'.")

    def build_tasks(self, exam_format, **build_settings):
        """
        Runs the build process for each student in the set.

        some set/subset of:

         - obj.init_document()
         - distribute_answers(obj, answers)
         - distribute_grades(obj, grades)
         - obj.setup_build()
         - build_template_spec(obj.template_spec())
         - finalize_build()
         - output_build()

        with options based on document version and the like.

        So for now, there's a few key tasks:

         - build-exam
         - build-solutions
         - generate-results

        """
        pass
