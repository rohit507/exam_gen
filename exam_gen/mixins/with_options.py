
import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

class WithOptions():
    """
    Mixin class that adds a `with_options` class method, which lets you
    specify some subset of the keyword arguments in an initializer and get a
    new initializer that has those arguments baked in.

    Instead of:
    ```py
    kw_args = {'arg1': "value", 'arg2': "other value"}

    target_class = SomeClass

    new_object = target_class(arg3="something else", **kw_args)
    ```

    You can have:

    ```py
    target_class = SomeClass.with_options(arg1="value", arg2="other value")

    new_object = target_class(arg3="something else")
    ```

    This is useful when you use class objects as values for various reasons.
    Now, both `SomeClass` and `SomeClass.with_options(...)` are callables that
    can be used interchangeably to create instances with some property.

    !!! Todo API Improvement
        Make this return a new stub class rather than a function. That way
        `with_options` can be called recursively and the other functionality
        of the class can be preserved.
    """

    @classmethod
    def with_options(cls, **kwargs):
        """
        Create a new constructor function w/ some kw-arguments curried in.
        """
        def init_bld(*vargs, **kwargs2):
            return cls(*vargs, **dict(kwargs, **kwargs2))

        return init_bld
