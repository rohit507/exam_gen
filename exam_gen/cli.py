#!/usr/bin/env python3

import importlib
import os
import pkgutil
import runpy
import sys

exam_root = 'exam.py'

def main():

    if os.path.exists(exam_root):
        # TODO:
        #   Add a file finder relative to this directory
        #   Add a path entry finder relative to the directory
        #   load the module w/ runpy and then futz with the globals
        module = runpy.run_path(exam_root)
        print(module)
        # for i in pkgutil.iter_modules(['.']):
        #     print(i)
        #     (loader, _) = i.module_finder.find_loader(i.name)
        #     print(loader)
        #     module = loader.load_module(i.name)
        #     print(module)
        # proj_loader = importlib.machinery.SourceFileLoader('proj','.')
        # print(dir(proj_loader))
        # exam_spec = importlib.util.spec_from_file_location('exam', exam_root)
        # mod = proj_loader.create_module(exam_spec)
        # print(mod)

        # exam_result = proj_loader.exec_module(mod)
        # print(exam_result)
        # # exam_spec = importlib.machinery.PathFinder.find_spec('proj')
        # print(exam_spec)
        # print(dir(exam_spec))
        # # print(exam_spec.__dict__)
        # # print(exam_spec.loader.__dict__)
        # # exam_module = importlib.util.module_from_spec(exam_spec)
        # exam_module = importlib.import_module('.exam',package='')
        # print(exam_module.__package__)
        # print(dir(exam_module))

    #import doit
    #doit.run(globals())
    # go through the cwd read in all the available files and generate the
    # different tasks.
    # Basically, you should be able to derive all the task info with the
    # various classes. Instantiating the objects themselves should wait until
    # you're specializing them for a student.


def run_cli(global_vars):
    print(global_vars)


# def task_hello():
#     """hello task desription"""

#     def python_hello(targets):
#         with open(targets[0], "a") as output:
#             output.write("#2 Python says Hello World!!!\n")

#     return {
#         'actions': [python_hello],
#         'targets': ["hello.txt"],
#         }

# def _t_ask_new_exam():
#     """
#     Create a new exam with either default values, a little wizard, or
#     command line flags.

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

#     """
#     pass

# def _task_new_question():
#     """
#     Creates a new question and possibly adds it to the exam loader
#     """
#     pass

# def _task_dump_templates():
#     """
#     Dump the stored default templates to an intermediate dir and update the
#     root configuration to point to the dumps
#     """
#     pass

# def _task_validate_exam():
#     """
#     Will exec an exam multiple times w/ random inputs to catch errors
#     """
#     pass

# def _task_validate_question():
#     """
#     Will exec a question w/ a whole bunch of random inputs to catch errs
#     """
#     pass

# def _task_build_exam():
#     """
#     Used to build exams for:
#       - sample
#       - indiv. students
#       - bulk students

#     In formats:
#       - Base Exam
#       - Solution Key
#     """
#     pass

# def _task_build_question():
#     """
#     Used to build single question exams for:
#       - sample
#       - indiv. students
#       - bulk students

#     In formats:
#       - Base Exam
#       - Solution Key
#     """
#     pass

# def _task_grade_exam():
#     """
#     Will read in answers and exam data, produce grades where possible.

#     Can be done in bulk or by student. Prints outputs to stdout as well as to
#     file.
#     """
#     pass
