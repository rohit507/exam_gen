from copy import copy, deepcopy
from pprint import pformat, pprint
from textwrap import dedent, indent
from collections import Iterable

import makefun
import inspect
import textwrap

import attr
import attr.validators as valid

import exam_gen.util.logging as logging

log = logging.new(__name__, level="WARNING")

setup_class_attr = "__user_setup_args__"
setup_sig_name = "__user_setup_sig__"
setup_func_attr = "__user_setup_arg__"
setup_func_name = "user_setup"

class UserSetup():
    """
    Having this as a parent should allow subclasses to register new arguments
    that will be made available to a user setup function w/ can be run to
    generate some metadata for a template.
    """

    def __pre_user_setup__(self):
        """
        Override to do something before user setup, should call `super()` to
        allow other classes to do their setup.

        Returns:

            A log dictionary or at least the dictionary from the call to
            `super()`
        """
        return dict()

    def __post_user_setup__(self, setup_vars):
        """
        Override to do something after the user setup.
        Should call `super(setup_vars)` to allow other classes to do their
        thing.

        Parameters:

            setup_vars (dict): The variable returned by the user setup function.
               Will be 'None' if no user setup function is defined.

        Returns:

            A log dictionary or at least the dictionary from a call to super.
        """
        return dict()

    def _run_user_setup(self, **kwargs):
        """
        Will run the user setup function if it exists with whatever kwargs
        are given to this function, using the registered providers for any
        args that are missing.pip

        Should generally be called without arguments.
        """

        # Run the pre-setup hook
        pre_setup_log = self.__pre_user_setup__()

        # Get the argument data from the class dictionary
        arg_data_dict = getattr(self, setup_class_attr, dict())

        arg_dict = dict()

        # Either run the generator hooks or use the value in the kwargs
        for (arg_name, data) in arg_data_dict.items():
            if arg_name in kwargs:
                arg_dict[arg_name] = kwargs[arg_name]
            else:
                arg_dict[arg_name] = data['fun'](self)

        # grab the setup function
        setup_func = getattr(self, setup_func_name, None)

        results = None

        # Run it with the generated arguments
        if setup_func != None:

            log.debug("Calling user_setup with args: \n\n %s",
                        pformat(arg_dict))

            log.debug("user_setup has signature: \n\n %s",
                        inspect.signature(setup_func))

            try:
                if arg_dict != dict():
                    results = setup_func(**arg_dict)
                else:
                    results = setup_func()
            except TypeError as err:
                if not err.args[0].startswith("user_setup"):
                    raise err
                raise TypeError(("{} function should have signature "
                                 "'def {}{}'. \n\n"
                                 "This error might because no `{}` function is "
                                 "defined for the class `{}` with the correct "
                                 "sugnature."
                                 ).format(setup_func_name,
                                          setup_func_name,
                                          getattr(self,setup_sig_name),
                                          setup_func_name,
                                          type(self).__name__
                                          )) from err

        # Run the post setup hook.
        post_setup_log = self.__post_user_setup__(results)

        # return some logging information
        return {'pre_setup': pre_setup_log,
                'return': results,
                'post_setup': post_setup_log}

    def __init_subclass__(cls, *vargs, **kwargs):
        """
        Creates a dict in the class with all the available arguments, iterates
        over all the functions that are marked as `user_setup_args`, adds them
        to the class's setup arg dictionary.

        !!! Todo
            Generate Docs for the User Setup function as needed. Will probably
            need some templating stuff.
        """
        super().__init_subclass__(*vargs, **kwargs)

        # Gather all the user setup args this class has
        user_setup_args = dict()

        for attr_name in dir(cls):
            attr = getattr(cls, attr_name, None)
            if (attr != None) and inspect.isfunction(attr):
                func_data = getattr(attr, setup_func_attr, None)
                if (func_data != None):
                    user_setup_args[func_data['arg']] = func_data

        # Save that information to a class attribute
        setattr(cls, setup_class_attr , user_setup_args)

        # Generate the stub function w/ documentation
        setup_sig = user_setup_sig(user_setup_args)

        log.debug("Making user_setup func with signature: %s", setup_sig)

        func_base = getattr(cls, setup_func_name, user_setup_stub)

        setup_func = makefun.with_signature(
            setup_sig, func_name = setup_func_name)(func_base)
        setup_func.__doc__ = user_setup_stub.__doc__
        setup_docs = user_setup_docs(setup_sig, setup_func, user_setup_args)
        setup_func.__doc__ = setup_docs

        # Attach that stub to the new class, so that it shows up in the
        # docs with all the assorted metadata.
        setattr(cls, setup_sig_name, setup_sig)
        setattr(cls, setup_func_name, setup_func)

def user_setup_stub(self, *args, **kwargs):
    """
    Override this function in your code, otherwise it won't customize stuff.
    """
    raise NotImplementedError(
        "Please overload the `user_setup` function in your class")

def user_setup_docs(new_sig, stub_func, arg_dict):
    """
    Generate the docs for this function

    !!! Todo
        Make this add stuff from the signature
    """
    new_doc = dedent(
        """
        {old_doc}

        !!! Todo
            We need a nicer output format here, but this will do for the
            moment.

        Function Signature: `py {func_sig}`

        Arg Metadata:
        ```py
        {arg_meta}
        ```
        """
    ).format(
        old_doc = stub_func.__doc__,
        func_sig = pformat(new_sig),
        arg_meta = indent(pformat(arg_dict), "  "),
    )

    return new_doc

def user_setup_sig(arg_dict):
    """
    Generate the inspect.Signature we want our output function to have.
    """

    params = list()
    params.append(inspect.Parameter(
        'self',
        inspect.Parameter.POSITIONAL_OR_KEYWORD))

    for arg_name in sorted(arg_dict.keys()):
        data = arg_dict[arg_name]
        param = inspect.Parameter(
            arg_name,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=data['typ'])
        params.append(param)

    return inspect.Signature(params)

def setup_arg(arg_name=None, func=None, *, doc=None):
    """
    Decorator to register a new user setup argument, will just annotate the
    return function with a few parameters so that `UserSetup.__init_subclass__`
    can pick it up from the class environment.
    """

    if inspect.isfunction(arg_name) and (func == None):
        func = arg_name
        arg_name = None

    def wrapper(setup_func):
        metadata = dict()
        metadata['arg'] = arg_name if arg_name != None else setup_func.__name__
        metadata['doc'] = doc if doc != None else setup_func.__doc__
        metadata['doc'] = textwrap.dedent(metadata['doc']).strip()
        metadata['typ'] = inspect.signature(setup_func).return_annotation
        metadata['fun'] = setup_func
        setattr(setup_func, setup_func_attr, metadata)
        return setup_func

    if func == None:
        return wrapper
    else:
        return wrapper(func)
