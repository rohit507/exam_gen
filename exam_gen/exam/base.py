import attr

import exam_gen.util.logging as logging
from exam_gen.builders import *
from exam_gen.mixins.config import *
from exam_gen.mixins.path_manager import PathManager
from exam_gen.exam.metadata import *

log = logging.new(__name__, level="DEBUG")

@attr.s
class Exam(ExamSettings, ExamMetadata, PathManager):
  """
  Base class for all concrete exams, should be overridden

  TODO

    - People define the options for this thing.
    - It gets instantiated with information on a student that's then
      propagated down to the questions.

    - Has metadata and settings
    - Has a set of sub-questions

    - Need: Tasks to generate intermediate data and files given:
      - Metadata on exam and question

    - Focus 1: Files and file environments:
      -
  """

  classes = attr.ib(factory=dict, kw_only=True)
  """
  The dict of classes, with students and stuff, that we can perform operations
  over
  """

  questions = dict()
  """
  The dict of questions that are to be included in the exam
  """

  use_class_root = True


  # student_data = attr.ib()
  # """
  # Information about the student that we're being instantiated with.
  # """

  # grade_data = attr.ib(default=None)
  # answer_data = attr.ib(default=None)
  # exam_data = attr.ib(default=None)

  # def setup_build(self, builder, build_dir, build_type):
  #   """
  #   Does various things needed
  #   """
  #   pass

  # def gen_build(self, builder, build_dir, build_type):
  #   pass

  # def run_build(): pass

  # pass
