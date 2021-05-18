from pprint import *
import exam_gen.util.logging as logging
import doit.task as doit
import doit.loader as doit
import inspect
import textwrap
import os
import functools
from copy import *
from typing import *
from pathlib import *


log = logging.new(__name__, level="WARNING")

def build_task_group(task_prefix : str,
                     group_data : dict,
                          run_task : Callable,
                          task_doc : str = "",
                          mapped_task_deps : List[str] = None,
                          task_fields : dict = None):
    """
    Create a task for each entry in a dictionary.

    Parameters:

       task_prefix : the prefix of the task name

       task_doc : documentation for the root task

       group_data : the dict from subtask_prefix to subtask_data

       run_task : Function with sig
          `(subtask_prefix : str, subtask_data : Any) -> None` that should be
          run when the task is executed.

       mapped_task_deps : A list of task prefixes that each subtask
          should depend on. These will have the student id added as a suffix
          before being added to `task_dep`. Used to chain

       task_fields : Other fields to be added to each student task that's
          generated.
    """

    return doit.generate_tasks(
        "build_task_group({})".format(task_prefix),
        build_task_group_iter(
            task_prefix,
            group_data,
            run_task,
            task_doc,
            mapped_task_deps,
            task_fields))

def build_task_group_iter(task_prefix : str,
                     group_data : dict,
                     run_task : Callable,
                     task_doc : str = "",
                     mapped_task_deps : List[str] = None,
                     task_fields : dict = None):
    """
    Create a list of task dicts. See `build_task_group` for parameter details.
    """

    # Create the root task for the class
    yield {
        'basename' : task_prefix,
        'name': None,
        'actions': None,
        'doc': task_doc
        }

    # Walk over students generating a new task for each
    for (subtask_prefix, subtask_data) in group_data.items():

        # modify student_task_deps
        append_subtask = lambda t, s_p = subtask_prefix: "{}:{}".format(t,s_p)


        new_task_deps = list()
        new_task_fields = dict()

        if task_fields != None:
            new_task_fields = deepcopy(task_fields)

        # map any neccesary fields and
        if mapped_task_deps != None:
            new_task_deps = list(map(append_subtask, mapped_task_deps))


            if 'task_dep' in new_task_fields:
                new_task_deps += deepcopy(new_task_fields['task_dep'])

            new_task_fields['task_dep'] = new_task_deps

        # partially apply the subtask parameters
        fixed_task = functools.partial(run_task, subtask_prefix, subtask_data)

        # yield task dict
        yield { 'basename': task_prefix,
                'name': subtask_prefix,
                'actions': [fixed_task],
                **new_task_fields
        }
        # Python is stupid. See: https://stackoverflow.com/questions/10452770/
        # def student_task(sid = student_id,
        #                  sdata = student_data):
        #     log.debug("running student task %s for student %s",
        #               task_prefix, student_id)

        #     run_student_task(sid, sdata)



def build_all_class_tasks(task_prefix : str,
                          exam_data : dict,
                          run_task : Callable,
                          task_doc : str = "",
                          subtask_doc : str = "",
                          class_task_deps : List[str] = None,
                          student_task_deps : List[str] = None,
                          task_fields : dict = None):
    """
    Builds tasks for all classes in an exam.

    Parameters:

       task_prefix : the prefix of the task name

       exam_data : dictionary where each key is a class_name and the values
          are class_rosters. `class_rosters` are maps from `student_id` to
          `student_data`.

       run_student_task : Function with signature
          `(class_name : str, student_id : str, student_data : Any) -> None`
          that should be run when the task is executed.

       task_doc : documentation for the root task

       subtask_doc : documentation for each class subtask, will be used as
          format string with the class_name as the sole parameter.

       class_task_deps : A list of task prefixes for each student task that
          will have the class name added to the end before being added to
          `task_dep`.

       student_task_deps : A list of task prefixes that each student task
          should depend on. These will have the class name and the
          student id added as a suffixes before being added to `task_dep`

       task_fields : Other fields to be added to each student task that's
          generated.
    """

    task_list = list()
    exam_task_deps = list()

    for (class_name, class_roster) in exam_data.items():

        # Useful function for appending the class name to things
        append_class = lambda t, c_n = class_name: "{}:{}".format(t, c_n)

        # generate new task_prefix
        class_task_prefix = append_class(task_prefix)

        # Generate class task doc, attempt formatting
        class_task_doc = None
        class_task_doc = subtask_doc.format(class_name)

        # Add the new class task to the set of deps for the super task
        exam_task_deps.append(class_task_prefix)

        # Partially apply the class name to the task function
        student_task = functools.partial(run_task, class_name)

        # copy task_feilds
        new_task_fields = dict()
        if task_fields != None:
            new_task_fields = deepcopy(task_fields)

        # Add class suffixes to the student task deps
        new_student_task_deps = list()
        if student_task_deps != None:
            new_student_task_deps = list(map(append_class, student_task_deps))

        # Add class suffixed to the class task deps and add them to the
        # task_fields dictionary
        if class_task_deps != None:
            new_class_task_deps = list(map(append_class, class_task_deps))

            if 'task_dep' in new_task_fields:
                new_class_task_deps += new_task_fields['task_dep']

            if new_class_task_deps != []:
                new_task_fields['task_dep'] = new_class_task_deps

        # Actually generate the tasks for the class and all the students in it.
        task_list += build_task_group(class_task_prefix,
                                             class_roster,
                                             student_task,
                                             class_task_doc,
                                             new_student_task_deps,
                                             new_task_fields)

    # generate the super-task that will perform the action for all classes
    task_list.append(doit.dict_to_task({
            'name' : task_prefix,
            'actions': None,
            'doc': task_doc,
            'task_dep': exam_task_deps
            }))

    return task_list

def build_exam_task(classrooms,
                    task_prefix,
                    exam_format,
                    exam_task,
                    task_doc = "",
                    subtask_doc = "",
                    log_file_name = None,
                    class_task_deps = None,
                    student_task_deps = None,
                    task_fields = None):
    """
    Generates a set of build tasks that each require initializing an exam
    object and sticking logging data somewhere. Will chdir into the build
    directory before running the `exam_task` function.

    Arguments:

        classrooms: dict of class_name to class_obj


        task_prefix: the string that tells us what type of exam format we have

        exam_task: function with signature
          `(class_name, student_id, class_obj, data_dir, build_dir) -> dict`
          that initializes and performs the task. Should return a log
          dictionary.

        task_doc: root task documentation

        subtask_doc: class task doumentation

        log_file_name: The name of the output logfile

        mapped_task_deps:
    """

    append_format = lambda t, e_f = exam_format: "{}:{}".format(e_f, t)

    exam_data = dict()

    for (class_name, class_obj) in classrooms.items():
        exam_data[class_name] = dict()
        for student_id in class_obj.students():
            exam_data[class_name][student_id] = class_obj


    def build_task(class_name, student_id, class_obj):

        data_dir  = class_obj.builder.exam_data_path(
            class_name, student_id, exam_format)
        build_dir = class_obj.builder.exam_build_path(
            class_name, student_id, exam_format)


        build_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)

        cwd = Path.cwd()
        os.chdir(build_dir)

        log = exam_task(class_name,
                        student_id,
                        class_obj,
                        data_dir,
                        build_dir)

        os.chdir(cwd)

        if log_file_name != None:
            log_file = Path(data_dir,log_file_name).open(mode='w')
            log_file.write(yaml.dump(log))
            log_file.close()

    if class_task_deps != None:
        class_task_deps = list(map(append_format,class_task_deps))

    if student_task_deps != None:
        student_task_deps = list(map(append_format,student_task_deps))

    return build_all_class_tasks(
        task_prefix = append_format(task_prefix),
        exam_data  = exam_data,
        run_task = build_task,
        task_doc = task_doc,
        subtask_doc = subtask_doc,
        class_task_deps = class_task_deps,
        student_task_deps = student_task_deps,
        task_fields = task_fields)
