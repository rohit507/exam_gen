import graphlib
import inspect
import itertools
import textwrap
from pprint import *

import attr
import attr.validators as valid
import jinja2
import pkg_resources

import exam_gen.templates

import exam_gen.util.logging as logging

from .group import ConfigGroup
from .value import ConfigValue

log = logging.new(__name__)

def var_empty_docstring(var_name, desc):
    return textwrap.dedent("""
        {desc}

        Setting a field (e.g. `#!py {var_name}.foo`) that was created in
        some superclass (`#!py ParentClass`) during class definition:
        ```python
        class OurClass(ParentClass):
           {var_name}.foo = "some value"
        ```

        Setting a field during instance runtime (i.e. in a function or outside
        of the class definition):
        ```python
        class OurClass(ParentClass):

           def set_foo(self, some_value):
              self.{var_name}.foo = some_value

        our_instance = OurClass()
        our_instance.{var_name}.foo = 13
        ```

        !!! Tip ""
            Child classes of `#!py OurClass` will inherit any updates to settings
            that are defined at the class level. Changes made at runtime will
            **not** be inherited by subclasses and only affect a single object.
        """).format(var_name = var_name, desc = textwrap.dedent(desc))

@attr.s
class ConfigDocFormat():
    """
    Class to store formats for printing out configuration setting information.
    Tries to handle a lot of heavy lifting and provide a nicer interface for
    common case definitions and a convenient interface for template authors.

    Attributes:

       doc (str): the base docstring to be used by the template.

       template (str or jinja2.Template): Template that is used to render
          the final docstring for a full config group.

          ??? Info "Available Template Variables"
              These will be variables the template has access to:

              - `doc`: primary documentation for the root config group
              - `val_table`: dict w/ various info on each var.
                  - `exists`: Does the table exist? Other entries will not be
                       there if this is false.
                  - `name`: The name of the table
                  - `headers`: column headings (in definition order)
                  - `entries`: list of dicts for each table entry, where the
                       keys are the column headings and the values are the
                       formatted strings.

                       **Note:** Any variables available to format specifiers, like
                       `is_group` or `is_val`, will also be made available
                       to the template under each entry.

              - `group_table`: dict w/ various info on groups
                  - `exists`: Does the table exist
                  - `name`: The name of the table
                  - `headers`: column headings (in definition order)
                  - `entries`: list of dicts for each table entry, where the
                       keys are the column headings and the values are the
                       formatted strings.

                       **Note:** Any variables available to format specifiers, like
                       `is_group` or `is_val`, will also be made available
                       to the template under each entry.

              - `combined_table`: A table of combined vars and groups
                  - `exists`: Does the table exist
                  - `name`: The name of the table
                  - `headers`: column headings (in definition order)
                  - `entries`: list of dicts for each table entry, where the
                       keys are the column headings and the values are the
                       formatted strings.

                        **Note:** Any variables available to format specifiers, like
                        `is_group` or `is_val`, will also be made available
                        to the template under each entry.

                  - `group_col_widths`: map from keys to colwidths for a group.
                       Should be used to set the `colspan` parameter in table
                       cells if needed.

                       The width of a column will be `0` if it should be
                       omitted.

                  - `val_col_widths`: map from keys to colwidths for a value
                       Should be used to set the `colspan` parameter in table
                       cells if needed.

                       The width of a column will be `0` if it should be
                       omitted.

       val_table_name (dict): The title for the value table.

       val_table_format (dict): Dictionary used to set the columns the val
          table. Each key should be a column heading, with the value being
          a format string used to format the entry.

          Use `None` if you don't want the val table to appear at all. The
          table will also be ommitted if there are no entries for it.

          ??? Info "Available Format Specifiers"
              These are the keys that will be available to the format strings.

               - `is_val`: is this a variable?
               - `is_group`: is this a group?
               - `defined_in`: the module where their was defined / last updated
               - `val`: the value the term was set to
               - `val_repr`: thst string representation of a value.
               - `doc`: the provided docstring for the term
               - `name`: the name of the term, only the final component
               - `path`: the full pathname of the value

       group_table_name (dict): The title for the subgroup table.

       group_table_format (dict): Dictionary used to set the columns the group
          table. Each key should be a column heading, with the value being
          a format string used to format the entry.

          Use `None` if you don't want the group table to appear at all. The
          table will also be ommitted if there are no entries for it.

          ??? Info "Available Format Specifiers"
              These are the keys that will be available to the format strings.

               - `is_val`: is this a variable?
               - `is_group`: is this a group?
               - `defined_in`: the module where their was defined / last updated
               - `doc`: the provided docstring for the term
               - `name`: the name of the term, only the final component
               - `path`: the full pathname of the value

       combine_tables (bool): Do we combine the value and group tables into a
           single joint table?

       combined_table_name (str): The title for the combined table.

       combined_table_header (list[str]): An ordered list of headers to use for
           a combined entry table. These should match keys in the `table_format`
           parameters.

       recurse_entries (bool): If `True` we recurse to all entries and subgroups
           otherwise we only print the direct children of the config group.

       other_vars (dict): other variables to be passed to the template directly.
    """


    template = attr.ib()

    doc = attr.ib(default="")

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

    val_table_name = attr.ib(
        default="",
        validator=valid.instance_of(str),
    )

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

    val_table_headers = attr.ib(
        validator=valid.optional(
            valid.and_(
                valid.instance_of(list),
                valid.deep_iterable(
                    valid.instance_of(str)
                ),
            )
        ),
    )

    @val_table_headers.default
    def val_table_headers_default(self):
        hide_doc = True # Docs must be the first statement to show up
        """
        List of headers for the value table.
        """
        if self.val_table_format != None:

            keys = list(self.val_table_format)

            log.debug(textwrap.dedent(
                """
                Attempting to get ordered headers for val table:

                  Dict:
                  %s

                  List:
                  %s
                """),
                      pformat(self.val_table_format),
                      pformat(keys),
            )

            return keys
        else:
            return []

    group_table_headers = attr.ib(
        validator=valid.optional(
            valid.and_(
                valid.instance_of(list),
                valid.deep_iterable(
                    valid.instance_of(str)
                ),
            )
        ),
    )

    @group_table_headers.default
    def group_table_headers_default(self):
        hide_doc = True # Docs must be the first statement to show up
        """
        List of headers for the group table
        """
        if self.group_table_format != None:
            return list(self.group_table_format)
        else:
            return []

    group_table_name = attr.ib(
        default="",
        validator=valid.instance_of(str),
    )

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

    combine_tables = attr.ib(
        default=False,
        validator=valid.instance_of(bool),
    )

    combined_table_name = attr.ib(
        default="",
        validator=valid.instance_of(str),
    )

    combined_table_headers = attr.ib(
        validator=valid.optional(
            valid.and_(
                valid.instance_of(list),
                valid.deep_iterable(
                    valid.instance_of(str)
                ),
            )
        ),
    )

    @combined_table_headers.default
    def combined_table_headers_default(self):
        hide_doc = True # Docs must be the first statement to show up
        graph = graphlib.TopologicalSorter()
        table_edges = list(zip(self.val_table_headers[::2],
                               self.val_table_headers[1::2]))
        table_edges += list(zip(self.group_table_headers[::2],
                                self.group_table_headers[1::2]))
        for (start, end) in table_edges:
            graph.add(end, start)
        return list(graph.static_order())


    @staticmethod
    def get_colwidths(combined_cols, elem_cols):
        hide_doc = True # Docs must be the first statement to show up
        col_widths = dict()

        # get whether each combined cell is in the group cols
        is_member = list(map(lambda x:x in elem_cols, combined_cols))

        log.debug(textwrap.dedent(
            """
            Generating Colspan widths:

               Combined Cols:
               %s

               Elem Type Cols:
               %s

               Membership List:
               %s
            """),
            pformat(combined_cols),
            pformat(elem_cols),
            pformat(is_member),
        )


        for (ind, col) in enumerate(combined_cols):
            if is_member[ind]:
                # Get list of members that follow, grouped by whether they're
                # within our elements of interest
                next_elems = is_member[ind+1:]
                next_groups = itertools.groupby(
                    next_elems)

                # This overly tedious unpacking is because itertools.groupby
                # returns a list of tuples with iterators in them. I'm just
                # converting them into a more sane format. You could make this
                # more efficient but I can't be arsed.
                next_cols = []
                for k, group in next_groups:
                    grp_list = []
                    for item in list(group):
                        grp_list += [item]
                    next_cols += [grp_list]

                # every valid entry is 1 col wide
                width = 1

                # If we're followed by a bunch of entries not in our set
                # then we can grow wide enough to fill those too.
                if ((len(next_cols) != 0)
                    and (len(next_cols[0]) != 0)
                    and (not next_cols[0][0])):
                    width += len(next_cols[0])

                log.debug(textwrap.dedent(
                    """
                    For col '%s' at index '%s':

                       Next Members:
                       %s

                       Next Groups:
                       %s

                       Final Width:
                       %s
                    """),
                          col,
                          ind,
                          next_elems,
                          next_cols,
                          width)

                col_widths[col] = width
            else:
                # invalid entries should be dropped
                col_widths[col] = 0

        return col_widths



    recurse_entries = attr.ib(
        default=True,
        validator=valid.instance_of(bool)
    )

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

    @property
    def combined_group_col_widths(self):
        hide_doc = True # Docs must be the first statement to show up
        """
        The column widths for a group entry in a combined table
        """

        widths = ConfigDocFormat.get_colwidths(
            self.combined_table_headers,
            self.group_table_headers
        )

        log.debug(textwrap.dedent(
            """
            Genrating Group Col Widths:

               Combined Headers:
               %s

               Group Headers:
               %s

               Result Widths:
               %s
            """),
                  pformat(self.combined_table_headers),
                  pformat(self.group_table_headers),
                  pformat(widths),
        )

        return widths

    @property
    def combined_val_col_widths(self):
        hide_doc = True # Docs must be the first statement to show up
        """
        The column widths for a value entry in a combined table
        """

        widths = ConfigDocFormat.get_colwidths(
            self.combined_table_headers,
            self.val_table_headers
        )

        log.debug(textwrap.dedent(
            """
            Genrating Value Col Widths:

               Combined Headers:
               %s

               Value Headers:
               %s

               Result Widths:
               %s
            """),
                  pformat(self.combined_table_headers),
                  pformat(self.val_table_headers),
                  pformat(widths),
        )

        return widths

    @classmethod
    def get_val_data(cls, config_val):
        hide_doc = True # Docs must be the first statement to show up
        """
        Exact and format data for a ConfigValue
        """
        return {config_val.path_string(): {
            'is_val': True,
            'is_group': False,
            'val': config_val.value,
            'val_repr': repr(config_val.value),
            'doc': config_val.doc,
            'defined_in': config_val.ctxt.__qualname__,
            'name': config_val.path[-1],
            'path': config_val.path_string(),
            }}

    @classmethod
    def get_group_data(cls, config_group):
        hide_doc = True # Docs must be the first statement to show up
        """
        Extract and format data for a ConfigGroup
        """
        return {config_group.path_string(): {
            'is_val': False,
            'is_group': True,
            'doc': config_group.doc,
            'name': config_group.path[-1],
            'path': config_group.path_string(),
            }}

    @classmethod
    def collect_group_data(self, config_group, recurse=False):
        hide_doc = True # Docs must be the first statement to show up
        """
        Run through the members of a ConfigGroup and gather all the template
        data in a dictionary, where the keys are the path to each term.
        This will recurse if necessary.
        """
        data = dict()
        for member in config_group.members.values():
            if isinstance(member, ConfigValue):
                data.update(ConfigDocFormat.get_val_data(member))
            else:
                data.update(ConfigDocFormat.get_group_data(member))
                if recurse:
                    data.update(
                        ConfigDocFormat.collect_group_data(member, recurse))
        return data


    @classmethod
    def format_data(self, format_dict, data):
        hide_doc = True # Docs must be the first statement to show up
        """
        Format all the values in a format dictionary given a particular
        dataset.
        """

        output = dict()
        for (key, format_string) in format_dict.items():
            output[key] = format_string.format_map(data)
        for (key, value) in data.items():
            if key not in output:
                output[key] = value

        log.debug(textwrap.dedent(
            """
            Formatting Data:

              Format String:
              %s

              Data:
              %s

              Result:
              %s
            """),
                  pformat(format_dict, depth = 6,indent = 2),
                  pformat(data, depth = 6, indent = 2),
                pformat(output, depth = 6, indent = 2),
        )

        return output

    def format_val_data(self, val_data):
        hide_doc = True # Docs must be the first statement to show up
        """
        format a value table entry if we have a formatter for it.
        """
        if self.val_table_format != None:
            return self.format_data(self.val_table_format, val_data)
        else:
            return dict()

    def format_group_data(self, group_data):
        hide_doc = True # Docs must be the first statement to show up
        """
        Format a group table entry if we have a formatter for it.
        """
        if self.group_table_format != None:
            return self.format_data(self.group_table_format, group_data)
        else:
            return dict()

    def format_member_data(self, data):
        hide_doc = True # Docs must be the first statement to show up

        log.debug("Formatting Member Data:\n\n%s", pformat(data))

        output = None
        if data['is_val']:
            output = self.format_val_data(data)
        else:
            output = self.format_group_data(data)

        log.debug("Formatted Member Data:\n\n%s", pformat(output))

        return output


    def process_config_group(self, config):
        hide_doc = True # Docs must be the first statement to show up
        """
        Run through a configuration group to produce all the variables that
        will be fed to the template.
        """

        # Process data from config group
        rows = self.collect_group_data(config, self.recurse_entries)
        formatted = dict()
        for (path, data) in rows.items():
            formatted[path] = self.format_member_data(data)
            log.debug("Formatted `%s` data to get:\n\n%s",
                      path, pformat(formatted[path]))

        vals = {path: data for (path, data) in formatted.items() if data['is_val']}
        groups = {path: data for (path, data) in formatted.items() if data['is_group']}

        log.debug(textwrap.dedent(
            """
            Control Group Raw Contents:

              Rows:
              %s

              Vals:
              %s

              Groups :
              %s
            """),
                  pformat(rows),
                  pformat(vals),
                  pformat(groups),
        )

        # Figure out which tables should exist in our output.
        val_table_can_exist = (
            (len(vals) > 0)
            and (self.val_table_format != None))
        group_table_can_exist = (
            (len(groups) > 0)
            and (self.group_table_format != None))
        combined_table_exists = (
            (val_table_can_exist and group_table_can_exist)
            and self.combine_tables)
        val_table_exists = (not combined_table_exists) and val_table_can_exist
        group_table_exists = (not combined_table_exists) and group_table_can_exist

        log.debug(textwrap.dedent(
            """
            Table Existence Data:

              Val Table Can Exist: %s
              Grp Table Can Exist: %s

              Val Table Exists: %s
              Grp Table Exists: %s
              Cmb Table Exists: %s
            """),
            val_table_can_exist,
            group_table_can_exist,
            val_table_exists,
            group_table_exists,
            combined_table_exists,
        )

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
            output['val_table']['headers'] = self.val_table_headers
            output['val_table']['entries'] = [
                vals[path] for path in sorted(vals.keys())]

        # generate group table data
        output['group_table']['exists'] = group_table_exists
        if group_table_exists:
            output['group_table']['name'] = self.group_table_name
            output['group_table']['headers'] = self.group_table_headers
            output['group_table']['entries'] = [
                groups[path] for path in sorted(groups.keys())]

        # generate group table data
        output['combined_table']['exists'] = combined_table_exists
        if combined_table_exists:
            output['combined_table']['name'] = self.combined_table_name
            output['combined_table']['headers'] = self.combined_table_headers
            output['combined_table']['entries'] = [
                formatted[path] for path in sorted(formatted.keys())]
            output['combined_table']['group_col_widths'] = (
                self.combined_group_col_widths)
            output['combined_table']['val_col_widths'] = (
                self.combined_val_col_widths)

        log.debug("Processed Doc Data:\n\n%s",pformat(output))

        return output


    @staticmethod
    def render_docs(docs_format, config_group, empty_doc = ""):
        """
        Render the documentation for a config group using the provided
        formatter.
        """
        processed_data = docs_format.process_config_group(config_group)

        if (processed_data['val_table']['exists']
            or processed_data['group_table']['exists']
            or processed_data['combined_table']['exists']):

            return docs_format.template.render(processed_data)
        else:
            return empty_doc

template_env = jinja2.Environment(
    loader = jinja2.PackageLoader('exam_gen'),
    )

default_format = ConfigDocFormat(
    template = template_env.get_template(
        'mkdocs/default_config_doc_format.jn2.html'
    ),
    val_table_name = "Configuration Values",
    val_table_format = {
        'Value Name':"`#!py {path}`",
        'Description':"{doc}",
        'Default':"`#!py {val_repr}`",
        #'Defined In':"`#!py {defined_in}`",
        },
    val_table_headers = [
        'Value Name',
        'Description',
        'Default',
        #'Defined In'
    ],
    group_table_name = "Configuration Subgroups",
    group_table_format = {
        'Value Name':"`#!py {path}`",
        'Description':"{doc}",
        },
    group_table_headers = ['Value Name', 'Description'],
    combine_tables = True,
    combined_table_name = "Configuration Values and Subgroups",
    combined_table_headers = [
        'Value Name',
        'Description',
        'Default',
        #'Defined In'
    ],
    recurse_entries = True,
)
""" A default ConfigDocFormat instance to be used in most places. """
