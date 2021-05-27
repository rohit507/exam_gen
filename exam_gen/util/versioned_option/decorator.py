import attr
import functools

from copy import *

from exam_gen.util.prepare_attrs import AttrDecorData, create_decorator

from .option import VersionedOptions

import exam_gen.util.logging as logging


log = logging.new(__name__, level="DEBUG")

__all__ = ["add_versioned_option"]

def add_versioned_option(
        name,
        template_class=None,
        option_spec=None,
        format_spec=None,
        doc=None,
        prep_args=dict()):

    if doc == None and hasattr(template_class,"__doc__"):
        doc = template_class.__doc__

    if template_class == None:
        template_class = VersionedOptions

    class VerOptDecor(AttrDecorData):

        @staticmethod
        def prep_attr_inst(prep_meta):

            params = copy(prep_args)

            params['var_name'] = name

            if option_spec: params['option_spec'] = option_spec
            if format_spec: params['format_spec'] = format_spec

            return template_class(**params)

        @staticmethod
        def prep_sc_update(cls_val, sc_val, prep_meta):

            opt_spec = sc_val._option_spec | cls_val._option_spec
            cls_val._option_spec = opt_spec

            cls_val.apply_version_tree(sc_val.version_tree())

            return cls_val

        @staticmethod
        def scinit_mk_secret_inst(cls_val, scinit_meta):
            return deepcopy(cls_val)

        @staticmethod
        def scinit_attr_docstring(cls_val, scinit_meta):
            return doc

        @staticmethod
        def new_mk_inst(super_obj, cls_inst, new_meta):
            return deepcopy(cls_inst)

    return create_decorator(name, VerOptDecor)
