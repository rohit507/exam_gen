import attr

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

class Exam():
  """
  Base class for all concrete exams

  TODO
  """
  pass

  @classmethod
  def get_task_loader(cls, cwd='.'):
      """
      Returns a new doit taskloader based on the settings for this class.
      """
      pass
