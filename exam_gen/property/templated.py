import attr
import textwrap
import functools

from pprint import *
from pathlib import *
from jinja2 import *
from copy import *

from .has_settings import HasSettings
from .has_dir_path import HasDirPath
from .document import Document

from exam_gen.util.versioned_option import add_versioned_option
from exam_gen.util.file_ops import dump_str, dump_yaml
from exam_gen.util.stable_hash import stable_hash

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

__all__ = ["Templated",
           "TemplateSpec",
           "build_template_spec",
           "add_template_var"]

@attr.s
class Templated(HasSettings, HasDirPath, Document):
    """
    This is for documents that have the ability to produce a template from user
    input that can be filled out by tools later on.
    """

    _template_manager = attr.ib(default=None, kw_only=True)

    settings.new_group('template',doc=
                       """
                       Settings for how templates should be applied by this
                       object.
                       """)

    settings.template.new_value(
        'format_dir',
        default = None,
        doc =
        """
        The format for this document. When not null it'll be used as a
        sub-folder in the search path for new templates.

        For instance if the format is `"latex"` and `base_template` is
        `"exam.jn2"` the template engine will search in
        `<template_dir>/latex/exam.jn2` before `<template_dir>/exam.jn2`
        """)

    settings.template.new_value(
        'format_ext',
        default = None,
        doc =
        """
        The extension used by this type of document, modifies the search
        path of the templates.

        If extension is 'tex' and you're trying to find 'foo.jn2', the loader
        will first search for a template named 'foo.jn2.tex' then 'foo.jn2'.
        This stacks with the `format_directory` and other template search
        options.
        """)

    settings.template.new_value(
        'output',
        default = "output",
        doc =
        """
        the body of the output file's name. If you want the build directory
        to write out "output.tex" then set this to `"output"` and
        `settings.template.format_ext` to `"tex"`
        """)

    settings.template.new_value(
        'embedded',
        default = None,
        doc =
        """
        The base template file that's used for this document/sub-document when
        it's meant to be included within another document.
        """)

    settings.template.new_value(
        'standalone',
        default = None,
        doc =
        """
        The template to use when building this file as a standalone document.
        """)

    settings.template.new_value(
        'search_path',
        default = list(),
        doc =
        """
        The directories where templates are to be located. Can be either a single
        path string like `"templates"` (without trailing path seperators) or a
        list of path strings.

        These paths are relative to the file in which they are defined.
        For example specifying `settings.template_dir = "templates"` in
        `question1/TimerQuestion.py` will make the system look for templates in
        the `question1/templates/` directory.

        Any directories specified will be **added** to the search path for
        templates. Directories specified in a `Classroom` will be searched
        before those for a `Question` and template directories specified in
        an `Exam` will be looked at last.
        """)

    settings.template.new_value(
        'template_dir',
        default = None,
        doc =
        """
        Convenience alias for a single-entry `settings.template.search_path`.
        This directory will be the first place that the templating engine looks
        for templates.
        """)

    settings.template.new_value(
        'jinja_opts',
        default = dict(),
        doc =
        """
        Init parameters for a
        [jinja2 environment]
        (https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.Environment)
        to be used when building this document.
        """)

    def build_template_spec(self, build_info=None):
        """
        build a TemplateSpec that describes how to apply all the various
        templates for each object.

        Each superclass can augment the template spec with more information

        It should call `template_spec(name)` on subquestions, appropriately
        name them and so on. Note that `template_spec` makes sure that
        settings from this document are properly set in the `TemplateSpec`
        object.

        The result should be a recursive TemplateSpec that can be built in
        one shot by whatever is managing the build process.

        Note: This assumes that we're using the `embedded` rather than the
        `standalone` template unless specified in `build_info.is_standalone`
        """

        template = self.settings.template.embedded
        if ((build_info != None and build_info.is_standalone)
            or template == None):
            template = self.settings.template.standalone

        spec = TemplateSpec(Path(template))

        if build_info != None:
            build_info = build_info.where(is_standalone = False)
            if build_info.exam_format != None:
                spec.context['format'] = build_info.exam_format

        spec.subtemplates['questions'] = dict()

        for (ind, (name, qn)) in enumerate(self.questions.items()):

            spec.subtemplates['questions'][name] = qn.template_spec(
                build_info=build_info)

            spec.subtemplates['questions'][name].context['index'] = ind

        return spec

    def __get_search_path(self):

        path = list()

        if isinstance(self._parent_doc, Templated):
            path = self._parent_doc.__get_search_path()

        add_root = lambda p : Path(self.root_dir, p)

        string_paths = list()
        if self.settings.template.template_dir != None:
            string_paths.append(self.settings.template.template_dir)
        string_paths += ['./',*self.settings.template.search_path]

        path += list(map(add_root,string_paths))

        return path

    def __get_jinja_opts(self):
        opts = dict()
        if isinstance(self._parent_doc, Templated):
            opts = deepcopy(self._parent_doc.__get_jinja_opts())
        opts |= self.settings.template.jinja_opts
        return opts

    def template_spec(self, out_file=None, build_info=None):



        spec = self.build_template_spec(build_info)

        spec.path += self.__get_search_path()

        spec.jinja_opts = __jinja_default_opts__ | self.__get_jinja_opts()
        spec.format_dir = self.settings.template.format_dir
        spec.format_ext = self.settings.template.format_ext

        return spec

def build_template_spec(name,
                        spec,
                        ctxt=None,
                        out_file=None,
                        debug_dir=None):

    if ctxt == None: ctxt = dict()

    template_file = None
    template_str  = None


    # Figure out whether our template is a file or string.
    if spec.template == None:
        raise RuntimeError("Template spec has no template given")
    elif isinstance(spec.template, Path):
        template_file =  spec.template
    else:
        template_str = textwrap.dedent(spec.template).strip()

    # build out jinja template env
    environment = Environment(**spec.jinja_opts)
    template = None

    # Retrieve the file from our loader if needed.
    file_name = None
    if template_str == None:

        # get our final path, after including all the format specs
        dir_path = list()
        for entry in spec.path:
            dir_path.append(entry)
            if spec.format_dir != None:
                dir_path.append(str(Path(entry, spec.format_dir)))

        # build our loader
        loader_list = [FileSystemLoader(dir_path)]
        if spec.format_dir != None:
            loader_list.append(PackageLoader(
                "exam_gen",
                "templates/{}".format(spec.format_dir)
            ))
        loader_list.append(PackageLoader("exam_gen","templates"))
        loader = ChoiceLoader(loader_list)

        # try getting our source w/ the format ext
        if spec.format_ext != None:
            try:
                file_n = "{}.{}".format(str(template_file),
                                         spec.format_ext)
                (template_str,_,_) = loader.get_source(environment, file_n)
                template = loader.load(environment, file_n)
                template_file = file_n
            except TemplateNotFound:
                pass

        # and just doing it normally
        if template_str == None:
            (template_str,_,_) = loader.get_source(environment, str(template_file))
            template = loader.load(environment, str(template_file))

    # Otherwise just get it from the string.
    else:
        template = environment.from_string(template_str)

    # Get the path we're outputting a file to
    out_path = out_file if out_file else spec.out_file
    spec.out_file = str(out_path)

    # Get the extension we use for debug output
    if out_path != None:
        out_ext = "".join(Path(out_path).suffixes)
    elif spec.format_ext != None:
        # log.warning(out_path)
        out_ext = "." + spec.format_ext
    else:
        out_ext = ""

    # TODO: Some settings that should be moved elsewhere
    tmpl_pat = 'template-{}.jn2{}'
    init_context_pat  = 'initial-context-{}.yaml'
    final_context_pat  = 'final-context-{}.yaml'
    result_pat   = 'result-{}{}'

    # write out the base template
    if debug_dir != None:
        dump_str(template_str,path=(debug_dir,tmpl_pat.format(name,out_ext)))

    # generate new context
    initial_ctxt = deepcopy(ctxt | spec.context)

    # and print it out
    if debug_dir != None:
        dump_yaml(initial_ctxt,path=(debug_dir,init_context_pat.format(name)))

    final_ctxt = deepcopy(initial_ctxt)

    # run through all subtemplates and build them too
    for (subname, subtemp) in spec.subtemplates.items():

        # log.warning((name, subname, type(subtemp)))

        final_ctxt[subname] = build_subtemplates(
            spec, name, subtemp, subname, initial_ctxt, debug_dir)


    # dump the context post subtemplating
    if debug_dir != None:
        dump_yaml(final_ctxt, path=(debug_dir,final_context_pat.format(name)))

    # actually render the template
    result = template.render(**final_ctxt)

    # dump the result of this template as a debug entry
    if debug_dir != None:
        dump_str(result, path=(debug_dir,result_pat.format(name, out_ext)))

    return_val = {k:v for (k,v) in final_ctxt.items() if k not in ctxt or
                  ctxt[k] != final_ctxt[k]}
    return_val['text'] = result

    # print the out_put
    if out_path != None:
        dump_str(result, path=out_path)
        return_val['file'] = out_path

    if spec.post_render_hook != None:
        spec.post_render_hook(return_val)

    return return_val


def build_subtemplates(spec, name, sub, subname, ctxt, debug):
    """
    Properly handle lists and dicts of subtemplates, allowing for better
    management of subquestions. Esp. not requiring templates to know what
    all the various sub-questions are called.
    """

    entries = None
    output = None

    if isinstance(sub, list):
        entries = list(enumerate(sub))
        output = [None] * len(entries)
    elif isinstance(sub, dict):
        entries = sub.items()
        output = dict()
    else:

        new_name = "{}-{}".format(name, subname)

        sub.path = spec.path + sub.path
        if sub.format_dir == None:
            sub.format_dir = spec.format_dir
        if sub.format_ext == None:
            sub.format_ext = spec.format_ext

        # make a new outfile for the subtemplate if none exists
        if spec.out_file != None and sub.out_file == None:
            pat = Path(spec.out_file)
            ext = "".join(pat.suffixes)
            suff = "." + sub.format_ext if sub.format_ext else ext
            pat = pat.with_stem(new_name).with_suffix(suff)
            sub.out_file = pat

        return build_template_spec(name=new_name,
                                   spec=sub,
                                   ctxt=ctxt,
                                   debug_dir=debug)

    for (keyname, subspec) in entries:
        # log.warning((keyname, subspec))
        output[keyname] = build_subtemplates(
            spec = spec,
            name = name,
            sub = subspec,
            subname = "{}[{}]".format(subname, keyname),
            ctxt = ctxt,
            debug = debug)
    return output

@attr.s
class TemplateSpec():
    """
    A specification for how to build a template.
    """

    template = attr.ib()
    context = attr.ib(factory=dict, kw_only=True)

    subtemplates = attr.ib(factory=dict, kw_only=True)

    path = attr.ib(factory=list, kw_only=True)
    format_dir = attr.ib(default=None, kw_only=True)
    format_ext = attr.ib(default=None, kw_only=True)

    out_file = attr.ib(default=None, init=False)

    jinja_opts = attr.ib(factory=dict, init=False)

    post_render_hook = attr.ib(default=None, kw_only=True)

def template_spec_from_var(var, versions=[], empty_okay=False):
    """
    Create a TemplateSpec from a template var (a `VersionedOpts` with the
    fields `text`, `file`, and `ctxt`)

    Treats `text` as higher priority than `file`
    """

    # Get the version of the spec we need for this task
    for v in versions:
        var = var[v]

    # get requisite template type
    template = None
    if var.text != None:
        template = var.text
        if var.file != None:
            log.warning(("Both `file` and `text` parameters are set "
                         "for template '{}'. `text` is being used by "
                         "default.").format(var.var_name))
    elif var.file != None:
        template = Path(var.file)
    elif empty_okay:
        template = ""
    else:
        raise RuntimeError(("Template Var {} has neither `text` nor `file` "
                            "parameter specified.").format(var.var_name))

    # log.warning(pformat((var.var_name, var.ctxt)))

    return TemplateSpec(template,
                        context=var.ctxt)





__jinja_default_opts__ = dict(
    block_start_string = '{%',
    block_end_string = '%}',
    variable_start_string = '{{',
    variable_end_string = '}}',
    comment_start_string = '{#',
    comment_end_string = '#}',
    trim_blocks = True, # !! Not Jinja default
    lstrip_blocks = False, # basically `textwrap.dedent`
    newline_sequence = '\n',
    keep_trailing_newline = False,
    optimized = True,
    autoescape = False, # !! Not Jinja Default
)


def exam_format_key_func(self, key, format_list=[]):
    if key in format_list:
        return key
    else:
        raise RuntimeError("{} is not a valid exam format.".format(key))

__template_versioned_opts__ = {
    'text':{'default':None},
    'file':{'default':None},
    'ctxt':{'factory':dict}
}

def add_template_var(
        name,
        format_list=[],
        doc=None):

    key_func = functools.partial(exam_format_key_func, format_list=format_list)

    return add_versioned_option(
        name = name,
        option_spec = __template_versioned_opts__,
        doc = doc,
        format_spec = [{'key_func':key_func}]
        )
