import attr

from .field import *


from collections import Iterable
import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s(init=False)
class DocSelect():
    """
    Associates record fields with documents and sub-documents
    """

    mapping = attr.ib()
    """
    Map from a document tree to various field selectors
    """

    selector = attr.ib(default=FieldSelect)
    """
    The field selector creator to use when none is specified, should be a
    callable that takes a user provided value and returns
    """

    norm_field = attr.ib(default=lambda f: (f,None))
    """
    A function that turns a field input into a field and some metadata.

    Used to allow mappings to contain additional info that might be useful.
    """

    def __new__(cls, *args, **kwargs):
        """
        Sorta idempotent normalised new.
        """

        if len(args) == 1 and len(kwargs) == 0:
            if isinstance(args[0], DocSelect):
                return args[0]

        return super(DocSelect, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        """
        Sorta idempotent normalised new.
        """

        if len(args) == 0 and len(kwargs) >= 0 and 'mapping' not in kwargs:
            _kwargs = dict()

            for k in ['selector', 'norm_field']:
                if k in kwargs: _kwargs[k] = kwargs.pop(k)

            kwargs = {'mapping': kwargs} | _kwargs

        self.__attrs_init__(*args, **kwargs)


    def __attrs_post_init__(self):

        _mapping = dict()

        for (k,v) in self.mapping.items():
            (field, meta) = self.norm_field(v)
            _mapping[k] = (self.norm_map_entry(field), meta)

        self.mapping = _mapping

    def norm_map_entry(self, entry):
        if isinstance(entry, DocSelect):
            return entry
        elif isinstance(entry, FieldSelect):
            return entry
        elif isinstance(entry, dict):
            return type(self)(mapping=entry,
                              selector=self.selector,
                              norm_field=self.norm_field)
        else:
            return self.selector(entry)

    def select(self, record, supress_error = False, with_meta = False):
        """
        Given a record produce a mapped dictionary of values.
        """

        result = dict()

        # Turn with_meta into a function that will turn the (match, meta) pair
        # into the result we want.
        if not callable(with_meta):
            as_tuple = lambda f, m: (f,m)
            only_field = lambda f, m: f
            with_meta = as_tuple if with_meta else only_field

        # Go through and grab the matching fields while assembling them
        # properly
        for (k, (fld, meta)) in self.mapping.items():
             match = fld.select(record, supress_error)
             if match != None:
                 result[k] = with_meta(match, meta)

        return result
