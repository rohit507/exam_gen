from .object import VersionedObj
from .option import VersionedOption
from .decorator import add_versioned_option


__template_var_opts__ = {
    'text':{},
    'file':{},
    'vars':{},
}

__choice_var_opts__ = __template_var_opts__ | {
    'shuffle':{'root_only':True},
    'num':{'root_only':True}
}

__exam_formats__ = ['exam', 'solution']

def exam_format_key_func(self, key):
    if key in __exam_formats__:
        return key
    else:
        raise RuntimeError("{} is not a valid exam format.".format(key))

def multiple_choice_key_func(self, key):
    if not isinstance(key, int):
        raise RuntimeError("Only integers can be used to reference multiple "
                           "choice answers.")
    elif self.num <= key:
        raise RuntimeError(("Key number too high, try setting "
                            "`{}.num` higher").format(self.root.var_name))
    else:
        return key

__template_var_format__ = [
    {'key_func':exam_format_key_func}]

__choice_var_format__ = [{'key_func':multiple_choice_key_func}
                        ] + __template_var_format__

template_var = functools.partial(
    add_versioned_option,
    format_spec = __template_var_format__,
    option_spec = __template_var_opts__
    )

choice_var = functools.partial(
    add_versioned_option,
    format_spec = __choice_var_format__,
    option_spec = __choice_var_opts__
    )
