import exam_gen.util.logging as logging
import textwrap
import types
import attr.validators as valid
import attr
from exam_gen.util.attrs_wrapper import attrs
from copy import *
from pprint import *

log = logging.new(__name__, level="WARNING")

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
