import attr
import inspect
import textwrap
from exam_gen.mixins.config.value import ConfigValue
import exam_gen.util.attrs_wrapper as wrapped
import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@wrapped.attrs()
class ConfigGroup():
    """
    A group of configuration variables and their subgroups. Only to be used
    within `exam_gen.mixins.config` and the class shouldn't be used outside of
    that. Some of the instance functions will be accessible to the user
    however.

    Attributes:

       members (dict): A dict of values and subgroups indexed by name.

       doc (str): The docstring explain what's within this group of
         configuration settings.

       ctxt (class or instance): The current evaluation context for this
         group. It's used to update the assignment context when values are
         defined or modified.

       root (ConfigGroup): The root of the configuration tree. If it's set
         to self then this instance is the root.

       path (list[str]): The path of attrs needed to access this config group
         as a list of strings.
    """

    members = attr.ib(factory=dict, init=False)
    doc = attr.ib(default="", converter=textwrap.dedent)
    ctxt = attr.ib(default=None)
    _root = attr.ib(default=None)
    path = attr.ib(factory=list)

    def __init__(self, **kwargs):
        log.debug("Initializing ConfigGroup with args: %s",kwargs)
        self.__attrs_init__(**kwargs)
        self.update_context(self.ctxt)

    def update_context(self, ctxt):
        log.debug("Updating context for %s to %s",
                  self, ctxt)
        self.ctxt = ctxt
        for member in self.members.values():
            if isinstance(member, ConfigGroup):
                member.update_ctxt(self._ctxt)

    @property
    def root(self):
      return self if self._root == None else self._root

    def path_string(self):
        return ".".join(self.path)

    def __getattr__(self, name):
        log.debug("Getting attr %s from ConfigGroup %s",
                  name, self.path_string())

        if name in self.members:
            if isinstance(self.members[name], ConfigValue):
                return self.members[name].value
            elif isinstance(self.members[name], ConfigGroup):
                return self.members[name]
            else:
                assert False, "Internal Error: member of invalid type."

        # Otherwise fall back to the usual attribute mechanism, if that fails
        # throw a more informative exception than the default AttributeError.
        #
        # Note: The `try` clause here should always fail as `__getattr__` is
        #       only called when `__getattribute__` (and therefore
        #       `object.__getattr__`) has already failed. It's only here so
        #       that we get access to the main `attribute
        try:
            _ = super().__getattribute__(name)
        except AttributeError as err:
            # TODO : better error message
            raise AttributeError from err
        else:
            assert False, "Unreachable"


    def __setattr__(self, name, value):
        if not hasattr(super(),"members"):
            super().__setattr__(name, value)
        elif name in self.members:
            self.members[name].value = value
            self.members[name].ctxt = self.ctxt
        else:
            super().__setattr__(name, value)

    def update(self, other):
        if  not isinstance(other, ConfigGroup):
            raise SomeError

        for (name, member) in other.members.items():
            if name in self.members:
                ours = self.members[name]
                theirs = member
                if (isinstance(ours, ConfigValue)
                    and isinstance(theirs, ConfigValue)):
                    ours.ctxt = theirs.ctxt
                    ours.doc = copy(theirs.doc)
                    ours.value = deepcopy(theirs.value)
                    self.members[name] = ours
                elif (isinstance(ours,ConfigGroup)
                      and isinstance(theirs, ConfigGroup)):
                    ours.doc = copy(theirs.doc)
                    ours.update(theirs)
                    self.members[name] = ours
                else:
                    raise SomeError
            else:
                if isinstance(member, ConfigValue):
                    self.new_value(
                        name = name,
                        value = deepcopy(member.value),
                        doc = copy(member.doc),
                    )
                    self.members[name].ctxt = member.ctxt
                elif isinstance(member,ConfigGroup):
                    self.new_group(
                        name = name,
                        doc = member.doc,
                    )
                    self.members[name].update(member)
                else:
                    assert False, "Internal Error: Member of invalid type."
        return self

    @property
    def value_dict(self):
        output = dict()
        for (name, member) in self.members.items():
            if isinstance(member, ConfigValue):
                output[name] = member.value
            elif isinstance(member, ConfigGroup):
                output[name] = member.value_dict()
        return output

    def new_value(self, name, default = None, doc = None):
        self.members[name] = ConfigValue(
            value = default,
            doc = doc,
            ctxt = self.ctxt,
            path = self.path + [name],
            )

    def new_group(self, name, doc = None):
        self._members[name] = ConfigGroup(
            doc = doc,
            ctxt = self.ctxt,
            path = self.path + [name],
            root = self.root(),
            )

    def clone(self, **kwargs):
        args = {
            'doc': self.doc,
            'path': self.path + [name],
            'ctxt': self.ctxt,
        }
        args.update(**kwargs)
        return ConfigGroup(**args).update(self)
