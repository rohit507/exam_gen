import wrapt
import inspect
import textwrap
import jinja2
from copy import deepcopy
from exam_gen.mixins.prepare_attrs import *
from types import new_class
import logging
import coloredlogs
import sys
from pprint import pformat
import collections

log = logging.getLogger(__name__)
field_styles = coloredlogs.DEFAULT_FIELD_STYLES
field_styles.update({ 'levelname': {'bold': True, 'color':'yellow'}})
coloredlogs.install(
    level='DEBUG',
    logger=log,
    fmt='%(levelname)s@%(name)s:%(lineno)s:\n%(message)s\n',
    field_styles = field_styles
)


__all__ = ["Settings","create_settings_mixin","SettingsManager"]

def create_settings_mixin(
        name,
        var_name,
        **kwargs
        ):

    def populate(namespace):

        def prepare_attrs(cls, name, bases, env):

            log.warn("Preparing Attrs for '%s' with cls %s and initial env: %s",
                  name, cls, env)

            if hasattr(super(cls), "__prepare_attrs__"):
                env = super(cls).__prepare_attrs__(name, bases, env)

            if var_name not in env:
                env[var_name] = Settings(
                    context = cls,
                    root = None,
                    path = var_name,
                    **kwargs
                )
            else:
                env[var_name] = env[var_name]._clone(context=cls)

            cls_settings = getattr(cls, var_name, None)
            if cls_settings != None:
                log.debug("Class %s already has variable %s while preparing " +
                      "attrs for %s: Updating", cls, var_name, name)
                env[var_name]._update(cls_settings)

            log.debug("Final env when preparing %s with %s: %s",
                  name, cls, env)

            return env

        def init_subclass(cls, **kwargs):
            log.debug("Initializing subclass for '%s' with cls %s",
                  name, cls)
            super(cls).__init_subclass__(**kwargs)
            setattr(cls, var_name,
                    getattr(cls, var_name)._clone(context=cls))

            docs = getattr(cls, var_name)._gen_docs()
            if cls.__doc__ != None:
                cls.__doc__ = textwrap.dedent(cls.__doc__)
                cls.__doc__ += "\n\n" + docs
            else:
                cls.__doc__ = getattr(cls, var_name)._gen_docs()

            log.debug("Generated docs for %s during subclass init: \n%s",
                  cls, cls.__doc__)

            log.debug("subclass init for %s has __dir__: %s",
                  cls, dir(cls))

        def init(self, *vargs, **kwargs):
            cls = type(self)

            log.debug("Initializing %s in %s of type %s: %s %s",
                  name, self, cls, vargs, kwargs)

            super(PrepareAttrs, cls).__init__(self, *vargs, **kwargs)
            data = getattr(self, var_name, None)
            if data != None:
                setattr(self, var_name, data._clone(context=self))

        namespace["__prepare_attrs__"] = classmethod(prepare_attrs)
        namespace["__init_subclass__"] = classmethod(init_subclass)
        namespace["__init__"] = init


        return namespace

    return new_class(
        name,
        (),
        {'metaclass': PrepareAttrs},
        exec_body = populate,
        )

SettingsManager = create_settings_mixin(
    name = "SettingsManager",
    var_name = "settings",
    desc = "",
    table_title = "Settings",
    table_header = "Name",
    desc_header = "Description",
    default_header = "Default Value",
    )


class Setting(wrapt.ObjectProxy):

    __name = None

    __short_desc = None
    __long_desc = None
    __options = None

    __context = None
    __root = None
    __path = None
    __doc__ = None

    def __init__(
            self,
            name,
            value,
            context,
            root,
            path,
            desc = None,
            short_desc = None,
            long_desc = None,
            options = None,
    ):
        super(Setting, self).__init__(value)

        log.debug("Initializing new setting with %s", {
            'name' : name,
            'value' : value,
            'context' : context,
            'root' : root,
            'path' : path,
            })

        self.__name = name
        self.__context = context
        self.__root = root
        self.__path = path

        (short_desc, long_desc) = format_description(desc, short_desc, long_desc)
        self.__short_desc = short_desc
        self.__long_desc = long_desc

        self.__options = dict()
        if options != None:
            for (name, desc) in options.items():
                self.set_option(name, desc)

    def _as_dict(self):
        return {
            'name': self.__name,
            'value': deepcopy(self.__wrapped__),
            'long_desc': self.__long_desc,
            'short_desc': self.__short_desc,
            'options': self.__options.copy(),
            'context': self.__context,
            'root': self.__root,
            'path': self.__path,
        }

    def _settings_dict(self):
        return {self._path_string: (repr(self.__wrapped__), self.__long_desc)}

    @property
    def _path_string(self):
        return ".".join(self.__path)

    def __get__(self, obj, objtype = None):
        return self

    def __set__(self, obj, value):
        if isinstance(value, wrapt.ObjectProxy):
            self.__wrapped__ = value.__wrapped__
        else:
            self.__wrapped__ = value

    def _clone(self, options = {}, **kwargs):
        properties = self._as_dict()
        properties['options'].update(options)
        properties.update(kwargs)
        return Setting(**properties)

    def set_option(self, name, desc):
        self.__options[name] = textwrap.dedent(desc)

    def _gen_docs(self):

        template_vars = {
            'long_desc': self.__long_desc,
            'table_title': "Available Options",
            'table_header': "Options",
            'desc_header': "Description",
            'table': self.__options,
            }

        log.debug("Generating docs for %s with template vars:\n %s",
              self._path_string, pformat(template_vars))

        self.__doc__ = setting_docs_template.render(template_vars)
        return self.__doc__



class Settings:

    __members = {}

    __short_desc = None
    __long_desc = None
    __context = None
    __root = None
    __path = None
    __table_title = None
    __table_header = None
    __desc_header = None
    __default_header = None

    def __init__(self,
                 context,
                 root = None,
                 desc = None,
                 short_desc = None,
                 long_desc = None,
                 path = [],
                 table_title = "Available Settings",
                 table_header = "Settings",
                 desc_header = "Description",
                 default_header = "Default",
                 frozen = False
    ):

        log.debug("Initializing new settings group with %s", {
            'context' : context,
            'root' : root,
            'path' : path,
            })

        self.__members = dict()
        self.__context = context

        (short_desc, long_desc) = format_description(desc, short_desc, long_desc)
        self.__short_desc = short_desc
        self.__long_desc = long_desc

        self.__root = self if root == None else root

        if isinstance(path, str):
            self.__path = path.split(".")
        elif isinstance(path, list):
            self.__path = path

        self.__table_title = table_title
        self.__table_header = table_header
        self.__desc_header = desc_header
        self.__default_header = default_header

    def _as_dict(self):
        return {
            'members': {k: v._as_dict() for (k,v) in self.__members.items()},
            'context': self.__context,
            'root': None if self == self.__root else self.__root,
            'path': self.__path,
            'long_desc': self.__long_desc,
            'short_desc': self.__short_desc,
            'table_title': self.__table_title,
            'table_header': self.__table_header,
            'desc_header': self.__desc_header,
            'default_header': self.__default_header,
            }

    def _settings_dict(self):
        output = dict()
        for v in self.__members.values():
            output.update(v._settings_dict())
        return output

    def __apply_new_members(self, members):
        for (name, d) in members.items():
            member_params = d._as_dict()
            member_params['name'] = name
            member_params.pop('root', None)
            member_params.pop('path', None)
            if isinstance(d, Setting):
                self.new_setting(override = True, **member_params)
            elif isinstance(d, Settings):
                member_params.pop('context', None)
                member_params.pop('members', None)
                self.new_setting_group(override = True, **member_params)
                self.__members[name].__apply_new_members(d.__members)
            else:
                raise SomeError

    def _clone(self, **kwargs):
        log.debug("cloning '%s' with override args '%s'",
              self, kwargs)
        params = self._as_dict()
        params.pop('members', None)
        params.pop('root', None)
        params.update(kwargs)
        clone = Settings(**params)
        clone.__apply_new_members(self.__members)
        return clone

    def _update(self, other):
        log.debug("updating '%s' with data in '%s'",
              self, other)
        self.__apply_new_members(other.__members)

    def __getattr__(self,name):

        # Try getting a setting from the members
        if name in self.__members:
            if isinstance(self.__members[name], Setting):
                return self.__members[name].__get__(self, type(self))
            elif isinstance(self.__members[name], Settings):
                return self.__members[name]
            else:
                raise SomeError

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
            raise AttributeError from err
        else:
            assert False, "Unreachable"

    def __setattr__(self, name, value):
        if name in self.__members:
            self.__members[name].__set__(self, value)
        elif hasattr(self, name):
            super().__setattr__(name, value)
        else:
            raise SomeError


    @property
    def _instance_context(self):
        return not inspect.isclass(self.__context)

    @property
    def _path_string(self):
        return ".".join(self.__path)

    def new_setting(
            self,
            name : str,
            value = None,
            default = None,
            override = False,
            **kwargs
            ):

        log.debug("creating new setting %s in %s",name, self._path_string)
        if value == None:
            value = default


        if (not override) and self._instance_context:
            log.debug("Problematic context of '%s'",
                  self.__context)
            raise SomeError

        if (not override) and (name in self.__members):
            raise SomeError

        attrs = self.__dir__()
        if (name in attrs) or ("_Settings" + name in attrs):
            log.debug("Failed to add setting %s to %s with __dir__: %s",
                  name, self, attrs)
            raise SomeError

        self.__members[name] = Setting(
            name,
            value = value,
            context = kwargs.pop('context', self.__context),
            root = self.__root,
            path = self.__path + [name],
            **kwargs)

    def new_setting_group(
            self,
            name : str,
            override = False,
            **kwargs
            ):

        if (not override) and self._instance_context:
            raise SomeError

        if (not override) and (name in self.__members):
            raise SomeError

        attrs = self.__dir__()
        if (name in attrs) or ("_Settings" + name in attrs):
            log.debug("Failed to add setting group %s to %s with __dir__: %s",
                  name, self, attrs)
            raise SomeError

        self.__members[name] = Settings(
            context = self.__context,
            root = self.__root,
            path = self.__path + [name],
            **kwargs)

    def _get_setting_docs(self):
        doc_dict = dict()
        for (name, val) in self.__members.items():
            if isinstance(val, Setting):
                val._gen_docs()
                doc_dict[val._path_string] = val.__doc__
            elif isinstance(val, Settings):
                doc_dict.update(val._get_setting_docs())
            else:
                raise SomeError
        return doc_dict

    def _gen_docs(self):

        settings =collections.OrderedDict(
            sorted(self._settings_dict().items()))

        template_vars = {
            'long_desc': self.__long_desc,
            'table_title': self.__table_title,
            'table_header': self.__table_header,
            'desc_header': self.__desc_header,
            'default_header': self.__default_header,
            'table': settings,
            }

        log.debug("Generating docs for %s with template vars:\n %s",
              self._path_string, pformat(template_vars))

        self.__doc__ = settings_docs_template.render(template_vars)
        return self.__doc__


def format_description(desc, short_desc, long_desc):

    if (desc == None) and (short_desc == None) and (long_desc == None):
        raise SomeError

    if desc != None:
        desc = textwrap.dedent(desc).strip()

    if long_desc != None:
        long_desc = textwrap.dedent(long_desc).strip()
    elif long_desc == None and desc != None:
        long_desc = desc
    elif long_desc == None and short_desc != None:
        long_desc = short_desc

    if short_desc != None:
        short_desc = short_desc.strip()
    elif short_desc == None:
        desc = desc if desc != None else long_desc
        short_desc = textwrap.shorten(desc, width = 80)

    return (short_desc, long_desc)

setting_docs_template_string = """
{{long_desc}}

{% if table != {} %}
**{{table_title}}**
<table markdown="block">
<tr markdown="block">
<th markdown="block">
{{table_header}}
</th>
<th markdown="block">
{{desc_header}}
</th>
</tr>
{% for (name, desc) in table.items() %}
<tr markdown="block">
<td markdown="block">
`{{name}}`
</td>
<td markdown="block">
{{desc}}
</td>
</tr>
{% endfor %}
</table>
{% endif %}
"""

setting_docs_template = jinja2.Template(textwrap.dedent(
    setting_docs_template_string))

settings_docs_template_string = """
<details class=abstract markdown="block">
<summary markdown="span">{{table_title}}</summary>
{{long_desc}}
{% if table != {} %}
<table markdown="1" width="100%">
<tr markdown="block" width="100%">
<th markdown="block">
{{table_header}}
</th>
<th markdown="block">
{{default_header}}
</th>
<th markdown="block" width="auto">
{{desc_header}}
</th>
</tr>
{% for (name, (def, desc)) in table.items() %}
<tr markdown="block" width="100%">
<td markdown="block">
`#!python {{name}}`
</td>
<td markdown="block">
`#!python {{def}}`
</td>
<td markdown="block" width="auto">
{{desc}}
</td>
</tr>
{% endfor %}
</table>
{% endif %}
</details>
"""

settings_docs_template = jinja2.Template(textwrap.dedent(
    settings_docs_template_string))
