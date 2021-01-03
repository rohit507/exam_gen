import attr
import inspect
import textwrap
from pprint import *
from copy import *
import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

# task has:
#   actions: callables or commands
#   targets: output files or data
#   file_dep: dependent filenames
#   task_dep: dependent tasks
#   name: name to be shown
#   doc: documentation

DOIT_CONFIG = {'action_string_formatting': 'both'}

"""
So what do I want out of the deps management stuff?

  - Format the internal processing of an object as a set of dependency managed
    tasks, each of which can potentially use a file as an intermediary:

      - A: Run User Init (deps: E, F)
      - B: Render Template (Deps: C, D)
           - B1: Base (Deps: A, B)
           - B2: Solutions (Deps: A, B)
           - B3: Answered (Deps: A, B Has_Answer)
           - B4: Graded (Deps: A, B, Has_Answer, Has_Grade)
      - C: Init Required Files (Deps: C1, C2)
           - C1: Copy Assets from Base Dir (Deps: A)
           - C2: Generate Neccesary Assets from User Code (Deps: A, C1)
      - D: Render Sub-Templates (Deps: A, possibly C, more in sub-templates)
      - E: RNG Init (Deps: F)
      - F: Class Init

  - Nice CLI that lists all the available tasks in a good format, something
    like having tasks for `<class>:<student>:test.pdf` or something, and
    having the larger scale management actions just sorta work.

  - Not having to rebuild everything every damn time.

  - I wish python made this easier for me.

"""
