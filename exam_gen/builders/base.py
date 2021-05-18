from pprint import *
import attr
import exam_gen.util.logging as logging
from doit.task import dict_to_task
from doit.cmd_base import TaskLoader2
import jinja2
import doit.loader as doit
import inspect
import yaml
import textwrap
import os
from pathlib import *

import exam_gen.builders.task_gen as task_gen
from exam_gen.mixins.with_options import WithOptions
from exam_gen.mixins.path_manager import PathManager

log = logging.new(__name__, level="WARNING")

exam_formats = ['exam', 'solution']

@attr.s
class Builder(TaskLoader2, PathManager, WithOptions):
    """
    """

    exam = attr.ib()
    """
    The exam class that w
    """

    @exam.validator
    def __exam_validator(self, attribute, value):
        if not inspect.isclass(value):
            raise TypeError("`exam` parameter to a builder must be a class")


    data_dir = attr.ib(default='~data', kw_only=True)
    build_dir = attr.ib(default='~build', kw_only=True)
    out_dir = attr.ib(default='~out', kw_only=True)

    class_prefix = attr.ib(default='class-', kw_only=True)
    student_prefix = attr.ib(default='student-', kw_only=True)
    exam_prefix = attr.ib(default='exam-', kw_only=True)
    question_prefix = attr.ib(default='question-', kw_only=True)

    roster_file = attr.ib(default='roster.yaml', kw_only=True)
    student_data_file = attr.ib(default='data.yaml', kw_only=True)
    setup_log_file = attr.ib(default='setup_build.log.yaml', kw_only=True)
    generate_log_file = attr.ib(default='gen_files.log.yaml', kw_only=True)
    generate_out_file = attr.ib(default='gen_files.out.yaml', kw_only=True)

    def __attrs_post_init__(self):

        self.parent_path = Path(inspect.getsourcefile(self.exam)).parent

        if hasattr(super(),'__attrs_post_init__'):
            super().__attrs_post_init__()

    def setup(self, opt_values): pass

    def load_doit_config(self):
        return {'verbosity': 2,
                'default_tasks':[]}

    def load_tasks(self, cmd, pos_args):
        task_list = list()
        task_list += self.parse_roster_tasks()
        task_list += self.clean_working_dirs()
        task_list += self.exam_build_setup_tasks('test-format')
        task_list += self.exam_build_files_tasks('test-format')


        return task_list

    def clean_working_dirs(self):
        """
        Todo: fix so it works relative to `self.root_dir`
        """

        return [doit.dict_to_task({
            'name':'cleanup',
            'actions':["rm -rf ~*"],
            'doc':"Clean all generated files. (i.e. 'rm -rf ~*')"
        })]

    classroom_cache = attr.ib(default=None, init=False)
    "Cache for class objects"

    def classrooms(self):
        if self.classroom_cache == None:
            self.classroom_cache = dict()
            for (class_name, class_init) in self.exam.classes.items():
                self.classroom_cache[class_name] = class_init(builder=self)

        return self.classroom_cache

    def parse_roster_tasks(self):
        """
        Creates the doit tasks to parse the roster with.
        """

        def build_roster(class_name, class_obj):
            """
            The actual command that's run to generate the roster files
            """

            roster_path = Path(self.class_data_path(class_name),
                               self.roster_file)

            roster_data = class_obj.roster_data()

            self.write_class_roster(roster_path, roster_data)

            for (student_id, student_data) in roster_data.items():

                student_data_path = Path(
                    self.student_data_path(class_name, student_id),
                    self.student_data_file)

                student_data['ident'] = student_id

                self.write_student_data(student_data_path, student_data)

        return task_gen.build_task_group(
                  task_prefix = 'parse_roster',
                  group_data = self.classrooms(),
                  run_task = build_roster,
                  task_doc = 'Parse all class rosters.')

    def write_class_roster(self, roster_path, roster_data):
        roster_path.parent.mkdir(parents=True, exist_ok=True)
        roster_file = roster_path.open(mode='w')
        roster_file.write(yaml.dump(roster_data))
        roster_file.close()


    def write_student_data(self, student_path, student_data):
        student_path.parent.mkdir(parents=True, exist_ok=True)
        data_file = student_path.open(mode='w')
        data_file.write(yaml.dump(student_data))
        data_file.close()

    def data_path(self):
        return Path(self.root_dir, self.data_dir)

    def class_data_path(self, class_name):
        return Path(self.data_path(),
                    self.class_prefix + class_name)

    def student_data_path(self, class_name, student_id):
        return Path(self.class_data_path(class_name),
                    self.student_prefix + student_id)

    def exam_data_path(self, class_name, student_id, exam_format):
        return Path(self.student_data_path(class_name, student_id),
                    self.exam_prefix + exam_format)

    def question_data_path(self, class_name, student_id, question_format):
        return Path(self.student_data_path(class_name, student_id),
                    self.question_prefix + question_format)

    def build_path(self):
        return Path(self.root_dir, self.build_dir)

    def class_build_path(self, class_name):
        return Path(self.build_path(),
                    self.class_prefix + class_name)

    def student_build_path(self, class_name, student_id):
        return Path(self.class_build_path(class_name),
                    self.student_prefix + student_id)

    def exam_build_path(self, class_name, student_id, exam_format):
        return Path(self.student_build_path(class_name, student_id),
                    self.exam_prefix + exam_format)

    def question_build_path(self, class_name, student_id, question_format):
        return Path(self.student_build_path(class_name, student_id),
                    self.question_prefix + question_format)


    def exam_build_setup_tasks(self, exam_format, build_settings=None):
        """
        """


        def exam_task(class_name,
                      student_id,
                      class_obj,
                      data_dir,
                      build_dir):

            exam = self.exam(student_id, class_obj)
            setup_log = exam.setup_build_dir(
                data_dir, build_dir, build_settings)

            log_path = Path(data_dir, self.setup_log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_file = log_path.open(mode='w')
            log_file.write(yaml.dump(setup_log))
            log_file.close()

        return task_gen.build_exam_task(
            classrooms = self.classrooms(),
            task_prefix = "setup_build_dir",
            exam_format = exam_format,
            exam_task = exam_task,
            task_doc = 'Set up build directories.',
            subtask_doc = 'Set up build directories for class {}.')

    def exam_build_files_tasks(self, exam_format, build_settings=None):

        append_format = lambda t, e_f = exam_format: "{}:{}".format(t, e_f)

        def exam_task(class_name,
                      student_id,
                      class_obj,
                      data_dir,
                      build_dir):

            exam = self.exam(student_id, class_obj)
            (gen_out, gen_log) = exam.generate_build_files(
                data_dir, build_dir, build_settings)

            out_path = Path(data_dir, self.generate_out_file)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_file = out_path.open(mode='w')
            out_file.write(yaml.dump(gen_out))
            out_file.close()

            log_path = Path(data_dir, self.generate_log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_file = log_path.open(mode='w')
            log_file.write(yaml.dump(gen_log))
            log_file.close()


        return task_gen.build_exam_task(
            classrooms = self.classrooms(),
            task_prefix = "generate_files",
            exam_format = exam_format,
            exam_task = exam_task,
            task_doc = 'Generate files for building exams',
            subtask_doc = 'Generate files for class {}\'s exams.',
            student_task_deps = ['setup_build_dir']
        )
