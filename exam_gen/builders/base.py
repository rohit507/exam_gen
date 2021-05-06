
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

log = logging.new(__name__, level="DEBUG")

@attr.s
class Builder(TaskLoader2):
    """
    """

    exam = attr.ib(default=None)

    root_dir = attr.ib(factory=Path.cwd, kw_only=True)

    template_dir = attr.ib(default='templates', kw_only=True)
    template_loader = attr.ib(default=None, kw_only=True)

    data_dir = attr.ib(default='~data', kw_only=True)
    build_dir = attr.ib(default='~build', kw_only=True)
    out_dir = attr.ib(default='~out', kw_only=True)

    class_prefix = attr.ib(default='class-', kw_only=True)
    student_prefix = attr.ib(default='student-', kw_only=True)

    roster_file = attr.ib(default='roster.yaml', kw_only=True)
    student_data_file = attr.ib(default='data.yaml', kw_only=True)


    def __attrs_post_init__(self):
        if self.template_loader == None:
            self.template_loader = self.init_template_loader()

    def init_template_loader(self):
        """
        The default template loader will look in order at:

          - `<root_dir>/<template_dir>`
          - `<package_root>/template`

        Override to change where templates are looked for.
        """
        return jinja2.ChoiceLoader([
            jinja2.FileSystemLoader(self.root_dir / self.template_dir),
            jinja2.PackageLoader('exam_gen')
            ])

    def load_exam(self, exam):
        self.exam = exam

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

        for clsrm in self.exam.classes:

            def gen_class_roster(cls=clsrm):

                roster_path = Path(
                    self.root_dir,
                    self.data_dir,
                    self.class_prefix+cls.name,
                    self.roster_file)

                roster_data = cls.parse_roster(self)


                for (student_id, student_data) in roster_data.items():
                    student_path = Path(
                        self.root_dir,
                        self.data_dir,
                        self.student_prefix+student_id,
                        self.student_data_file)

                    student_data['ident'] = student_id

                    self.write_student_data(student_path, student_data)

                self.write_class_roster(roster_path, roster_data)

            yield { 'basename': basename,
                    'name': clsrm.name,
                    'actions': [gen_class_roster] }

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
