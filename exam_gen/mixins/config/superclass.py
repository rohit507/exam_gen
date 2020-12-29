import exam_gen.util.logging as logging
import textwrap
import types
import attr
from pprint import *
from copy import *
from exam_gen.util.attrs_wrapper import attrs
from exam_gen.mixins.prepare_attrs import PrepareAttrs
from exam_gen.mixins.config.value import ConfigValue
from exam_gen.mixins.config.group import ConfigGroup
from exam_gen.mixins.config.format import ConfigDocFormat, default_format

__all__ = ["config_superclass"]

log = logging.new(__name__)

config_classes = dict()

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
    __var_name = "__" + var_name

    def annotate_class(cls):

        class_name = cls.__name__
        qual_name = "{}.{}".format(cls.__module__, cls.__name__)

        args = {
            'var_name': var_name,
            'var_docstring': var_docstring,
            'doc_style': attr.asdict(doc_style),
        }
        args.update(kwargs)

        log.debug(textwrap.dedent(
            """
            Generating new Config Superclass:

              Args:
              %s

              Input Class:
              %s

              Class Directory:
              %s

            """
            ),
                  pformat(args), cls, pformat(cls.__dict__))


        def prepare_attrs(cls, name, bases, env):

            log.debug("Preparing Attrs:\n  %s",pformat({
                'cls': cls, 'name': name, 'bases':bases, 'env':env}))

            if hasattr(super(cls), "__prepare_attrs__"):
                env = super(cls).__prepare_attrs__(name, bases, env)

            class_config = ConfigGroup(
                doc = var_docstring,
                ctxt = cls,
                path = [var_name])
            if var_name in env:
                log.debug(prepare_attrs_debug_msg(
                    "Updating config for %(name)s with data from prepare_attrs of %(supr).",
                    name, cls, bases, class_config, env[var_name]))

                class_config.update(env[var_name])


            superclass_config = getattr(cls, __var_name, None)
            if superclass_config != None:
                log.debug(prepare_attrs_debug_msg(
                    "Updating config for %(name) with post-init data from %(cls).",
                    name, cls, bases, class_config, superclass_config))
                class_config.update(superclass_config)

            env[var_name] = class_config

            log.debug(textwrap.dedent(
                """
                Prepared Attrs for Subclass:

                   Class:
                   %s

                   Name:
                   %s

                   Environment:
                   %s
                """), cls, name, pformat(env))
            return env

        def empty_doc(cls):
            return textwrap.dedent(
                """
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
                """).format(
                        var_name = var_name,
                        class_name = cls.__name__,
                    )

        def init_subclass(cls, **kwargs):

            log.debug("Running init subclass for %s on class %s",
                      class_name, cls)

            super(config_classes[qual_name], cls).__init_subclass__(**kwargs)

            class_config = getattr(cls, var_name, None)
            if class_config == None:
                assert False, "Internal Error: w/ config class gen."

            class_config = class_config.clone(ctxt=cls)
            setattr(cls, __var_name, class_config)


            v_docstring = ConfigDocFormat.render_docs(
                attr.evolve(
                    doc_style,
                    doc = textwrap.dedent(var_docstring),
                    **kwargs),
                class_config,
                empty_doc = empty_doc(cls))

            def property_getter(self):
                return getattr(self,__var_name)

            property_getter.__doc__ = v_docstring

            def property_setter(self, value):
                setattr(self, __var_name, value)

            property_class = type(
                "_{}_ConfigProperty".format(class_name),
                (type(property()),),
                { '__getattr__': class_config.__getattr__,
                  '__setattr__': class_config.__setattr__,
                })

            setattr(cls, var_name, property_class(
                property_getter,
                property_setter))

        def init(self, *vargs, **kwargs):
            super(
                config_classes[qual_name], self
            ).__init__(*vargs, **kwargs)

            log.debug(textwrap.dedent(
                """
                Running `__init__` For Settings Superclass:

                  Settings Class: %s

                  Class: %s
                """)
                      , config_classes[qual_name], cls)

            class_config = getattr(self, __var_name, None)
            if class_config == None:

                class_config = ConfigGroup(
                    doc = var_docstring,
                    ctxt = self,
                    path = [var_name])

            instance_config = class_config.clone(ctxt=self)
            setattr(instance_config,'_hidden_new_value',
                    getattr(instance_config, 'new_value'))
            delattr(instance_config,'new_value')
            setattr(instance_config,'_hidden_new_group',
                    getattr(instance_config, 'new_group'))
            delattr(instance_config,'new_group')
            setattr(self, __var_name, instance_config)
            # return inst

        def populate_class_namespace(namespace):

            input_namespace = copy(namespace)

            namespace["__prepare_attrs__"] = classmethod(prepare_attrs)
            namespace["__init_subclass__"] = classmethod(init_subclass)
            namespace["__init__"] = init
            namespace["__doc__"] = cls.__doc__
            namespace["__module__"] = cls.__module__
            # namespace[var_name] = attr.ib()

            log.debug(textwrap.dedent(
                """
                Populating Namespace of New Superclass:

                  Class:
                  %s

                  Initial Namespace:
                  %s

                  Final Namespace:
                  %s
                """)
                      , cls, pformat(input_namespace), pformat(namespace))
            return namespace

        # # Make sure the parent class is attrs annotated
        # attrs_cls = cls

        # if not attr.has(cls):
        #     attrs_cls = attr.make_class(
        #         class_name,
        #         {var_name: attr.ib()},
        #         (cls,),
        #     )

        output_class = types.new_class(
            "wrapped_{}".format(class_name),
            (),
            {'metaclass':PrepareAttrs},
            exec_body = populate_class_namespace,
        )

        # Shove a property into the variable so we can stick in an attribute
        # docstring
        def get_stub(self): pass

        get_stub.__doc__ = empty_doc(cls)
        setattr(output_class,var_name, property(get_stub))

        log.debug(textwrap.dedent(
            """
            Finished Generating Config Superclass:

              Output Class:
              %s

              Class Directory:
              %s

            """
        ),

        output_class, pformat(output_class.__dict__))
        config_classes[qual_name] = output_class
        return config_classes[qual_name]

    return annotate_class

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
