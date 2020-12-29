import attr
import inspect
import textwrap
from pprint import *
from copy import *
from exam_gen.mixins.config.value import ConfigValue
import exam_gen.util.attrs_wrapper as wrapped
import exam_gen.util.logging as logging

log = logging.new(__name__)

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
        log.debug("Initializing ConfigGroup with args:\n\n%s",
                  pformat(kwargs))

        self.__attrs_init__(**kwargs)
        self.update_context(self.ctxt)

    def set_docstring(self, docstring, value=None):
        """
        Set a new docstring for this config group or a in the group subvalue.
        This will only do anything if set in the class definition. Setting it
        at runtime (after the docstring has been generated) will do nothing.

        Parameters:

           docstring (str): The new docstring to use.
           value (str): If left to the default (`None`) then the function will
              update the docstring of this config group. If it's set to the
              name of a value then it'll update the docstring of that value.
        """
        if value == None:
            self.doc = textwrap.dedent(docstring)
        else:
            self.members[value] = textwrap.dedent(docstring)

    def update_context(self, ctxt):
        log.debug(textwrap.dedent(
            """
            Updating context for:

              ConfigGrouup:
              %s

              New Ctxt: %s
            """),
                  pformat(attr.asdict(self)),
                  pformat(ctxt)
        )
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
        log.debug("Getting attr '%s' from ConfigGroup %s.",
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

    def apply_value_dict(
            self,
            values,
            preserved_ctxts=[],
            ignore_missing_members=False,
            preserve_self_set=False):
        """
        Will update the values of this settings group using terms from the
        value dictionary that's been passed to it.

        !!! Important ""
            Note that the value dict can always be missing values and subgroups
            that are defined in the config group. Those entries will simply not
            be changed.

            The `ignore_missing_members` parameter determines how we handle the
            opposite case where the value dict has entries that are **not**
            already defined in the config group.

        Parameters:

           values (dict): The value dict we're using to update this config
              group.

           preserved_ctxts (list[ctxt]): If a value if from any of these
              contexts we're not going to override them with values from the
              dictionary.

           ignore_missing_members (bool): If true we'll ignore any values in
              the input dict that aren't defined in the config group. Otherwise
              we'll throw an error if the dict is trying to set some value that
              isn't in the control group.

           preserve_self_set (bool): Ignored if there's any entries in the
              `preserved_ctxts` otherwise if true will add the current context
              (and if the current context is an instance its parent class) to
              the list of `preserved_ctsts`.


        ??? Todo "Feature Todo List"
            - Better error handling and messages
        """
        if (len(preserve_ctxts) == 0) and preserve_self_set:
            preserve_ctxts = [self.ctxt]
            if not inspect.isclass(ctxt):
                preserve_ctxts += [type(self.ctxt)]

        for (key, value) in values.items():

            # Catch extra keys in dict
            if (key not in self.members) and (not ignore_missing_members):
                raise SomeError # TODO

            if key in self.members:

                # Insert key subtree into subgroup
                if isinstance(self.members[key], ConfigGroup):
                    self.members[key].apply_value_dict(
                        value, preserved_ctxts, ignore_missing_members)

                # If we can override this
                if (isinstance(self.members[key], ConfigValue)
                    and (self.members[key].ctxt not in preserved_ctxts)):
                        setattr(self, key, value)



    def new_value(self, name, default = None, doc = "", value = None):
        """
        Will create a new value member in this control group which looks
        like a normal attribute variable.

        Parameters:

           name (str): The name of the new value attribute, must be a valid
              python identifier.

              !!! Example
                  Once created the value becomes an attribute like any other.

                  ```python
                  group = ConfigGroup(...)

                  group.new_value('foo', ...)

                  group.foo = 12
                  print(group.foo)
                  ```

                  And so on ...

           default (Any): The value the variable should be set to initially.

           doc (str): The docstring for the value, will be used in the
              auto-generated documentation.

           value (Any): Alias for `default` that is used when `default` is
              set to `None`. Ignored otherwise.
        """

        self.members[name] = ConfigValue(
            value = default if default != None else value,
            doc = doc,
            ctxt = self.ctxt,
            path = self.path + [name],
            )

    def new_group(self, name, doc = ""):
        """
        Creates a new subgroup for this config group. You can add more
        values and subgroups to it the same way you can to this caller.

        Parameters:

           name (str): The name of the subgroup, must be a valid python
              identifier. Will be accessible as an attribute just like a value
              created with `new_value()`.

           doc (str): The docstring for the subgroup, used when documentation
              is autogenerated at class creation. (Note: This is well before an
              instance is initialized)
        """

        self.members[name] = ConfigGroup(
            doc = doc,
            ctxt = self.ctxt,
            path = self.path + [name],
            root = self.root,
            )

    def clone(self, **kwargs):
        """
        Create a copy of this ConfigGroup with potentially updated arguments.

        Parameters:

           **kwargs (Any): Any parameters that the `ConfigGroup(...)`
              initializer takes.
        """
        args = {
            'doc': self.doc,
            'path': self.path,
            'ctxt': self.ctxt,
        }
        args.update(**kwargs)
        return ConfigGroup(**args).update(self)
