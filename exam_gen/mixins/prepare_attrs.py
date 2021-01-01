import exam_gen.util.logging as logging
import textwrap
import types
import attr.validators as valid
import attr
from exam_gen.util.attrs_wrapper import attrs
from copy import *
from pprint import *


log = logging.new(__name__, level="DEBUG")

class PrepareAttrs(type):
    """
    Classes using this metaclass can define a `__prepare_attrs__` class method to
    manipulate the attributes available during the definition of any *child*
    classes.
    """

    @classmethod
    def __prepare_attrs__(cls, name,bases, attrs):
        """
        Define this function in classes using this metaclass to manipulate the
        attributes available in subclass definitions.

        ???+ Important
            Any function defining `__prepare_attrs__` should make sure it's
            idempotent in the `attrs` dictionary. Equivalently, the
            following should work for all possible `name`,`bases`,and `attrs`:

            ``` python
              prep_attrs = lambda a : YourClass.__prepare_attrs__(name,bases,a)

              assert(prep_attrs(attrs) == prep_attrs(prep_attrs(attrs)))
            ```

        Args:
           name (str): The name of the class being created
           bases (list): list of classes this class is derived from
           attrs (dict): The attributes defined by previous classes in the mro

        Returns:
           dict: The edited `attrs` dictionary that will be available to child
           classes as they're defined. The simplest possible version will just
           return the argument directly.
        """
        return attrs

    @classmethod
    def __prepare__(metaclass, name, bases):

        attrs = super().__prepare__(name,bases)
        mro = PrepareAttrs.get_future_mro(name, bases)

        for cls in reversed(mro):

            prep_hook = getattr(cls,'__prepare_attrs__', None)
            if prep_hook is not None:
                attrs = prep_hook(name,bases,attrs)

        return attrs

    # Code below from : https://stackoverflow.com/a/52427184
    # Meant to replicate the mro calculation process in python without
    # The sort of side effects that just using type(name,bases,{}).__mro__
    # would produce.

    stub_cache = {object: object}

    @classmethod
    def get_stub_class(self, cls):
        """
        Creates/retrieves a class object that is a side effect free version
        of another class.

        Args:
          cls (class): An external class

        Returns:
          class: An 'empty' stub with an identical mro to the parent class.
              This is cached and so will return the same stub class each time
              it's called on another class.
        """
        if cls is object:
            return object
        stub_bases = []
        for base in cls.__bases__:
            stub_bases.append(self.get_stub_class(base))
        if cls not in self.stub_cache:
            self.stub_cache[cls] = type(cls.__name__, tuple(stub_bases), {})
        return self.stub_cache[cls]

    @classmethod
    def get_future_mro(self, name, bases):
        """
        Method to get the mro of a potential new class without triggering a
        number of class initialization and metaclass side-effects. Results are
        cached internal to the `PrepareAttrs` class object.

        Args:
           name (str): The name of the class you're getting an mro for
           bases (tuple): A tuple of all the classes that the new one
              will directly inherit from.

        Returns:
           list: The mro that a hypothetical class with the given
              bases would have.
        """
        stub_bases = tuple(self.get_stub_class(base) for base in bases)
        stub_cls = type(name, stub_bases, {})
        reversed_cache = {value:key for key, value in self.stub_cache.items()}
        return [reversed_cache[mro_base] for mro_base in  stub_cls.__mro__[1:]]

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

    ??? Info "The Full Decoration Process"

         1. `prep`: defining and creating the `__prepare_attrs__` function,
            which is run before a class's definition is evaluated and controls
            what's in the environment during class definition.

            1. `new_inst`: Create a new instance of your attr for this specific
               class.

            1. `env_update`: If your attribute already exists in the environment
               generated by a superclass's `__prepare_attrs__`, then update your
               the new instance with that information.

            1. `sc_update`: If the fully initialized superclass has your
               attribute, then update this class's instance with that info.

            1. Add the final version of the attr to the environment that
               `__prepare_attrs__` produces.

         1. `scinit`: defining and creating the `__init_subclass__` function,
            which is run just after the class is defined and helps create the
            final version of the class.

            1. `mk_secret_inst`: Create the instance of the class that'll be
               stored in a "secret" attribute for restoration when we're
               initializing a new instance.

            1. `attr_docstring`: Generate the docstring for the attribute we're
               initializing.

            1. `prop_cls_name`: Generate a name for the `#!py property()`
               subclass we'll use to make the `attr_docstring` visible to
               documentation tools.

            1. `prop_tweak_dir`: Tweak the directory of the new property we're
               going to create. Useful for making sure that `__setattr__`,
               `__getattr__`, and other dunders are accessible.

            1. Create a new pseudo-property that holds the docstring and attach
               it to our new attribute.

            1. `tweak_cls`: Potentially further tweak our subclass.

         1. `new`: defining and creating the `__new__` function.

            1. `mk_inst`: Create the instance that will populate our new
               attribute at runtime, usually by creating a clone or copy of
               what's in the "secret" class attribute.

            1. Assign the newly created instance to the original attr name.

         1. `init`: defining and creating the `__init__` function.

            1. `tweak_fun`: Manipulate the default `__init__` function somehow,
               this allows for arbitrary wrapping or complete replacement.

         1. `final`: tweaking and finalizing the final output class.

            1. `tweak_ns`: Tweak the namespace that will be used to initialize
               the newly created class. This is run after adding the various
               important dunders to the namespace so can manipulate them
               directly.

            1. `tweak_cls`: Tweak the class after it has been created if
               needed.

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


class AttrDecorData():
    """
    This class mostly exists to provide nicely formatted docs for
    `create_decorator` by wrapping the main input attributes in a class.

    Specialize them for a particular task by subclassing this, overriding the
    relevant functions and passing it as an argument to `create_decorator`.
    """

    @staticmethod
    def prep_attr_inst(prep_meta):
        """
        Set the initial value of your attribute as it will be before the class
        definitions are run.

        !!! Danger ""
            This function **must** be overridden by any subclasses.

        Parameters:

           prep_meta (PrepMeta): See `PrepMeta` class for info.

        Returns:

           attr_val : The initial value of the new variable.

        """
        raise NotImplementedError("Subclasses must override this function")

    @staticmethod
    def prep_env_update(cls_val, env_val, prep_meta):
        """
        This describes how to update your attribute if a superclass has
        already set a value for your attribute during its `__prepare_attrs__`
        phase.

        !!! Info ""
            This defaults to just returning the previous value of the class's
            attribute and ignoring the value from the superclass.

        Parameters:

           cls_val (attr_val): The value of the attribute currently assigned
              to the new subclass.

           env_val (attr_val): The value of the attribute that was generated
              by a superclass's `__prepare_attrs__`.

           prep_meta (PrepMeta): See `PrepMeta` class for info.

        Returns:

           attr_val: The updated value of your new attr.

        """
        return cls_val

    @staticmethod
    def prep_sc_update(cls_val, sc_val, prep_meta):
        """
        This describes how to update your attribute if a superclass has
        a value for your attribute **after it has been initialized**.

        !!! Warning ""
            This defaults to using **the value from the superclass** as,
            generally, you'll want to preserve any updates to a variable
            by a superclass.

            **Note:** This default will end up keeping the value from most
            recent superclass in mro order.

        Parameters:

           cls_val (attr_val): The value of the attribute currently assigned
              to the new subclass.

           env_val (attr_val): The value of the attribute that was generated
              by a superclass after it was initialized.

           prep_meta (PrepMeta): See `PrepMeta` class for info.

        Returns:

           attr_val: The updated value of your new attr.
        """
        return sc_val

    @staticmethod
    def scinit_mk_secret_inst(cls_val, scinit_meta):
        """
        Create a version of the attr's value that's unique to the class,
        tweaking it if necessary.

        !!! Info ""
            By default this just returns `cls_val` and doesn't make any
            additional changes. That said, you probably want to make a copy of
            the value.

        Parameters:

           cls_val (attr_val): The value of the attr after class definition.

           scinit_meta (ScInitMeta): See `ScInitMeta` class for info.

        Returns:

           attr_val: Write details of expected return values

        """
        return cls_val

    @staticmethod
    def scinit_attr_docstring(cls_val, scinit_meta):
        """
        Generate the docstring for your new attribute.

        !!! Info ""
            This defaults to `None`, which means no docstring will be found or
            generated.

        Parameters:

           cls_val (attr_val): The value of the attribute currently assigned
              to the new subclass.

           scinit_meta (ScInitMeta): See `ScInitMeta` class for info.

        Returns:

           str: The new docstring for your type.
        """
        return None

    @staticmethod
    def scinit_prop_cls_name(scinit_meta):
        """
        Choose the name of the newly generated property stub class.

        !!! Info ""
            Defaults to `#!py "_{scinit_meta.attr_name}_Property"`.

        Parameters:

           scinit_meta (ScInitMeta): See `ScInitMeta` class for info.

        Returns:

           str: The name of the property class
        """
        return "_{}_Property".format(scinit_meta.attr_name)


    @staticmethod
    def scinit_prop_tweak_dir(namespace,
                              cls_val,
                              scinit_meta):
        """
        Modify the namespace for the property we're creating to add sunders

        !!! Info ""
            Defaults to returning the `namespace` unchanged.

        Parameters:

           namespace (dict): A dictionary of properties to be added to the
              the new property subclass, includes `__getattr__` and
              `__setattr__` if they exist.

           cls_val (attr_val): The value of the attribute currently assigned
              to the new subclass.

           scinit_meta (ScInitMeta): See `ScInitMeta` class for info.

        Returns:

           dict: The new namespace for the stub property.
        """
        return namespace

    @staticmethod
    def scinit_tweak_cls(cls, cls_val, scinit_meta):
        """
        Arbitrary tweaks to the class if needed. Note that this should
        modify `cls` directly, as it returns nothing.

        !!! Note ""
            Defaults to just doing nothing.

        Parameters:

           cls (cls): The subclass that's being initialized.

           cls_val (attr_val): The value of the attribute currently assigned
              to the new subclass.

           scinit_meta (ScInitMeta): See `ScInitMeta` class for info.
        """
        pass

    @staticmethod
    def new_mk_inst(super_obj, cls_inst, new_meta):
        """
        Create a new attr object for a specific instance of the subclass.

        !!! Note ""
            Defaults to just returning `cls_inst` without any modification.

        Parameters:

           super_obj (class): New instance of the class that was created
              by calling `#!py super().__new__(...)`.

           cls_inst (attr): The class's instance of the attribute.

           new_meta (NewMeta): See `NewMeta` class for info.

        Returns:

           attr: the instance attribute that is unique to a single object.
        """
        return cls_inst

    @staticmethod
    def final_secret_attr_name(attr_name, final_meta):
        """
        Pick a name for the secret attribute we use to store the attr data
        in the newly generated class.

        !!! Note ""
            Defaults to `#!py "__{}".format(attr_name)`

        Parameters:

           attr_name (str): The name of attribute we're creating.

           final_meta (FinalMeta): See the `FinalMeta` class for details. Note
              that `final_meta.secret_attr_name` will be set to `None` when
              this function is run.

        Returns:

           str: The name of the secret attribute we're going to use.
        """

        return "__{}".format(attr_name)

    @staticmethod
    def final_cls_name(final_meta):
        """
        Generate a new name for the final output class.

        !!! Note ""
            See source below for default implementation.

        Parameters:

           final_meta (FinalMeta): See `FinalMeta` class for info.

        Returns:

           str: the name of the new object.
        """
        return "_{}_{}".format(
            type(final_meta.decor_data).__name__,
            final_meta.base_name,
        )

    @staticmethod
    def final_tweak_ns(namespace, final_meta):
        """
        This lets you add things to the dictionary of the new class
        arbitrarily, and gives you a chance to bake various things in if you
        want.

        !!! Info ""
            Defaults to just returning `namespace` unmodified.

        Parameters:

           namespace (attr): The namespace of the function

           final_meta (FinalMeta): See `FinalMeta` class for info.

        Returns:

           dict: The modified namespace to use when generating the wrapped
              decorator class.
        """
        return namespace

    @staticmethod
    def final_tweak_cls(cls, final_meta):
        """
        Tweak the final class in whatever way is appropriate for your
        task.

        !!! Info ""
            Defaults to just returning the input class unmodified.

        Parameters:

           cls (cls): The namespace of the function

           final_meta (FinalMeta): See `FinalMeta` class for info.

        Returns:

           dict: The modified namespace to use when generating the wrapped
              decorator class.

        """
        return cls

@attr.s
class FinalMeta():
    """
    Metadata class that's passed around during deccorator creation.

    !!! Todo
        Fix the name, since the `final` phase is always the first thing that
        happens. The current name is just because the code for it comes later
        in the source file than the other phases.

    Attributes:

       base_cls (class): The class the decorator is modifying.
       base_mod (str): The module of the base class.
       base_name (str): The name of the base class.
       base_qual_name (str): The fully qualified name of the class.
       attr_name (str): The name of the new attribute being created.
       secret_attr_name (str): The name of the secret attribute being created.
       decor_data (AttrDecorData): The full decorator data class (or instance)
          used to define what the decorator function as a whole does.
    """
    base_cls = attr.ib()
    base_mod = attr.ib()
    base_name = attr.ib()
    base_qual_name = attr.ib()
    attr_name = attr.ib()
    secret_attr_name = attr.ib()
    decor_data = attr.ib()


@attr.s
class NewMeta(FinalMeta):
    """
    Metadata available when we are initializing an instance of the class
    created by the decorator.

    Attributes:

       cls (class): The current class being initialized, can be different from
          the base class if it's a subclass.

       vargs (list): The positional args passed to `__new__`.

       kwargs (dict): The keyword args passed to `__new__`.

       new_cls (class): The class that was generated by the decorator, barring
          shenanigans in the implementation of `decor_data` both
          `#!py instanceof(cls, new_cls)` and
          `#!py instanceof(new_cls, base_cls)` should be true.


    This also inherits from `FinalMeta` and has all its attributes.
    """
    cls = attr.ib()
    vargs = attr.ib()
    kwargs = attr.ib()
    new_cls = attr.ib()


@attr.s
class ScInitMeta(FinalMeta):
    """
    Metadata available when we are initializing a new subclass of our
    `base_cls`.

    Attributes:

       cls (class): The current class being initialized, can be different from
          the base class if it's a subclass.

       kwargs (dict): The keyword args passed to `__init_subclass__`.

       new_cls (class): The class that was generated by the decorator, barring
          shenanigans in the implementation of `decor_data` both
          `#!py instanceof(cls, new_cls)` and
          `#!py instanceof(new_cls, base_cls)` should be true.


    This also inherits from `FinalMeta` and has all its attributes.
    """
    cls = attr.ib()
    kwargs = attr.ib()
    new_cls = attr.ib()

@attr.s
class PrepMeta(FinalMeta):
    """
    Metadata available when we are preparing the environment for running a
    class definition. (i.e. running `__prepare_attrs__`)

    Attributes:

       cls (class): The superclass whose `__prepare_attrs__` hook is being
          called.

       name (str): The name of the new class that we're about to define.

       bases (tuple): The various super classes the new class we're making
          will have.

       env (dict): The environment that will be make available to statements
          when the new class is being defined.

    This also inherits from `FinalMeta` and has all its attributes.
    """
    cls = attr.ib()
    name = attr.ib()
    bases = attr.ib()
    env = attr.ib()
