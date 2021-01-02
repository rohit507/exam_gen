import exam_gen.util.logging as logging
import textwrap
import types
import attr.validators as valid
import attr
from exam_gen.util.attrs_wrapper import attrs
from exam_gen.mixins.prepare_attrs.metaclass import *
from exam_gen.mixins.prepare_attrs.dataclasses import *
from copy import *
from pprint import *


log = logging.new(__name__, level="WARNING")


def create_decorator(attr_name, decor_data):
    """
    Can be used to create superclasses that define a new attribute that's
    available at class definition for anything that inherits from them.

    Instances of this class have a `decorate()` function that can be used as
    a class transformer. In general you'll want to initialize this in a
    separate function and return the `decorate()` method to create your class
    decorator.

    This will generally define a new class that subclasses whatever it's
    decorating.

    !!! Todo
        Fix description of the process below. Make clear that the `final`
        phase happens when the decorator is run, and the other phases happen
        at various points during class and instance initialization.

        Needs renaming since the `final` phase is actually the first thing
        that happens.

    ??? Info "The Full Decoration Process"

         1. **Class Decoration:** Actually generating a new class from the
            input to the decorator.

             1. `final_cls_name`: Set the name for the output class.

             1. `final_secret_attr_name`: Set the name for the attribute that's
                going to hold the value at class init time.

             1. Create the namespace for the new subclass we're generating
                with the various other phases' functions assigned to the
                correct dunders.

             1. `final_tweak_ns`: Tweak the namespace that will be used to
                initialize the new class. This is run after adding the various
                important dunders to the namespace so the tweaker can
                manipulate them directly.

             1. Create the class with appropriate settings, metaclass,
                name, etc..

             1. `final_tweak_cls`: Tweak the class after it has been created if
                needed.

             1. Store a reference to the output class for later phases,
               especially for later calls to `#!py super()`.

         1. **Subclass Initialization:** Run when we're defining a new subclass
            that inherits from our decorator.

             1. `prep`: The `__prepare_attrs__` function is run before any of
                the declarations in the subclass's definition, and can add
                variables that are available to user when the subclass is
                being defined.

                 1. `prep_new_inst`: Create a new instance of your attr to add
                    to this specific class's defintion environment..

                 1. `prep_env_update`: This is used to update the class's version
                    of an attribute (as generated by `prep_new_inst`) with
                    information from the version of your attribute generated
                    by a superclass' `__prepare_attrs__`. (if it exists)

                 1. `prep_sc_update`: If the fully initialized superclass has
                    a version of your attribute, then this is used to update
                    this subclass's instance.

                 1. Add the final version of the attr to the environment that
                    `__prepare_attrs__` produces, so that its' available at
                    definition time.

             1. Run the subclass definition. These are all the statements and
                function definitions normally found when you declare a new class.

             1. `scinit`: The `__init_subclass__` function lets you manipulate
                new subclass after it's been declared.

                 1. `scinit_mk_secret_inst`: Create the instance of the attr
                    that'll be stored in a "secret" attribute for later.

                 1. `scinit_attr_docstring`: Generate the docstring for the
                    attribute we're initializing.

                 1. `scinit_prop_cls_name`: Generate a name for the
                    `#!py property()` subclass we'll use to make the
                    `attr_docstring` visible to documentation tools like `mkdocs`.

                 1. `scinit_prop_tweak_dir`: Tweak the directory of the new
                    property we're going to create. By default this makes
                    `__getattr__` and `__setattr__` for the property map directly
                    to the corresponding functions on the secret attribute.

                 1. Create a new pseudo-property that holds the docstring,
                    and passes calls to the secret attr.

                 1. Assign that new property to our subclass' under `attr_name`.

                 1. `scinit_tweak_cls`: Potentially further tweak our subclass
                    arbitrarily one the property is created.

         1. **Create a New Object:** This is the `__new__` function that is
            run everytime we create a new object with the subclass we defined.

             1. Run `#!py super().__new__(...)` to get the instance we'll be
                tweaking.

             1. `new_mk_inst`: Create a version of our subclass' attribute for
                the new object. Generally this should be a copy of some sort
                so runtime changes to the object don't also affect the class's
                version of the attribute.

             1. Assign the newly created instance to the original attr name,
                removing the indirection from the property.

    Parameters:

       attr_name (str): The name of the attribute to be created.

       decor_data (AttrDecorData): Subclass `AttrDecorData` and define
          the various functions appropriately. What they should do is
          documented in that class.

          The various attribute names in `AttrDecorData` line up with the
          various phase names in our description of the declaration process.

    Returns:

       func: The decorator function that takes and input class and modifies
          based on the params of this function.
    """

    def decorate(cls):
        """
        The final decorator function that can be used to modify class.
        """

        new_cls_ref = [None]

        final_meta = FinalMeta(
            base_cls = cls,
            base_mod = cls.__module__,
            base_name = cls.__name__,
            base_qual_name =  "{}.{}".format(
                cls.__module__,
                cls.__name__,
            ),
            attr_name = attr_name,
            secret_attr_name = None,
            decor_data = decor_data,
        )

        secret_attr_name = decor_data.final_secret_attr_name(
            attr_name, final_meta)

        final_meta.secret_attr_name = secret_attr_name

        log.debug(
            textwrap.dedent(
                """
                Begin decorating `%s` to add new attr `%s`:

                  Input Class Dictionary:
                %s

                  Input Class Directory:
                %s

                  Final Metadata:
                %s
                """
            ),
            final_meta.base_qual_name,
            final_meta.attr_name,
            textwrap.indent(pformat(dir(cls)),"      "),
            textwrap.indent(pformat(cls.__dict__),"      "),
            textwrap.indent(pformat(final_meta),"      ")
        )

        def prep_attrs(cls, name, bases, env):

            initial_env = copy(env)

            final_attrs = attr.asdict(final_meta)

            meta = PrepMeta(
                cls = cls,
                name = name,
                bases = bases,
                env = env,
                **final_attrs,
            )

            log.debug(
                textwrap.dedent(
                    """
                    Begin preparing attr `%s` for `%s`:

                      Class Name:
                    %s

                      Bases:
                    %s

                      Incoming Environment:
                    %s

                      Preparation Metadata:
                    %s
                    """
                ),
                attr_name,
                "{}.{}".format(cls.__module__, cls.__name__),
                textwrap.indent(name,"      "),
                textwrap.indent(pformat(bases),"      "),
                textwrap.indent(pformat(initial_env),"      "),
                textwrap.indent(pformat(meta), "      "),
            )

            if hasattr(super(cls), "__prepare_attrs__"):
                env = super(cls).__prepare_attrs__(name, bases, env)

            cls_inst = decor_data.prep_attr_inst(meta)

            if meta.attr_name in env:
                cls_inst = decor_data.prep_env_update(
                    cls_inst, env[meta.attr_name], meta)

            sc_inst = getattr(cls, meta.secret_attr_name, None)
            if sc_inst != None:
                cls_inst = decor_data.prep_sc_update(
                    cls_inst, sc_inst, meta)

            env[meta.attr_name] = cls_inst

            log.debug(
                textwrap.dedent(
                    """
                    Finished preparing attr `%s` for `%s`:

                      Class Name:
                    %s

                      Bases:
                    %s

                      Incoming Environment:
                    %s

                      Final Environment:
                    %s

                      Preparation Metadata:
                    %s
                    """
                ),
                attr_name,
                "{}.{}".format(cls.__module__, cls.__name__),
                textwrap.indent(name,"      "),
                textwrap.indent(pformat(bases),"      "),
                textwrap.indent(pformat(initial_env),"      "),
                textwrap.indent(pformat(env), "      "),
                textwrap.indent(pformat(meta), "      "),
            )

            return env

        def init_subclass(cls, **kwargs):

            final_attrs = attr.asdict(final_meta)

            meta = ScInitMeta(
                cls = cls,
                kwargs = kwargs,
                new_cls = new_cls_ref[0],
                **final_attrs,
            )

            super(meta.new_cls, cls).__init_subclass__(**kwargs)

            cls_inst = getattr(cls, meta.attr_name, None)

            if cls_inst == None:
                assert False, ("Internal Error: During `__init_superclass__`"+
                               " for `{}`").format(base_cls)

            cls_inst = decor_data.scinit_mk_secret_inst(
                cls_inst,
                meta,
            )

            setattr(cls, meta.secret_attr_name, cls_inst)

            docstring = decor_data.scinit_attr_docstring(cls_inst, meta)

            def prop_getter(self):
                return getattr(
                    self,
                    meta.secret_attr_name
                )

            prop_getter.__doc__ = docstring

            def prop_setter(self, val):
                setattr(
                    self,
                    meta.secret_attr_name,
                    val
                )

            prop_name = decor_data.scinit_prop_cls_name(meta)

            prop_env = {}

            copy_attrs = [
                # '__getattribute__',
                '__getattr__',
                '__setattr__',
            ]

            for copy_attr in copy_attrs:
                val = getattr(cls_inst, copy_attr, None)
                if val != None:
                    prop_env[copy_attr] = val

            prop_env = decor_data.scinit_prop_tweak_dir(
                prop_env, cls_inst, meta)

            prop_cls = type(prop_name, (type(property()),), prop_env)

            setattr(cls, attr_name, prop_cls(prop_getter, prop_setter))

            decor_data.scinit_tweak_cls(cls, cls_inst, meta)

            log.debug(
                textwrap.dedent(
                    """
                    Finished initalizing subclass `%s` for parent `%s`:

                      New Class:
                    %s

                      New Class Instance:
                    %s

                      Additional Arguments:
                    %s

                      Environment:
                    %s

                      Subclass Init Metadata:
                    %s
                    """
                ),
                "{}.{}".format(cls.__module__, cls.__name__),
                meta.base_name,
                textwrap.indent(pformat(prop_cls), "      "),
                textwrap.indent(pformat(cls_inst), "      "),
                textwrap.indent(pformat(kwargs), "      "),
                textwrap.indent(pformat(prop_env), "      "),
                textwrap.indent(pformat(meta), "      "),
            )

        def new(cls, *vargs, **kwargs):

            final_attrs = attr.asdict(final_meta)

            meta = NewMeta(
                cls = cls,
                vargs = vargs,
                kwargs = kwargs,
                new_cls = new_cls_ref[0],
                **final_attrs,
            )

            inst = super(meta.new_cls, cls).__new__(*vargs, **kwargs)

            cls_inst = getattr(cls, secret_attr_name, None)

            attr_inst = decor_data.new_mk_inst(inst, cls_inst, meta)

            setattr(inst, attr_name, attr_inst)

            log.debug(
                textwrap.dedent(
                    """
                    Generating new instance of `%s`:

                      Variadic Arguments:
                    %s

                      Keyword Arguments:
                    %s

                      Base Class:
                    %s

                      Class Attribute Instance:
                    %s

                      Object Attribute Instance:
                    %s

                      New Object Metadata:
                    %s
                    """
                ),
                "{}.{}".format(cls.__module__, cls.__name__),
                meta.base_name,
                textwrap.indent(pformat(vargs), "      "),
                textwrap.indent(pformat(kwargs), "      "),
                textwrap.indent(pformat(cls_inst), "      "),
                textwrap.indent(pformat(attr_inst), "      "),
                textwrap.indent(pformat(meta), "      "),
            )

            return inst

        def init(self, *vargs, **kwargs):

            final_attrs = attr.asdict(final_meta)
            meta = NewMeta(
                cls = None,
                vargs = vargs,
                kwargs = kwargs,
                new_cls = new_cls_ref[0],
                **final_attrs
            )

            super(meta.new_cls, self).__init__(*vargs, **kwargs)

            log.debug("Running init for %s", type(self).__name__)

        def populate_class_namespace(namespace):

            input_namespace = copy(namespace)

            namespace["__prepare_attrs__"] = classmethod(prep_attrs)
            namespace["__init_subclass__"] = classmethod(init_subclass)
            namespace["__new__"] = classmethod(new)
            namespace["__doc__"] = cls.__doc__
            namespace["__module__"] = cls.__module__

            namespace = decor_data.final_tweak_ns(namespace, final_meta)

            log.debug(textwrap.dedent(
                """
                Populating Namespace of New Superclass:

                  Class:
                %s

                  Initial Namespace:
                %s

                  Final Namespace:
                %s

                  Final Metadata:
                %s
                """),

                textwrap.indent(pformat(cls),"      "),
                textwrap.indent(pformat(input_namespace),"      "),
                textwrap.indent(pformat(namespace),"      "),
                textwrap.indent(pformat(final_meta),"      "),
                )

            return namespace

        output_cls_name = decor_data.final_cls_name(final_meta)

        output_cls = types.new_class(
            output_cls_name,
            (final_meta.base_cls,),
            {'metaclass': PrepareAttrs},
            exec_body = populate_class_namespace,
            )

        new_cls_ref[0] = output_cls

        output_cls = decor_data.final_tweak_cls(output_cls, final_meta)

        log.debug(
            textwrap.dedent(
                """
                Finalizing Generation of New Class:

                  Input Class:
                %s

                  Output Class:
                %s

                  Output Class Directory:
                %s

                  Output Class Dictionary:
                %s

                  Final Metadata:
                %s
                """
            ),

            textwrap.indent(pformat(cls),"      "),
            textwrap.indent(pformat(output_cls),"      "),
            textwrap.indent(pformat(dir(output_cls)),"      "),
            textwrap.indent(pformat(output_cls.__dict__),"      "),
            textwrap.indent(pformat(final_meta),"      "),
        )

        return output_cls

    return decorate
