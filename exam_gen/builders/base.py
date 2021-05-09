
import attr
import exam_gen.util.logging as logging
from doit.task import dict_to_task
from doit.cmd_base import TaskLoader2
import jinja2
import doit.loader as doit
import inspect
import yaml
import os
from pathlib import *

from exam_gen.mixins.with_options import WithOptions
from exam_gen.mixins.path_manager import PathManager

log = logging.new(__name__, level="DEBUG")

@attr.s
class Builder(TaskLoader2, PathManager, WithOptions):
    """
    """

    exam = attr.ib()

    data_dir = attr.ib(default='~data', kw_only=True)
    build_dir = attr.ib(default='~build', kw_only=True)
    out_dir = attr.ib(default='~out', kw_only=True)

    class_prefix = attr.ib(default='class-', kw_only=True)
    student_prefix = attr.ib(default='student-', kw_only=True)

    roster_file = attr.ib(default='roster.yaml', kw_only=True)
    student_data_file = attr.ib(default='data.yaml', kw_only=True)

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
        task_list += doit.generate_tasks(
            "clean_working_dirs",self.clean_working_dirs())
        task_list += doit.generate_tasks(
            "parse_roster_tasks", self.parse_roster_tasks())

        return task_list

    def clean_working_dirs(self):
        """
        Todo: fix so it works relative to `self.root_dir`
        """

        return {'basename':'cleanup',
                'actions':["rm -rf ~*"],
                'doc':"Clean all generated files. (i.e. 'rm -rf ~*')"
                }


    def parse_roster_tasks(self):
        basename = 'parse_roster'

        yield {
            'basename' : basename,
            'name': None,
            'actions': None,
            'doc': 'Parse all class rosters.'
            }

        for (classname,clsrm_init) in self.exam.classes.items():

            clsrm = clsrm_init(parent_obj=self)

            def gen_class_roster(cls=clsrm,name=classname):

                roster_path = Path(
                    self.root_dir,
                    self.data_dir,
                    self.class_prefix+name,
                    self.roster_file)

                roster_data = cls.parse_roster(self)


                for (student_id, student_data) in roster_data.items():
                    student_path = Path(
                        self.root_dir,
                        self.data_dir,
                        self.class_prefix+name,
                        self.student_prefix+student_id,
                        self.student_data_file)

                    student_data['ident'] = student_id

                    self.write_student_data(student_path, student_data)

                self.write_class_roster(roster_path, roster_data)

            yield { 'basename': basename,
                    'name': classname,
                    'actions': [gen_class_roster] }

    def write_class_roster(self, roster_path, roster_data):
        roster_path.parent.mkdir(parents=True, exist_ok=True)
        roster_file = roster_path.open(mode='w')
        roster_file.write(yaml.dump(roster_data))
        roster_file.close()

    def read_class_roster(self): pass

    def write_student_data(self, student_path, student_data):
        student_path.parent.mkdir(parents=True, exist_ok=True)
        data_file = student_path.open(mode='w')
        data_file.write(yaml.dump(student_data))
        data_file.close()

    def read_student_data(self, student_path):
        "read information about student taken from roster"
        pass

    def write_student_exam_data(self, student_path):
        """
        write down the exam and question specific data created when
        generating an exam
        """
        pass

    def read_student_exam_data(self, student_path):
        pass

    def write_answer_data(self, answer_path, answer_data):
        """
        write the answers provided by a student to a data file in a
        standard(ish) format.
        """
        pass

    def read_answer_data(self): pass

    def write_grade_data(self, grade_path, grade_data):
        """
        write any user information about grades for a student to a standard
        location.
        """
        pass

    def read_grade_data(self): pass

    def write_result_data(self, result_path, result_data):
        """
        Write the output grades, after any auto-grading, to a standard
        location.
        """
        pass

    def read_result_data(self): pass

    def generate_class_tasks(self, exam, clsrm):
        """
        Should have task for:
          - parse_roster:<class-name> (should create student data)
          - parse_answers:<class-name> (should create student data files)
          - print_grades:<class-name>

        w/ appropriate complete versions
        """
        pass

    def generate_exam_tasks(self, exam):
        """
        Shold have tasks for:
          - validate_exam
        """
        pass

    def generate_question_tasks(self, exam, question):
        """
        should have tasks for:
          - validate_question
        """
        pass

    def setup_exam(self, exam, build_type, student, build_dir, data_dir):
        """
        Sets up the build directory for the exam.
        """
        pass

    def setup_exam_question(self,
                                  exam,
                                      build_type,
                                      question,
                                      student,
                                      build_dir, data_dir):
        """
        Sets up the build directory for a specific question in the exam.
        """
        pass

    def gen_exam(self, exam, build_type, student, build_dir, data_dir):
        """
        runs the code in the exam object to generate source files and stuff.
        """
        pass

    def gen_exam_question(self):
        """
        Runs the code in a question object to generate the corresponding
        source.
        """
        pass

    def build_exam(self):
        """
        Once all the inputs are created, this will run an external tool
        to generate output files.
        """
        pass



    def generate_student_tasks(self, exam, student):
        """
          - _grades:<student>
          - _question_env:<student>:<type>:<question>
          - _exam_env:<type>:<student>
          - _question_bld:<student>:<type>:<question>
          - _exam_bld:<student>:<type>
          - _exam:<student>:<type>
          - _question:<student>:<type>:<question>

        Where <student> can also include a sample student;

        These should all be done with a delayed task that has '*' in the
        student position.
        """
        pass



    """
    Set of neccesary tasks:

    Top Level:

      - Build Exam : { format = Exam | Solutions | Graded | etc...
                        , target = Sample | Class | Student | All ... }

      - Build Question { question = <question name>
                          , others same as exam }

      - Print Grades : { target = Class | Student | All .. }

      - Validate Exam : ...

      - Validate Question : ...

    Lower Level:

      - Parse Roster : Roster -> `data/<class>/roster.yaml`
      - Parse Answers : Answers -> `data/<class>/answers.yaml`
      - Calc Grades : Exam , `answers.yaml` -> `data/<class>/grades.yaml`
      - Gen Student : `roster.yaml` -> `data/<student>/info.yaml`
      - Gen Question : `info.yaml` , Exam + Question , -> `data/<s>/<q>.yaml
      - Gen Exam : Exam ,  `info.yaml`, `<q>.yaml` -> `data/<s>/exam.yaml`
      - Setup Build Question : E + Q, Tmpl , `info.yaml`, `<q>.yaml`
          -> `build/<s>/<q>/*`
      - Setup Build Exam : SetupBQ, E + Q, Tmpl, `info.yaml`, `<q*>.yaml`
          `exam.yaml` -> `build/<s>/<e>/*`
      - Eval Build Question: ...
      - Eval Build Exam: ...
      - Output Build Question: `build/...` -> `output/...`
      - Output Build Exam: `build/...` -> `output/...`
      - Print Grades: `**/grades.yaml` -> `output/<c>-grades.cvs`

#     Each exam has the following structure:
#       - 'exam.py'
#       - ? 'templates/'
#          - ? 'exam/'
#          - ? '*/'
#       - ? 'class-*/'
#          - 'class.py'
#          - some roster
#          - some answers
#       - ? 'question-*/'
#          - 'question.py'
#       - ? 'build/'  : Intermediate build files
#       - ? 'data/'   : Intermediate metadata
#       - ? 'output/' : Output files
    """
