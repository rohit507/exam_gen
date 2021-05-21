import attr
from pathlib import *
from jinja2 import *
from copy import *
import yaml
import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class TemplateManager():

    template_path = attr.ib(factory=list, kw_only=True)
    base_loader = attr.ib(kw_only=True)

    @base_loader.default
    def _init_base_loader(self):
        return PackageLoader("exam_gen")

    jinja_opts = attr.ib(factory=dict, kw_only=True)

    environment = attr.ib(kw_only = True)

    @environment.default
    def _init_env(self):
        return Environment(__environment_default_opts__ | self.jinja_opts)

    template_loader = attr.ib(kw_only = True)

    @template_loader.default
    def _init_loader(self):
        return ChoiceLoader([
            FileSystemLoader(self.template_path),
            self.base_loader
        ])

    debug_template_pat = attr.ib(default='template-{}.jn2{}', kw_only=True)
    debug_context_pat  = attr.ib(default='context-{}.yaml', kw_only=True)
    debug_result_pat   = attr.ib(default='result-{}{}',     kw_only=True)

    def build_template(self,
                       name,
                       context,
                       debug_dir,
                       out_path,
                       loader=None,
                       environment=None,
                       file=None,
                       text=None
                       ):

        if (file == None) and (text == None):
            raise RuntimeError("build_template needs either file or text "
                               "parameter")

        if (file != None) and (text != None):
            raise RumtimeError("build_parameter cannot have both file and "
                               "text parameters specified.")

        loader = loader or self.template_loader
        environment = environment or self.environment

        template = None

        if (file != None):
            (text,_,_) = loader.get_source(self.environment,file)
            template = loader.load(self.environment, file)
        else:
            template = environment.from_string(text)

        assert (text != None), "Should have hit all other cases by here"

        out_ext = "".join(Path(out_file).suffixes)

        debug_template_path = Path(
            debug_dir,
            self.debug_template_pat.format(name, out_ext))
        debug_template_file = debug_template_path.open(mode='w')
        debug_template_file.write(text)
        debug_template_file.close()

        debug_context_path = Path(
            debug_dir,
            self.debug_context_pat.format(name))
        debug_context_file = debug_context_path.open(mode='w')
        debug_context_file.write(yaml.dump(context))
        debug_context_file.close()

        result = template.render(**context)

        debug_result_path = Path(
            debug_dir,
            self.debug_result_pat.format(name, out_ext))
        debug_result_file = debug_result_path.open(mode='w')
        debug_result_file.write(result)
        debug_result_file.close()

        out_file = Path(out_path).open(mode='w')
        out_file.write(result)
        out_file.close()

        return {'text': result,
                'file': out_file }

    def build_template_dict(
            name,
            param_dict,
            debug_dir : Path = None,
            out_path : Path = None):
        """
        Uses a parameter dictionary to recursively build some templates.

        Param_dict Fields:
           'file': template file
           'text': template text
           'context' : template variables
           'subtemplates' : map from name to param_dict for subtemplate.
           'loader' & 'environment': apply to all subdicts as well.

        other fields match build_template function params
        """

        context = deepcopy(param_dict['context'])

        loader = param_dict.get('loader', None)
        environment = param_dict.get('environment', None)

        if 'subtemplates' in param_dict:
            for (subname, subparams) in param_dict['subtemplates'].items():

                # Want to have variables from parents apply in sub-elements
                sub_ctxt = param_dict['context']
                if 'context' in subparams:
                    sub_ctxt = new_ctxt | subparams['context']
                sub_ctxt = deepcopy(sub_ctxt)

                params = deepcopy(subparams)
                params['context'] = sub_ctxt

                # set if does not exist
                params.setdefault('loader', loader)
                params.setdefault('environment', environment)

                context[subname] = deepcopy(self.build_template_dict(
                    "{}-{}".format(name, subname),
                    param_dict=params,
                    debug_dir=debug_dir,
                    out_path=out_path
                ))

        return self.build_template(
            name = name,
            context = deepcopy(context),
            debug_dir = debug_dir,
            out_path = out_path,
            file = param_dict.get('file', None),
            text = param_dict.get('text', None),
            loader = loader,
            environment = environment
        )


__environment_default_opts__ = dict(
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

# helps lookup templates for use
# write intermediate/debug template data to file
# prints output template data to file
#
