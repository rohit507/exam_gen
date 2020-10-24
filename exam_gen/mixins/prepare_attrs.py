from pprint import *
class PrepareAttrs(type):
    """
    Classes using this metaclass can define a `__prepare_attrs__` class method to
    manipulate the attributes available during the definition of any *child*
    classes.
    """

    @classmethod
    def __prepare_attrs__(cls, name, attrs):
        """
        Redefine this function in classes using this metaclass to manipulate the
        attributes available in subclass definitions.

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
        mro = type(name,bases,{}).__mro__[1:]

        for cls in reversed(mro):

            prep_hook = getattr(cls,'__prepare_attrs__', None)

            if prep_hook is not None:
                attrs = prep_hook(name,bases,attrs)

        return attrs
