import attr
import os
import subprocess
import shutil
import textwrap

from pprint import *
from pathlib import *
from collections import Iterable

from ..document import Document
from ..buildable import Buildable
from ..templated import Templated, build_template_spec

from exam_gen.util.file_ops import dump_str, dump_yaml

import exam_gen.util.logging as logging

import os

log = logging.new(__name__, level="DEBUG")

class LatexDoc(Buildable, Templated):
    """
    Specializes the document type for latex
    """

    settings.template.format_dir = "latex"

    settings.template.format_ext = "tex"

    settings.new_group(
        name="latex",
        doc="""
        Settings specific to LaTeX output.
        """)

    settings.latex.new_value(
        'command', default='pdflatex', doc=
        """
        The actual command line application that will be used to build the
        document. `'xelatex'` and `'lualatex'` are some other possible options.
        """)

    settings.latex.new_value(
        name='header_includes',
        default=None,
        doc = """
        The extra LaTeX code to be included in the header of the output
        document. Can either be a single string or a list of strings to be
        included in the output document.

        !!! error "Todo: more specific examples"
        """
        )

    def get_header_includes(self):
        """
        Retrieves the list of all header includes for each child and self.
        """

        includes = list()
        self_includes = self.settings.latex.header_includes

        if isinstance(self_includes, str):
            includes.append(textwrap.dedent(self_includes))
        elif isinstance(self_includes, Iterable):
            for inc in self_includes:
                if isinstance(inc, str):
                    includes.append(textwrap.dedent(inc))
                else:
                    raise RuntimeError("Invalid entry for header includes")
        elif self_includes == None:
            pass
        else:
            raise RuntimeError("Invalid entry for header includes")

        for (q,v) in self.questions.items():
            includes += v.get_header_includes()

        return list(dict.fromkeys(includes))

    def build_template_spec(self, build_info):

        spec = super(LatexDoc, self).build_template_spec(build_info)

        spec.context['header_includes'] = self.get_header_includes()

        return spec

    def finalize_build(self, build_info):

        if Path(os.getcwd()) != build_info.build_path:
            raise RuntimeError("LatexDoc Builds must be run in build dir")

        file_stem = self.settings.template.output
        tex_file = Path(file_stem + '.' + self.settings.template.format_ext)
        pdf_file = tex_file.with_suffix('.pdf')

        # template_spec = self.template_spec(
        #     out_file = self.settings.build.tex_file,
        #     **build_settings)

        # results = build_template_spec(
        #     file_stem, template_spec, dict(), tex_file, data_dir)

        build_cmd = subprocess.run([self.settings.latex.command,
                                    tex_file])

        log_ = {'tex_file': tex_file,
               'pdf_file': pdf_file,
               'build_info': build_info,
               'latex_command': self.settings.latex.command}

        try:
            build_cmd.check_returncode()

        except err:
            log_name = "finalize-error-{}.yaml".format(file_stem)

            dump_yaml(log_, path=(data_dir, log_name))

            raise err

        return log_

    def output_build(self, build_info, output_file=None):

        if output_file == None:
            output_file = self.settings.template.output

        output_file = Path(build_info.out_path, output_file).with_suffix('.pdf')

        pdf_file = Path(build_info.build_path,
                        self.settings.template.output).with_suffix('.pdf')

        shutil.copyfile(pdf_file, output_file)

        return {'output_file': output_file,
                'pdf_file': pdf_file,
                'build_info': build_info}
