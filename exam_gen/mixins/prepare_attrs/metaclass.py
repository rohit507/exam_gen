import exam_gen.util.logging as logging
import textwrap
import types
import attr.validators as valid
import attr
from exam_gen.util.attrs_wrapper import attrs
from copy import *
from pprint import *


log = logging.new(__name__, level="WARNING")

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
