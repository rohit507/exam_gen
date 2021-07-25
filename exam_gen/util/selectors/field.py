import attr

import exam_gen.util.logging as logging

from collections import Iterable

log = logging.new(__name__, level="DEBUG")

@attr.s(init=False)
class FieldSelect():

    selector = attr.ib()

    substring = attr.ib(default=True)
    strip_string = attr.ib(default=True)
    case_sensitive = attr.ib(default=False)

    def __new__(cls, *args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0:
            if isinstance(args[0], cls):
                return args[0]

        return super(FieldSelect, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        """
        Sorta idempotent normalised new.
        """

        if len(args) == 1 and len(kwargs) == 0:
            if isinstance(args[0], str):
               pass
            elif isinstance(args[0], dict):
               kwargs = args[0]
            elif isinstance(args[0], Iterable):
               args = list(args[0])

        return self.__attrs_init__(*args, **kwargs)

    def match(self, key):

        selector = self.selector

        if not self.case_sensitive:
            selector = selector.lower()
            key = key.lower()

        if self.strip_string:
            selector = selector.strip()
            key = key.strip()

        is_match = False

        if self.substring:
            is_match = selector in key
        else:
            is_match = selector == key

        return is_match


    def select(self, record, supress_error = False):
        """
        Returns the value of the field which matches the selector
        """

        for (k, v) in record.items():
            if self.match(k):
                return v

        if supress_error:
            return None

        raise RuntimeError("No field with selector {} found in {}".format(
            self.selector, record))
