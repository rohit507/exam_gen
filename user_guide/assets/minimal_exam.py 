#!/usr/bin/env -S pipenv run python3

from exam_gen import *

class MyExam(LatexDoc, Exam):

    classes = {}

    questions = {}

    intro.text = r'''
    \emph{Example Exam Introduction}
    '''

    def user_setup(self, **kwargs):
        pass

if __name__ == "__main__": run_cli(globals())