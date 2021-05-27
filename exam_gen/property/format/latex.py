import attr
import os
import subprocess
import shutil

from pathlib import *

from ..document import Document
from ..buildable import Buildable
from ..templated import Templated, build_template_spec

from exam_gen.util.file_ops import dump_str, dump_yaml

import exam_gen.util.logging as logging

import os

log = logging.new(__name__, level="DEBUG")

class LatexDoc(Templated, Buildable):
    """
    Specializes the document type for latex
    """

    settings.template.format_dir = "latex"

    settings.template.format_ext = "tex"

    settings.build.new_value(
        'latex_command', default='pdftex', doc=
        """
        The actual command line application that will be used to build the
        document. `'xetex'` and `'luatex'` are some other possible options.
        """)

    settings.build.new_value(
        'tex_file', default='document.tex', doc=
        """
        The file which the generated latex file will be written to.
        The resulting PDF file will use the same name with the '.pdf'
        extension.
        """)

    def finalize_build(self, data_dir, build_dir, **build_settings):

        if os.getcwd() != build_dir:
            raise RuntimeError("LatexDoc Builds must be run in build dir")

        tex_file = Path(self.settings.build.tex_file)
        file_stem = tex_file.stem
        pdf_file = tex_file.with_suffix('.pdf')

        template_spec = self.template_spec(
            out_file = self.settings.build.tex_file,
            **build_settings)

        results = build_template_spec(
            file_stem, template_spec, dict(), tex_file, data_dir)

        build_cmd = subprocess.run([self.settings.build.latex_command,
                                    tex_file], capture_output=True)

        log = {'tex_file': tex_file,
               'pdf_file': pdf_file,
               'build_cmd': build_cmd,
               'data_dir': data_dir,
               'build_dir': build_dir,
               'cwd': os.getcwd(),
               'build_settings': build_settings,
               'latex_command': self.settings.build.latex_command}

        try:
            build_cmd.check_returncode()

        except err:
            log_name = "finalize-error-{}.yaml".format(file_stem)

            dump_yaml(log, path=(data_dir, log_name))

            raise err

        return log

    def output_build(self, data_dir, build_dir, out_dir,
                     output_file=None,
                     **build_settings):

        if output_file == None:
            output_file = Path(self.settings.build.tex_file).with_suffix('.pdf')

        output_file = Path(out_dir, output_file)

        pdf_file = Path(build_dir,
                        self.settings.build.tex_file).with_suffix('.pdf')

        shutil.copyfile(pdf_file, output_file)

        return {'data_dir': data_dir,
                'build_dir': build_dir,
                'out_dir': out_dir,
                'output_file': output_file,
                'pdf_file': pdf_file,
                'build_settings': build_settings}
