import attr

import exam_gen.util.logging as logging
import exam_gen.builders

log = logging.new(__name__, level="DEBUG")

@attr.s
class Exam():
  """
  Base class for all concrete exams

  TODO
  """

  builder = attr.ib(factory=exam_gen.builders.Builder)
  """
  The class that defines how to construct a particular exam, as well as
  some other things.
  """

  classes = None
  """
  The list of classes, with students and stuff, that we can perform operations
  over
  """

  questions = None
  """
  The list (tree?) of questions that are to be included in the exam
  """


  pass
