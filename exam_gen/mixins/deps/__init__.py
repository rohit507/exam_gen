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

I wish python made this easier for me.

And what sort of features could it take?

  - References to parent tasks.
  - References to child tasks, that are associated with something or another.
    and the overloading of tasks where needed.
  - Each object being a `taskable` entity that can hold a number of specific
    tasks, potentially additional internal taskable objects, and reference
    parent and child task_sets.
  - A task generator that can be called after some other tasks have run and
    produce something useful.
  - Registration for tasks of various sorts that's available as a decorator or
    some such.

Types of tasks:

  - File Tasks
  - Python Object Manipulation / Data Processing tasks

So two types of structural heirarchies in design:

  - File/Directory Hierarchies
      - <exam_defs> : python files
      - templates/ : template files
      - assets/ : asset files
      - <class>/ : class directories
          - class_settings.py : settings for this class.
          - <roster> : roster files
          - <answers> : provided answers
          - <grade> : raw grades
          - _data : generated intermediate data files
              - <parsed roster> : parsed roster data
              - <parsed answer> : parsed answer data
              - <parsed grade> : parsed grade data
              - <per-student>/: student specific data
          - _build : generated intermediate build files
              - <per-student build>: student specific build data
          - _output : final output files
              - <grade csv> : final grades
              - <build-type>/ : folder for collected pdfs of some type of
                   output.

  - Exam Structure Hierarchies: Each of these can be instantiated with some
    combo of (student, build type, output type, other meta info, etc..)
      - Exam: Base Exam
           - Section: Base Subsection
               - Problem: Base Problem

In general when we run a task set on an exam, it'll be producing output that
goes in the `_data/`, or `_build/` directories for said task.

We'll also have larger tasks that collate that data or work on a larger scale
to produce various grouped output of one sort or another that will generally
be poking into other directories.

So, what operations will we have?

   - Generate PDFs:
       - Student specific exams as a bundle or singletons
       - Potentially some meta PDFs for various purposes
   - Generate Grades:
       - Again as a bundle or singletons
   - Generate Random Things: (for testing purposes)
       - Full Tests
       - Single Problems, etc.
       - Single Exams, etc.
   - Validate Things:
       - Esp. Randomly generated problems or grading.

So let's take a look at task init process maybe w/ subproblems:

   - Task to parse input data from a class-level source.
   - Generate set of subtasks from that class level information for each
     student and other subtargets. (Requires parsing of available data files
     to get lists of students, but that should be it?) (Using create_after
     and target_regex this should be able to be triggered only when
     we're trying to build something involving a student)
       - Generate tasks to get student specific data where possible but
         these are designed so they can fail.
       - So for each student we setup data_tasks (which read and write from
         the _data dir) and are used to instantiate the corresponding exam
         object as needed.
       - Then we instantiate build tasks (which shouldn't need any specific
         information from the data tasks.)
   - Then we instantiate the tasks for the grouped operations now that we have
     the list of students. (Probably needs something to ensure that it
     doesn't choke when dependencies fail)

So what does this mean for our little mixin class?

   - It needs to let us create tasks that can be specialized to fit a
     particular student/instantiation parameter.
   - Build tasks shouldn't directly call data tasks and instead ask
     for some data term to be well defined, and that is defined as a task
     of some sort.
   - Build tasks asking for a file or a template should trigger tasks that
     link things from the root folder.
   - Data tasks should be able to ask for files from the data directory and
     have them autolinked when possible.
   - Library users should only ever need access to base tasks in order to
     create files and stuff.
   - Data tasks are based on using getargs and need some way to keep their
     nesting terms in order.

The fundamental problem here is dependency hierarchies and the rewriting of
actions so that they respect the group structure.

I guess the question now is whether I want to do this at all? I mean it's a
minor improvement over the basic imperative process for very little positive
value. Maybe? Pfeh.

"""
