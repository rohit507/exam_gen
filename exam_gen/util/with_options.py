import functools
import inspect
import types

from pprint import *

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

        class AppOpts(cls):
            def __init__(self, *vargs, **kwargs2):
                super().__init__(*vargs, **(kwargs2 | kwargs))

        # new_cls = type(cls.__name__,
        #                (cls,),
        #                {'__init__': functools.partial(
        #                    new_init, cls=cls, **kwargs)})

        return AppOpts
    else:
        return functools.partial(cls, **kwargs)

class WithOptions():

    @classmethod
    def with_options(cls, **kwargs):
        return with_options(cls, **kwargs)
