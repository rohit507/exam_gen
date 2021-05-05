
import attr
import exam_gen.util.logging as logging
from doit.task import dict_to_task
from doit.cmd_base import TaskLoader2
import doit.loader as doit
import os
import yaml

log = logging.new(__name__, level="DEBUG")

@attr.s
class Builder(TaskLoader2):
    """
    Describes how to build the various targets
    """

    exam = attr.ib(default=None)
    template_dir = attr.ib(default='templates', kw_only=True)
    data_dir = attr.ib(default='~data', kw_only=True)
    build_dir = attr.ib(default='~build', kw_only=True)
    out_dir = attr.ib(default='~out', kw_only=True)

    @classmethod
    def with_options(cls, **kwargs):
        """
        Create a new constructor function w/ some kw-arguments curried in.
        """
        def init_bld(*vargs, **kwargs2):
            return cls(*vargs, **dict(kwargs, **kwargs2))

        return init_bld

    def load_exam(self, exam):
        self.exam = exam
        return self

    def setup(self, opt_values):
        pass

    def load_doit_config(self):
        return {'verbosity': 2}

    def load_tasks(self, cmd, pos_args):
        task_list = list()
        task_list += doit.generate_tasks(
            "parse_roster_tasks", self.parse_roster_tasks())

        return task_list

    def get_classrooms(self, exam):
        """
        Get the list of classrooms for this exam
        """
        return exam.classes

    def get_versions(self, exam):
        """
        Get the list of exam versions (i.e. exam, solutions, graded, etc...)
        """
        return ['exam','solution']

    def get_questions(self, exam):
        """
        Gets the list of questions in the exam.
        """
        return exam.questions

    def parse_roster_tasks(self):


        basename = 'parse_roster'

        yield {
            'basename' : basename,
            'name': None,
            'actions': None,
            'doc': 'Parse all class rosters.'
            }

        for clsrm in self.get_classrooms(self.exam):
            name = clsrm.class_name

            print(clsrm.parse_roster())

            def print_data(cls=clsrm):
                roster_data = cls.parse_roster()
                print(roster_data)
                self.write_class_data(name, roster_data)
                for (sid, dat) in roster_data.items():
                    self.write_student_data(sid, dat)

            yield { 'basename': basename,
                    'name': name,
                    'actions': [print_data] }

    def write_class_data(self, name, data):
        class_dir = self.data_dir + '/class-' + name
        roster_path = class_dir + '/roster.yaml'

        os.makedirs(class_dir, exist_ok=True)
        roster_file = open(roster_path, 'w')
        roster_file.write(yaml.dump(data))
        roster_file.close()

    def write_student_data(self, sid, data):
        student_dir = self.data_dir + '/student-' + sid
        data_path = student_dir + '/data.yaml'

        os.makedirs(student_dir, exist_ok=True)
        data_file = open(data_path, 'w')
        data_file.write(yaml.dump(data))
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
