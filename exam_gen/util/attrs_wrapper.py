from attr import attrs, attrib

def wrap(attrs_init=None, **kwargs):
    '''
    Decorator that can wrap attrs to rename the `__init__` function to
    `__attrs_init__`
    '''
    def wrap(cls):
        ''' The internal wrapper method for the decorator. '''
        if attrs_init:
            __old_init__ = getattr(cls, '__init__')
            new_cls = attrs(init=True, **kwargs)(cls)
            __init__ = getattr(new_cls, '__init__')

            setattr(new_cls, '__attrs_init__', __init__)
            setattr(new_cls, '__init__', __old_init__)
            return new_cls
        else:
            new_cls = attrs(**kwargs)(cls)
            return new_cls

    return wrap
