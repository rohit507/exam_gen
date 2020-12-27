import exam_gen.util.logging as logging
import inspect
import textwrap
import attr
import exam_gen.util.attrs_wrapper as wrapped

log = logging.new(__name__, level="DEBUG")

@wrapped.attrs()
class ConfigValue():
    """
    This is an internal class that stores a single configuration value.

    Attributes:

       value (Any): The actual value stored. Ideally only immutable terms go
         here. It's a default term if ctxt is a class, an actual setting
         value otherwise.

       doc (str): The docstring for the value. Will be used when docs are
         generated for any configuration superclasses.

       ctxt (Class or Instance): The location where the default or runtime
         value was last set.

       path (List[str]): The chain of attributes that you need to walk in
         order to get to this element from the root config group.
    """

    value = attr.ib(default=None)
    doc   = attr.ib(converter=textwrap.dedent,
                     default="",
                     kw_only=True)
    ctxt  = attr.ib(default=None,
                     kw_only=True)

    path  = attr.ib(default=[],
                     kw_only=True)

    def __init__(self, value, **kwargs):
        self.__attrs_init__(value, **kwargs)

    def path_string(self):
        return ".".join(self._path)

    @property
    def instance_context(self):
        return not inspect.isclass(self.ctxt)

    def as_dict(self):
        dict = attr.asdict(self)