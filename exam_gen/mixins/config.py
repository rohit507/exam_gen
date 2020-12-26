import exam_gen.util.logging as logging
import exam_gen.util.attrs_wrapper as attrs_wrapper
import attr
import attr.validators as valid
import wrapt
import textwrap
import graphlib
import itertools
import jinja2
import types
from pprint import *
from copy import *

log = logging.new(__name__, level="DEBUG")

default_attrs_params = {
    'order': False,
    'collect_by_mro': True,
    'attrs_init': True,
    }

def attrs(**kwargs):
    params = deepcopy(default_attrs_params)
    params.update(kwargs)
    return attrs_wrapper.wrap(**params)

@attr.s()
class ConfigVal():

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

    def as_dict(self):
        return attr.asdict(self)

@attrs()
class ConfigGroup():

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
            if isinstance(self.members[name], ConfigVar):
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
                if isinstance(ours, ConfigVal) and isinstance(theirs, ConfigVal):
                    ours.ctxt = theirs.ctxt
                    ours.doc = copy(theirs.doc)
                    ours.value = deepcopy(theirs.value)
                    self.members[name] = ours
                elif isinstance(ours,ConfigGroup) and isinstance(theirs, ConfigGroup):
                    ours.doc = copy(theirs.doc)
                    ours.update(theirs)
                    self.members[name] = ours
                else:
                    raise SomeError
            else:
                if isinstance(member, ConfigVal):
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

    def value_dict(self):
        output = dict()
        for (name, member) in self.members.items():
            if isinstance(member, ConfigVal):
                output[name] = member.value
            elif isinstance(member, ConfigGroup):
                output[name] = member.value_dict()
        return output

    def new_value(self, name, value = None, doc = None):
        self.members[name] = ConfigVal(
            value = value,
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



@attrs()
class ConfigDocFormat():

    template = attr.ib(
        converter=textwrap.dedent,
        )
    """
    Template to use when rendering the terms.

    Available Vars:
       'doc': primary documentation for the root config group
       'val_table': dict w/ various info on each var.
           'exists': Does the table exist? Other entries will not be there if
                     this is false.
           'name': The name of the table
           'headers': column headings (in definition order)
           'entries': list of dicts for each table entry
       'group_table': dict w/ various info on groups
           'exists': Does the table exist
           'name': The name of the table
           'headers': column headings (in definition order)
           'entries': list of dicts for each table entry
       'combined_table': A table of combined vars and groups
           'exists': Does the table exist
           'name': The name of the table
           'headers': column headings (in definition order)
           'entries': list of dicts for each table entry
           'group_col_widths': map from keys to colwidths for a group
           'val_col_widths': map from keys to colwidths for a value
    """

    @template.validator
    def __template_validator(self, attr, val):
        if isinstance(val, str):
            self.template = jinja2.Template(textwrap.dedent(val))
            return None
        elif isinstance(val, jinja2.Template):
            self.template = val
        else:
            raise TypeError(
                ("ConfigDocFormat expects a template of type `str` or of " +
                 "type `jinja2.Template`. Instead got a template of type {}"
                ).format(type(val)))


    @staticmethod
    def __normalize_format_dict(format_dict):
        return {key: textwrap.dedent(val) for (key,val) in format_dict.items()}

    val_table_format = attr.ib(
        default=None,
        converter=__normalize_format_dict,
        validator=valid.optional(
            valid.deep_mapping(
                key_validator=valid.instance_of(str),
                value_validator=valid.instance_of(str),
            )
        ),
    )

    """
    Should be a dict where keys are column headings and rows
    are format strings for the available settings. Use 'None' to specify
    there should be no var table.

    The val table will be dropped if there's no entries.

    Available Vars:
       'is_val': is this a variable?
       'is_group': is this a group?
       'defined_in': the module where their was defined / last updated
       'val': the value the term was set to
       'val_repr': thst string representation of a value.
       'doc': the provided docstring for the term
       'name': the name of the term, only the final component
       'path': the full pathname of the value
    """

    val_table_name = attr.ib(
        default="",
        validator=valid.instance_of(str),
    )
    """
    The name of the value table
    """

    group_table_format = attr.ib(
        default=None,
        converter=__normalize_format_dict,
        validator=valid.optional(
            valid.deep_mapping(
                key_validator=valid.instance_of(str),
                value_validator=valid.instance_of(str),
            )
        ),
    )
    """
    Should be a dict where keys are column headings and rows
    are format strings for the available groups. Set to 'None' to specify that
    there should be no group table.

    The group table will be automatically dropped if there's no entries.

    Available Vars:
       'is_val': is this a variable?
       'is_group': is this a group?
       'doc': the provided docstring for the group
       'name': the name of the group
       'path': the full pathname of the group
    """

    group_table_name = attr.ib(
        default="",
        validator=valid.instance_of(str),
    )
    """
    the name of the aubgroup table
    """

    combine_tables = attr.ib(
        default=False,
        validator=valid.instance_of(bool),
    )
    """
    Should the group and var tables include entries from subgroups as well?

    The expectation is that if this chosen, then a number of the columns
    specified for the group and var tables should overlap and their order
    should be consistent.
    """

    combined_table_name = attr.ib(
        default="",
        validator=valid.instance_of(str),
    )
    """
    The name of the combined table
    """

    combined_table_header = attr.ib(
        validator=valid.optional(
            valid.and_(
                valid.instance_of(list),
                valid.deep_iterable(
                    valid.instance_of(str)
                ),
            )
        ),
    )
    """
    List of column headers for a combined table
    """

    @combined_table_header.default
    def combined_table_header_default(self):
        graph = graphlib.TopologicalSorter()
        table_edges = zip(self.val_table_headers[::2],
                              val_table_headers[1::2])
        table_edges += zip(self.group_table_headers[::2],
                                self.group_table_headers[1::2])
        for (start, end) in table_edges:
            graph.add(end, start)
        return list(graph.sorted_order())



    def combined_group_col_widths(self):
        output = dict()
        combined_col_members = map(lambda x:x in self.group_table_headers,
                                 self.combined_cols)
        for col in self.group_table_headers:
            if col in self.combined_cols:
                loc = self.combined_cls.index(col)
                next_entries = itertools.groupby(
                    combined_col_members[loc+1:])[0]
                width = 1
                if not next_entries[0]:
                    width += len(next_entries)
                output[col] = width
        return output


    def combined_val_col_widths(self):
        output = dict()
        combined_col_members = map(lambda x:x in self.val_table_headers,
                                 self.combined_cols)
        for col in self.val_table_headers:
            if col in self.combined_cols:
                loc = self.combined_cols.index(col)
                next_entries = itertools.groupby(
                    combined_col_members[loc+1:])[0]
                width = 1
                if not next_entries[0]:
                    width += len(next_entries)
                output[col] = width
        return output

    recurse_entries = attr.ib(
        default=True,
        validator=valid.instance_of(bool)
    )
    """
    Should we recurse through all subgroups and gather every entry?
    """

    other_vars = attr.ib(
        factory=dict,
        validator=valid.and_(
            valid.instance_of(dict),
            valid.deep_mapping(
                key_validator=valid.instance_of(str),
                value_validator=(lambda _a,_b,_c: True),
            ),
        ),
    )
    """
    Other variables to be made available to the template
    """

    def __init__(self, **kwargs):
        self.__attrs_init__(**kwargs)


    @classmethod
    def get_val_data(config_val):
        return {config_val.path_string(): {
            'is_val': True,
            'is_group': False,
            'val': config_val.value,
            'val_repr': repr(config_val.value),
            'doc': config_val.doc,
            'defined_in': config_val.ctxt.__module__.__qualname__,
            'name': config_val.path[-1],
            'path': config_val.path_string(),
            }}

    @classmethod
    def get_group_data(config_group):
        return {config_group.path_string(): {
            'is_val': False,
            'is_group': True,
            'doc': config_group.doc,
            'name': config_group.path[-1],
            'path': config_group.path_string(),
            }}

    @classmethod
    def collect_group_data(config_group, recurse=False):
        data = dict()
        for member in config_group.__members.values():
            if isinstance(member, ConfigVal):
                data.update(ConfigDocFormat.get_val_data(member))
            else:
                data.update(ConfigDocFormat.get_group_data(member))
                if recurse:
                    data.update(
                        ConfigDocFormat.collect_group_data(member, recurse))
        return data

    @property
    def val_table_headers(self):
        return self.val_table_format.keys() if self.val_table_format != None else []

    @property
    def group_table_headers(self):
        return self.group_table_format.keys() if self.group_table_format != None else []

    @classmethod
    def format_data(self, format_dict, data):
        output = dict()
        for (key, format_string) in format_dict:
            output[key] = format_string.format(**data)
        return output

    def format_val_data(self, val_data):
        if self.val_table_exists:
            return self.format_data(self.val_table_format, val_data)
        else:
            return dict()

    def format_group_data(self, group_data):
        if self.group_table_exists:
            return self.format_data(self.group_table_format, group_data)
        else:
            return dict()

    def process_config_group(self, config):

        # Process data from config group
        rows = self.collect_group_data(config, self.recurse_entries)
        vals = {path: data for (path, data) in rows.items() if data['is_var']}
        groups = {path: data for (path, data) in rows.items() if data['is_group']}

        # Figure out which tables should exist in our output.
        val_table_can_exist = (
            (len(vals) > 0)
            and (self.val_table_format != None))
        group_table_can_exist = (
            (len(groups) > 0)
            and (self.group_table_format != None))
        combined_table_exists = (
            ((len(vals) == 0) or (self.val_table_format != None))
            and ((len(groups) == 0) or (self.group_table_format != None))
            and (len(vals) + len(groups) > 0)
            and self.combine_tables)
        val_table_exists = (not combined_table_exists) and val_table_can_exist
        group_table_exists = (not combined_table_exists) and group_table_can_exist

        # generate top level output data
        output = dict()
        output.update(self.other_vars)
        output['doc'] = config.doc
        output['val_table'] = dict()
        output['group_table'] = dict()
        output['combined_table'] = dict()

        # generate val table data
        output['val_table']['exists'] = val_table_exists
        if val_table_exists:
            output['val_table']['name'] = self.val_table_name
            output['val_table']['headers'] = self.val_table_header
            output['val_table']['entries'] = [
                vals[path] for path in sorted(vals.keys())]

        # generate group table data
        output['group_table']['exists'] = group_table_exists
        if group_table_exists:
            output['group_table']['name'] = self.group_table_name
            output['group_table']['headers'] = self.group_table_header
            output['group_table']['entries'] = [
                groups[path] for path in sorted(groups.keys())]

        # generate group table data
        output['combined_table']['exists'] = combined_table_exists
        if combined_table_exists:
            output['combined_table']['name'] = self.combined_table_name
            output['combined_table']['headers'] = self.conbimed_table_header
            output['combined_table']['entries'] = [
                rows[path] for path in sorted(rows.keys())]
            output['combined_table']['group_col_widths'] = (
                self.combined_group_col_widths())
            output['combined_table']['val_col_widths'] = (
                self.combined_val_col_widths())


    @staticmethod
    def render_docs(docs_format, config_group):
        return docs_format.template.render(
            docs_format.process_config_group(config_group)
            )

config_classes = dict()

def new_config_superclass(
        class_name,
        var_name,
        class_doc = "",
        var_doc = "",
        doc_style = None,
        ):
    """
    Generates a new superclass with a sp ... finish this documentation bit,
    it's important.
    """

    __var_name = "__" + var_name

    def prepare_attrs(cls, name, bases, env):
        if hasattr(super(cls), "__prepare_attrs__"):
            env = super(cls).__prepare_attrs__(name, bases, env)

        class_config = ConfigGroup(doc = var_doc, ctxt = cls, path = [var_name])
        if var_name in env:
            log.debug(prepare_attrs_debug_msg(
                "Updating config for {name} with data from prepare_attrs of {supr}.",
                name, cls, bases, class_config, env[var_name]))

            class_config.update(env[var_name])


        superclass_config = getattr(cls, __var_name, None)
        if superclass_config != None:
            log.debug(prepare_attrs_debug_msg(
                "Updating config for {name} with post-init data from {cls}.",
                name, cls, bases, class_config, superclass_config))
            class_config.update(superclass_config)

        env[var_name] = class_config

        return env

    def init_subclass(cls, **kwargs):

        log.debug("Running init class for {class_name} on class {cls}",
                  class_name=class_name, cls=cls)

        super(config_classes[class_name], cls).__init_subclass__(**kwargs)

        class_config = getattr(cls, var_name, None)
        if class_config == None:
            assert False, "Internal Error: w/ config class gen."
        class_config = class_config.clone(ctxt=cls)
        setattr(cls, __var_name, class_config)
        docstring = ConfigDocFormat.render_docs(doc_style, class_config)

        def property_getter(self):
            return getattr(self,__var_name)

        property_getter.__doc__ = docstring

        def property_setter(self, value):
            setattr(self, __var_name, value)

        property_class = type(
            "_{}_ConfigProperty".format(class_name),
            (type(property()),),
            { '__getattr__': class_config.__getattr__,
              '__setattr__': class_config.__setattr__,
            })

        setattr(cls, var_name, property_class(property_getter, property_setter))

    def init(self, *vargs, **kwargs):
        super(config_classes[class_name], self).__init__(self, *vargs, **kwargs)
        class_config = getattr(self, __var_name, None)
        if class_config == None:
            assert False, "Internal Error: w/ config class gen."
        instance_config = class_config.clone(ctxt=self)
        setattr(self, __var_name, instance_config)

    def populate_class_namespace(namespace):
        namespace["__prepare_attrs__"] = classmethod(prepare_attrs)
        namespace["__init_subclass__"] = classmethod(init_subclass)
        namespace["__init__"] = init
        namespace["__doc__"] = class_doc

        return namespace

    config_classes[class_name] = types.new_class(
        class_name,
        (),
        {'metaclass':PrepareAttrs},
        exec_body = populate_class_namespace,
    )

    return config_classes[class_name]

def prepare_attrs_debug_msg(msg, name, cls, bases, us, them):

    properties = dict(
        name = name,
        cls = cls.__qualname__,
        bases = bases,
        our_ctxt = us.ctxt,
        our_path_string = us.path_string(),
        our_values = pformat(
            us.value_dict(),
            indent = 8),
        their_path_string = them.path_string(),
        their_ctxt = them.ctxt,
        their_value = pformat(
            them.value_dict(),
            indent=8),
        supr=super(cls)
        )

    template = """
        During PrepareAttrs of {name} with {cls}:
        {msg}

          {name} Data:
            Bases: {bases}
            Path: {our_path_string}
            Context: {our_ctxt}
            Data: {our_values}

          {cls} Data:
            Path: {their_path_string}
            Context: {their_ctxt}
            Data: {their_values}
        """

    return textwrap.dedent(template).format(
        msg=msg.format(properties),
        **properties,
    )
