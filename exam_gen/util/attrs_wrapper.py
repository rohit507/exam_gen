import attr
from copy import *

default_attrs_params = {
    'order': False,
    'collect_by_mro': True,
    'attrs_init': True,
    }

def attrs(**kwargs):
    params = deepcopy(default_attrs_params)
    params.update(kwargs)
    return wrap(**params)

def wrap(attrs_init=None, **kwargs):
    '''
    Decorator that can wrap attrs to rename the `__init__` function to
    `__attrs_init__`. There's currently a pull request in the attrs github
    that does the same thing, though hopefully it'll be
    '''
    def wrap(cls):
        ''' The internal wrapper method for the decorator. '''
        if attrs_init:
            __old_init__ = getattr(cls, '__init__')
            new_cls = attr.s(init=True, **kwargs)(cls)
            __init__ = getattr(new_cls, '__init__')

            setattr(new_cls, '__attrs_init__', __init__)
            setattr(new_cls, '__init__', __old_init__)
            return new_cls
        else:
            new_cls = attr.s(**kwargs)(cls)
            return new_cls

    return wrap
