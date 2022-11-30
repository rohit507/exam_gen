#!/usr/bin/env python3

import sys
import inspect
import os

from pathlib import *

from .loader import BuildLoader

from exam_gen.exam import Exam
from doit.doit_cmd import DoitMain

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

exam_root = 'exam.py'

def main():
    """
    The entry point for the exam_gen command line interface.

    !!! important "Currently does nothing."

    !!! todo "Todo: Create a new assignment and other utility functions."
    """
    pass

def run_cli(global_vars):
    """
    The entry point for when we're using `exam_gen` as a pure library.

    Should be used in `exam.py` as follows:
    ```python
    if __name__ == "main": run_cli(globals())
    ```

    Parameters:

      global_vars: The local namespace to build a cli around.
    """
    # var_opts = get_var_opts(global_vars)
    exam = get_exam(global_vars)
    builder = BuildLoader(exam)
    sys.exit(DoitMain(builder).run(sys.argv[1:]))

def get_var_opts(global_vars):
    """
    Pulls any settings information from the global variables.

    !!! important "Currently does nothing."

    Parameters:

      global_vars: The local namespace which contains options.
    """
    return {}

def get_exam(global_vars):
    """
    Parses through a list of global variables to find the `Exam` subclass
    that we're going to be building.

    Parameters:

      global_vars: The local namespace that will be searched in order to find
        an `Exam`.

    """
    exam = None
    source_file = Path(global_vars['__file__'])

    for (k, v) in global_vars.items():
        if (inspect.isclass(v)
            and issubclass(v, Exam)
            and v != Exam
            and Path(inspect.getsourcefile(v)) == source_file):
            assert (exam == None), ("Found multiple potential exam classes in"+
                                    " file, should only ever have one")
            exam = v
    assert (exam != None), ("Found no potential exams in file, need one.")
    return exam
