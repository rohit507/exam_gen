import functools
import inspect
import types

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

__all__ = ["with_options", "WithOptions"]

def with_options(cls, **kwargs):
    """
    Create a new constructor function w/ some kw-arguments curried in.
    Adds a with_options property to the function that will allow for
    recursion and multiple things doing the same op.
    """

    if inspect.isclass(cls):
        new_cls = types.new_class(cls.__name__, (cls))

        def new_init(self,*vargs,cls,**kwargs):
            super(cls, self).__init__(*vargs, **kwargs)

        new_cls.__init__ = functools.partial(
            new_init,
            cls=cls,
            **kwargs
        )

        return new_cls
    else:
        return functools.partial(cls, **kwargs)

class WithOptions():

    @classmethod
    def with_options(cls, **kwargs):
        return with_options(cls, **kwargs)
