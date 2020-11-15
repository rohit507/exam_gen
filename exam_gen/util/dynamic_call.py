from pprint import *
from inspect import *


def dynamic_call(
        func,
        arg_dict,
        order = [],
        required = [],

):
    """
    This function basically attempts to call the input with as much of
    the available argument options as it'll take. In general the process
    is as follows:

      1. Go through all the standard parameters of the function and match
         them up with `arg_dict` entries based on `order`, using the function
         defaults if needed.

    ??? Example

        For example, if we have:

        ```python
        def      f ( a ,    b    ,      c=34,     d=72 ,  e=14  ): pass
        order    = ['a',   'buzz',     'bar',     None ]
        arg_dict = {'a': 1,'buzz': 44, 'bar': 12,        'e': 93}
        ```

        Then `dynamic_call(f,arg_dict,order)` would match up each argument in
        order:

          - `a` is in the dict, so we can use that,
          - `b` matches with `'buzz'` so we use the value for `'buzz'`.
          - `c` is matches with `'bar'` so we ignore the default and use that
            value.
          - `d` matches with `None`, but has a default so that is used.
          - `e` is after the end of the list (equivalent to order containing
            `None` at that position) but there's a matching key in our dict
            so we use the value from there.

        Leaving us with a final call of `f(1,44,12,72,93)`.

      2. Match up all the keyword parameters, using the defaults if the values
         aren't found in `arg_dict`.

      3. If there are more elements in `order` than there are parameters to the
         function **and** there's a variadic positional argument (like `*args`),
         then return those additional parameters.

      4. If there are any unused arguments in `arg_dict` and a variadic keyword
         argument (like `**kwargs`) then add those keyword arguments to the dict.

      5. If there are any required arguments that remain unused, then throw an
         error.

    !!! Danger
        I am not at all sure if this is a good idea. Like with
        `prepare_attrs` it makes code using it less 'pythonic', but potentially
        neater and easier for non-python programmers to work with.

        Unlike `prepare_attrs` it *might* be prone to throwing errors to the
        end user that they're unable to handle. It's dependent on the user of
        this library to make sure that errors get translated into something
        more user friendly.

    Args:
        func (function): The function to call.
        arg_dict (dict): The full dict of possible keyword arguments that the
            function has available
        order (list): The names for all the basic ordered arguments, `None` if
            they're to be matched up by keyword or default.
        required (list): The names of all the arguments that must be passed
            to the function

    Returns:
        any: Whatever `func` would return, or an error if arguments don't
            match up.
    """
    sig = signature(func)
    num_args = len(sig.parameters)
    err_data = {
        'arg_dict': arg_dict,
        'order': order,
        'required': required,
        'func': func
    }

    args = []
    kwargs = {}
    used_args = []

    # Pad Order to match the number of args
    if len(order) < num_args:
       order = (order + num_args * [None])[:num_args]

    # Use zip to make a big list of all the order elements parameters
    # and other info we need to evaluate each parameter.
    terms = zip(zip(range(0,num_args),order),sig.parameters.items())
    for ((index,order_item),(param_name, param)) in terms:
        if param.kind == Parameter.POSITIONAL_OR_KEYWORD:
            if param_name in arg_dict:
                used_args.append(param_name)
                args.append(arg_dict[param_name])
            elif (order_item != None) and (order_item in arg_dict):
                used_args.append(order_item)
                args.append(arg_dict[order_item])
            elif param.default != Parameter.empty:
                used_args.append(param_name)
                args.append(param.default)
            elif (order_item != None) and (order_item not in arg_dict):
                raise PositionalParameterNotAvailable(
                    ("Parameter '{}' found in positional param list " +
                     "but not in provided argument dictionary."
                    ).format(order_item),
                    order_item = order_item,
                    param = param,
                    index = index,
                    **err_data)
            elif (order_item == None) and (param_name not in arg_dict):
                raise ParameterNotAvailable(
                    ("Parameter '{}' not found in argument dictionary " +
                     "and no default was provided."
                    ).format(param_name),
                    param_name = param_name,
                    param = param,
                    index = index,
                    **err_data)
            else:
                raise RuntimeError(
                     "Should be unreachable. There's an error in " +
                     "`exam_gen.util.dynamic_call` somewhere." )
        elif param.kind == Parameter.VAR_POSITIONAL:
            raise VarPositionalArgumentNotSupported(
                ("Dynamic Call API doesn't support variadic positional " +
                 " variables"),
                param_name = param_name,
                param = param,
                index = index,
                **err_data)
        elif param.kind == Parameter.KEYWORD_ONLY:
            if param_name in arg_dict:
                used_args.append(param_name)
                kwargs[param_name] = arg_dict[param_name]
            elif param.default != Parameter.empty:
                used_args.append(param_name)
                kwargs[param_name] = param.default
            else:
                raise ParameterNotAvailable(
                    ("Parameter '{}' not found in argument dictionary " +
                     "and no default was provided."
                    ).format(param_name),
                    param_name = param_name,
                    param = param,
                    index = index,
                    **err_data)
        elif param.kind == Parameter.VAR_KEYWORD: pass
        else:
            raise RuntimeError(
                "Should be unreachable. There's an error in " +
                "`exam_gen.util.dynamic_call` somewhere.")

    for arg in arg_dict:
        if arg not in used_args:
            kwargs[arg] = arg_dict[arg]

    return func(*args, **kwargs)


class DynamicCallError(RuntimeError):
    """
    Parent error for various things that could go wrong with
    `dynamic_call`. Exists to make it easier to provide good error messages
    to users.

    Params:
      func (function): The function we failed to call
      message (string): The error message
      **meta (dict): Whatever additional metadata is reasonable.
    """
    def __init__(self, message = "", **meta):
        super().__init__(message)
        self.meta = meta

class PositionalParameterNotAvailable(DynamicCallError):
    """
    Thrown when a parameter in the list of ordered parameters is not
    found in the provided argument dictionary. This usually is an error
    on the part of the caller of `dynamic_call`.
    """
    pass

class ParameterNotAvailable(DynamicCallError):
    """
    Thrown when a parameter required by the function being called isn't
    available in argument dictionary. This is usually because the input
    function to `dynamic_call` is asking for some input that the caller
    of `dynamic_call` wasn't expected.
    """
    pass

class VarPositionalArgumentNotSupported(DynamicCallError):
    """
    This error is thrown when a `VAR_POSITIONAL` argument is used by the
    called function, which the `dynamic_call` interface doesn't support.
    """
    pass
