import functools
import inspect
import types

from pprint import *

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

__all__ = ["WithOptions"]

# def with_options(cls, **kwargs):
#     """
#     Create a new constructor function w/ some kw-arguments curried in.
#     Adds a with_options property to the function that will allow for
#     recursion and multiple things doing the same op.
#     """

#     if inspect.isclass(cls):

#         cls_ref = list([None])

#         def init(self, *vargs, **kwargs2):
#             super(cls_ref[0], self).__init__(*vargs, **(kwargs2 | kwargs))

#         cls_ref[0] = type(
#             "_with_opts_{}".format(cls.__name__),
#             (cls,),
#             cls.__dict__ | {'__init__': init})

#         return cls_ref[0]
#     else:
#         return functools.partial(cls, **kwargs)

class WithOptions():

    @classmethod
    def with_options(cls, **kwargs):
        return functools.partial(cls, **kwargs)
