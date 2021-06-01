import attr
import os
import subprocess
import shutil

from pprint import *
from pathlib import *

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

    settings.build.new_value(
        'latex_command', default='pdflatex', doc=
        """
        The actual command line application that will be used to build the
        document. `'xelatex'` and `'lualatex'` are some other possible options.
        """)

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

        build_cmd = subprocess.run([self.settings.build.latex_command,
                                    tex_file])

        log_ = {'tex_file': tex_file,
               'pdf_file': pdf_file,
               'build_info': build_info,
               'latex_command': self.settings.build.latex_command}

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
