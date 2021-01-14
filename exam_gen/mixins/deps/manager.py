import inspect
import textwrap
from copy import *
from pprint import *

import attr

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

# task has:
#   actions: callables or commands
#   targets: output files or data
#   file_dep: dependent filenames
#   task_dep: dependent tasks
#   name: name to be shown
#   doc: documentation



class TaskManager():
    task_basename = attr.ib(default="")
    tasks = attr.ib(factory=list)
    sub_managers = attr.ib(factory=dict)
    file_search_path = attr.ib(factory=list)
    data_dir = attr.ib(default="")
    build_dir = attr.ib(default="")

    def collect_init_tasks(): pass

    def generate_task_list(): pass

    def build_task(
            name = "",
            action = [],
            dependencies = [],
            targets = [],
            clean = False,
            hidden = False,
    ): pass

    def data_task(
            name = "",
            dependencies = [],
            targets = [],
            hidden = False,
    ): pass
