import textwrap
import types
from copy import *
from pprint import *

import attr

import exam_gen.util.logging as logging
from exam_gen.mixins.config.format import ConfigDocFormat, default_format
from exam_gen.mixins.config.group import ConfigGroup
from exam_gen.mixins.config.value import ConfigValue
from exam_gen.mixins.prepare_attrs.dataclasses import AttrDecorData
from exam_gen.mixins.prepare_attrs.decorator import create_decorator

__all__ = ["config_superclass"]

log = logging.new(__name__, level="WARNING")

config_classes = dict()

def empty_doc(var_name, cls_name, cls_doc=None):
    cls_doc = "" if (cls_doc == None) or (cls_doc == "") else cls_doc + "\n"
    return textwrap.dedent(
        """
        {cls_doc}
        ## {var_name} Setup ##

        Empty configuration group variable that you can extend in
        subclasses as needed. These extensions will be automatically
        documented where possible.

        ??? Example "Creating new `#!py {var_name}` fields."
            Add new values with `#!py {var_name}.new_value()`:
            ```python
            class SomeSubclass({class_name}):

                {var_name}.new_value(
                    name = "example_var",
                    default = ["some","example","value"], # defaults to `None`
                    doc = \"""
                    Docstring for `example_var`
                    \""",
                )

                {var_name}.example_var = ["new","example","value"]
            ```

        ??? Example "Creating new `#!py {var_name}` subgroups."

            Add new config subgroups with `#!py {var_name}.new_group()`:
            ```python
            class SomeSubclass({class_name}):

                {var_name}.new_group(
                    name = "example_group",
                    doc = \"""
                    Docstring for `example_group`
                    \""",
                )

                {var_name}.example_group.new_value(
                "example_var", 1234, "example_docstring")

                {var_name}.example_group.example_var += 12
            ```

        ??? Warning
            Both `#!py new_value()` and `#! new_group()` are
            unavailable at runtime, and can only be used in class
            definitions like the above.

            This keeps the documentation in sync with the available
            options and generally prevents bad practices.

            <sub><sub>If you really must do this, the functions are moved to
            `#!py _hidden_new_value()` and `#!py _hidden_new_group()`
            during instance initialization.</sub></sub>
        """
    ).format(
        cls_doc = cls_doc,
        var_name = var_name,
        class_name = cls_name,
    )

def config_superclass(
        var_name,
        var_docstring = "",
        doc_style = None,
        **kwargs
        ):
    """
    A decorator to create new superclasses with a special configuration
    variable that various subclasses can add to, and which is automatically
    documented properly.

    Look in `exam_gen.mixins.config.managers` for examples of how to use this
    decorator.

    !!! Danger ""
        The *only* property of the decorated class which is preserved is the
        docstring. All other functions and properties are **lost**. The
        post-decoration class isn't even a subclass of the input and can't
        access any of its features.

        This is really only meant to produce stubs that are at the very tops
        of an inheritance hierarchy. **It will not work as a way to add a
        configuration group to a class with existing functionality.**

    ??? Todo "Feature Todo List"

          - `attrs` support for generated class
          - Fix bug where attributes inherited from `ConfigDocFormat` aren't
            properly passed through.
          - Actually inherit from the decorates class in some useful way.
          - Make these classes work with whatever YAML stuff you end up
            using for the rest of the system.
          - Add two methods for the generated to read in a set of config vals
            as a nested dictionary when `__init__` is called.
             - **Method 1:** Naively override all settings based on the
                dict input.
             - **Method 2:** Only override settings that were defined outside
                before the current class definition or this specific instance.


    Parameters:

       var_name (str): The name of the class's configuration variable.

       var_docstring (str): The docstring for the configuration variable. Will
          be visible in the collected docs for every subclass.

       doc_style (ConfigDocFormat): The documentation style object to use when
          generating the variable documentation for this class. (Defaults
          to `exam_gen.mixins.config.format.default_format` when the actual
          input is `#!py None`)

       **kwargs: Extra parameters that are passed to documentation style. Taken
          from `#!py exam_gen.mixins.config.format.ConfigDocFormat` so look
          there for specific flags you can set.

          **Notable Inherited Params:**

             - `val_table_name` (str): As in `#!py ConfigDocFormat`
             - `group_table_name` (str): As in `#!py ConfigDocFormat`
             - `combined_table_name` (str): As in `#!py ConfigDocFormat`
             - `recurse_entries` (bool): As in `#!py ConfigDocFormat`
             - `combine_tables` (bool): As in `#!py ConfigDocFormat`
    """

    doc_style = doc_style if doc_style != None else default_format

    class ConfigManagerDecor(AttrDecorData):

        @staticmethod
        def prep_attr_inst(prep_meta):
            return ConfigGroup(
                doc = copy(var_docstring),
                ctxt = prep_meta.cls,
                path = [prep_meta.attr_name],
                )

        @staticmethod
        def prep_env_update(cls_val, env_val, prep_meta):
            cls_val.update(env_val)
            return cls_val

        @staticmethod
        def prep_sc_update(cls_val, sc_val, prep_meta):
            cls_val.update(sc_val)
            return cls_val

        @staticmethod
        def scinit_mk_secret_inst(cls_val, scinit_meta):
            return cls_val.clone(ctxt=scinit_meta.cls)

        @staticmethod
        def scinit_attr_docstring(cls_val, scinit_meta):

            cls_attr = getattr(
                scinit_meta.cls,
                scinit_meta.attr_name,
                None)

            cls_attr_doc = None

            if cls_attr != None:
                cls_attr_doc = getattr(cls_attr, "__doc__", None)

            return ConfigDocFormat.render_docs(
                attr.evolve(
                    doc_style,
                    doc= textwrap.dedent(var_docstring),
                    **kwargs),
                cls_val,
                empty_doc = empty_doc(
                    scinit_meta.attr_name,
                    scinit_meta.cls.__name__,
                    cls_attr_doc,
                ),
            )

        @staticmethod
        def new_mk_inst(super_obj, cls_inst, new_meta):
            new_inst = cls_inst.clone(ctxt=super_obj)

            log.debug(
                textwrap.dedent(
                    """
                    Creating new `%s` attr for instance of `%s`:

                      New Instance Directory:
                    %s

                      New Instance Dictionary:
                    %s

                      New Instance Contents:
                    %s
                    """
                ),
                new_meta.attr_name,
                new_meta.cls,
                textwrap.indent(pformat(dir(new_inst)), "      "),
                textwrap.indent(pformat(new_inst.__dict__), "      "),
                textwrap.indent(pformat(new_inst), "      "),
            )

            setattr(new_inst,'_hidden_new_value',
                    getattr(new_inst, 'new_value'))
            # delattr(new_inst,'new_value')

            setattr(new_inst,'_hidden_new_group',
                    getattr(new_inst, 'new_group'))
            # delattr(new_inst,'new_group')


            return new_inst

    return create_decorator(var_name, ConfigManagerDecor)

def prepare_attrs_debug_msg(msg, name, cls, bases, us, them):

    hide_docs = True
    """
    Generate an overly verbose debug message during class initialization.
    Mainly to help debug inheritance of variables in the environment of a
    class that's inheriting from a config superclass.
    """

    properties = dict(
        name = name,
        cls = cls.__qualname__,
        bases = bases,
        our_ctxt = us.ctxt,
        our_path_string = us.path_string(),
        our_values = pformat(
            us.value_dict,
            indent = 8),
        their_path_string = them.path_string(),
        their_ctxt = them.ctxt,
        their_value = pformat(
            them.value_dict,
            indent=8),
        supr=super(cls)
        )

    template = """
        During PrepareAttrs of %(name)s with %(cls):
        %(msg)s

          %(name)s Data:
            Bases: %(bases)s
            Path: %(our_path_string)s
            Context: %(our_ctxt)s
            Data: %(our_values)s

          %(cls)s Data:
            Path: %(their_path_string)s
            Context: %(their_ctxt)s
            Data: %(their_values)s
        """

    return textwrap.dedent(template).format(
        msg=msg.format(properties),
        **properties,
    )
