import copy
import inspect
import logging
import textwrap
from pprint import *

__all__ = ["new"]

colored_logs_loaded = False

try:
    import coloredlogs
    colored_logs_loaded = True
except ModuleNotFoundError:
    pass


def new(name=None, level='WARNING'):
    """
    Create a new logger for this module. Once made, the logger can then
    can be used as with any logger from the python standard library's
    [`logging`](https://docs.python.org/3/library/logging.html) module.

    This lets us consolidate a bunch of nice tweaks to output format in one
    place instead of having to repeat the same logger initialization in
    every module.

    ??? Example "Example Use"

        Basic use should include the following at the start of every module:

        ```python
        import exam_gen.util.logging

        log = exam_gen.util.logging.new(__name__)
        ```

        During development you will probably want to show debug level messages
        by adding a `#!py level = 'DEBUG'` parameter to the call, but once
        you're not actively debugging then removing the parameter will only
        show warnings of `#!py 'WARNING'` level or above.

        Once the logger is initialized you can use the functions
        `#!py debug()`, `#!py info()`, `#!py warning()`, `#!py error()`, and
        `#!py critical()`. All of these functions take a format string and
        arguments in the same style as the string `%` operator, as in the
        following example:

        ```python
        (var_name, obj_name, number) = ("foo", "bar", 12)
        log.debug("Looking up variable `%s` in object `%s` and found: `%(result)03d`",
                  var_name, obj_name,result = number)
        ```

        Which would produce a raw message of *"Looking up variable \`foo\` in
        object \`bar\` and found: 012"*, that will be sent to`#!py STDOUT` with
        some additional formatting and metadata.
        See the python [string format operator](https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting)
        docs for more details on how to use format strings.


    Parameters:

       name (str): The name of the logger, used to differentiate between log
           messages from different modules. If the value is `None` then this
           function will attempt to get the module name of the caller by
           analyzing the stacktrace.

       level (log_lvl): The lowest level of messages this logger should show
           at runtime. From lowest to highest, the available levels are
           `#!py 'NOTSET'`, `#!py 'DEBUG'`, `#!py 'INFO'`, `#!py 'WARNING'`,
           `#!py 'ERROR'`, and `#!py 'CRITICAL'`.


    """

    # If we're missing a specific name for the logger then we can try to grab
    # it from the stack trace.
    if name == None and len(inspect.stack()) > 1:
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        name = mod.__name__
        del frm

    log = logging.getLogger(name)

    # I want to keep coloredlogs a dev dependency so that it doesn't need to
    # be installed when the library is just being used to make an exam.
    if colored_logs_loaded:
        # We modify this, since the original color for the level-name isn't that
        # visible on terminals w/ a dark theme.
        field_styles = copy.deepcopy(coloredlogs.DEFAULT_FIELD_STYLES)
        field_styles.update({ 'levelname': {'bold': True, 'color':'yellow'}})

        coloredlogs.install(
            level=level,
            logger=log,
            field_styles = field_styles,

            # Default coloredlog format is way too noisy, and hard to quickly read.
            fmt='%(levelname)s@%(name)s:%(lineno)s:\n%(message)s\n',
        )

    return log
