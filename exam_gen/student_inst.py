import attr

import exam_gen.util.logging as logging
from copy import *
import textwrap
import functools
from exam_gen.builders.metadata import Buildable

log = logging.new(__name__, level="DEBUG")

@attr.s
class Document():
    """
    Superclass for documents.

    `Exam` and `Question` are the key inheritors.

    Note: everything that inherits from this can have subques

    Basically, inheriting from this class means that instances if this class
    are tied to the information for a particular student.
    """

    __subdoc_vars__ = []
    """
    list of class variables that can contain subdocument sets.
    """

    subdoc_sets = attr.ib(factory=dict, init=False)
    """
    a dictionary of subdocument sets found within this document

    !!! Important
      This must be set in the class definition, not at runtime or at init.
    """

    subdoc_cache_sets = attr.ib(factory=dict, init=False)
    """
    Different caches for each set of sub-documents.
    """

    def __init_subclass__(cls, *vargs, **kwargs):
        """
        Will go through the variables in subdoc_vars and generate the stub
        properties for each thing.
        """
        super().__init_subclass__(*vargs, **kwargs)

        final_subdoc_vars = list()

        for item in cls.__subdoc_vars__:

            subdoc_var = None
            subdoc_cache_var = None
            subdoc_doc = None
            subdoc_cache_doc = None

            # Parse out subdoc_var fields
            if isinstance(item,str):

                subdoc_var = item

            elif isinstance(item, dict):

                subdoc_var = item['var']
                if 'cache' in item:
                    subdoc_cache_var = item['cache']
                if 'doc' in item:
                    subdoc_doc = textwrap.dedent(item['doc'])
                if 'cache_doc' in item:
                    subdoc_cache_doc = textwrap.dedent(item['cache_doc'])

            else:
                raise RuntimeError("Invalid entry in `__subdoc_vars__`")

            # Get any already set subdoc information
            cls.subdoc_sets[subdoc_var] = getattr(cls, subdoc_var, dict())

            # Create property for the base store
            get_subdoc = functools.partial(
                lambda self, s_v: self.subdoc_sets[s_v],
                s_v = subdoc_var)

            if subdoc_doc != None:
                get_subdoc.__doc__ = subdoc_doc

            setattr(cls, subdoc_var, property(get_subdoc))

            # create property for the cache variable
            if subdoc_cache_var != None:
                get_subdoc_cache = functools.partial(
                    lambda self, sc_v: self.subdoc_cache_sets[sc_v],
                    sc_v = subdoc_cache_var)

                if subdoc_cache_doc != None:
                    get_subdoc_cache.__doc__ = subdoc_cache_doc

                setattr(cls, subdoc_cache_var, property(get_subdoc_cache))

            # add to normalized subdoc list
            final_subdoc_vars.append({
                'var': subdoc_var,
                'cache': subdoc_cache_var,
                'doc': subdoc_doc,
                'cache_doc': subdoc_cache_doc
                })

        # Replace the subdoc vars with the normalized version
        cls.__subdoc_vars__ = final_subdoc_vars



@attr.s
class Personalized():
    """
    Classes that are initialized with information on a specific student.
    """

    student_id = attr.ib()
    """
    The student that this instance of the exam is for.
    """

    classroom = attr.ib()
    """
    The classroom object we're querying for information on a student.
    """

@attr.s
class PersonalDoc(Personalized,Document):
    """
    Will initialize all the different subdocs with the student_id and classroom
    information.
    """

    def __attrs_post_init__(self):

        if hasattr(super(),'__attrs_post_init__'):
            super().__attrs_post_init__()

        for (set_name, subdocs) in self.subdoc_sets.items():
            for(doc_name, doc_init) in subdocs.items():
                doc_obj = doc_init(self.student_id, self.classroom)
                self.subdoc_cache_sets[set_name][doc_name] = doc_obj

@attr.s
class BuildableDoc(Buildable,Document):
    """
    Superclass for things that are instantiated with respect to a single
    student. `Exam` and `Question` are the key inheritors.

    Note: everything that inherits from this can have subquestions

    Basically, inheriting from this class means that instances if this class
    are tied to the information for a particular student.
    """

    def setup_build_dir(self, data_dir, build_dir, build_settings=None):
        """
        Will copy the files mentioned in this exam's `settings.assets` into the
        build directory. Also calls `setup_build_dir` for each question in the
        exam.
        """
        log_data = super().setup_build_dir(data_dir, build_dir, build_settings)

        for (set_name, subdocs) in self.subdoc_cache_sets.items():

            log_data[set_name] = dict()

            for (doc_name, doc_obj) in self.subdocs.items():
                log_data[set_name][doc_name] = doc_obj.setup_build_dir(
                    data_dir,
                    build_dir,
                    build_settings)

        return log_data

    def generate_build_files(self, data_dir, build_dir, build_settings=None):
        """
        Generates new files for the build process.
        """

        # Call super?
        (outputs, log_data) = super().generate_build_files(data_dir,
                                                           build_dir,
                                                           build_settings)

        # Initial setup
        (pre_out, pre_log) = self.start_build_files(
            outputs,
            data_dir,
            build_dir,
            build_settings)

        outputs['pre_build'] = pre_out
        log_data['pre_build'] = pre_log

        # Recursive call
        for (set_name, subdocs) in self.subdoc_cache_sets.items():

            ds_log = dict()
            ds_out = dict()

            for (doc_name, doc_obj) in self.subdocs.items():

                (d_out, d_log) = self.doc_build_files(
                    set_name,
                    doc_name,
                    doc_obj,
                    outputs,
                    data_dir,
                    build_dir,
                    build_settings)

                ds_log[doc_name] = d_log
                ds_out[doc_name] = d_out

            outputs[set_name] = ds_log
            outputs[set_name] = ds_out

        # finish up, produce output
        (post_out, post_log) = self.finish_build_files(
            outputs,
            data_dir,
            build_dir,
            build_settings)

        return (dict(**outputs, **post_out),
                dict(**log_data, **post_log))

    def start_build_files(self,
                          outputs,
                          data_dir,
                          build_dir,
                          build_settings):
        """
        Pre-question part of the build process. Generally runs the user init
        sets up questions, etc...
        """

        if type(self) == BuildableDoc:
            raise NotImplementedError("Implement this function in a subclass")

        log_data = dict()
        outputs = dict()
        return (outputs, log_data)

    def subdoc_build_files(self,
                           set_name,
                             doc_name,
                             doc_obj,
                             outputs,
                             data_dir,
                             build_dir,
                             build_settings):
        """
        """
        return doc_obj.generate_build_files(data_dir,
                                                 build_dir,
                                                 build_settings)

    def finish_build_files(self,
                           outputs,
                           data_dir,
                           build_dir,
                           build_settings):
        """
        """
        if type(self) == BuildableDoc:
            raise NotImplementedError("Implement this function in a subclass")

        log_data = dict()
        outputs = dict()
        return (outputs, log_data)

    def run_build_command(self,
                          data_dir,
                          build_dir,
                          build_settings=None):
        pass
