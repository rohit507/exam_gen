#!/usr/bin/env python3

import sys
import inspect
from exam_gen.exam import Exam
from doit.doit_cmd import DoitMain

exam_root = 'exam.py'


def main():
    """
    The entry point for the exam_gen command line interface.
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

      global_vars: The local namespace that will be searched for
    """
    # var_opts = get_var_opts(global_vars)
    exam = get_exam(global_vars)
    builder = exam.builder(exam)
    sys.exit(DoitMain(builder).run(sys.argv[1:]))

def get_var_opts(global_vars):
    """
    Pulls any settings information from the global variables if need be
    """
    return {}

def get_exam(global_vars):
    """
    Gets the exam class from the set of global variables
    """
    exam = None
    for (k, v) in global_vars.items():
        if inspect.isclass(v) and issubclass(v, Exam) and v != Exam:
            assert (exam == None), ("Found multiple potential exam classes in"+
                                    " file, should only ever have one")
            exam = v
    assert (exam != None), ("Found no potential exams in file, need one.")
    return exam
