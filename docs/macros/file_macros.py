import os
import textwrap
import re
from pathlib import *

def _include_file(env, filename, start_line=0, end_line=None, relative=True, dedent=False):
    """
    Include a file, optionally indicating start_line and end_line
    (start counting from 0)
    The path is relative to the top directory of the documentation
    project.
    """

    base = Path(env.project_dir, "docs")

    if relative:
        base = Path(base, env.page.url).parent

    file_obj = Path(base,filename)

    if not file_obj.exists():
        raise RuntimeError(f'No File Found At: #{file_obj.as_posix()}')

    with file_obj.open('r') as f:
        lines = f.readlines()
    line_range = lines[start_line:end_line]

    text = ''.join(line_range)

    return textwrap.dedent(text) if dedent else text

def _include_block(
        env,
        filename,
        start_line=0,
        end_line=None,
        relative=True,
        dedent=True,
        lines=True,
        hl_lines=False,
        lang="python"):
    """
    Include a block from a file w/ appropriate escaping and indentation.
    """

    header = r'```'
    if lang:
        header += lang

    if lines:
        header += f' linenums="{start_line + 1}"'

    if lines and hl_lines:
        elems = re.findall(r'\d+|\D+', hl_lines)
        hl_lines = ''.join([str(int(s) - start_line) if s.isdigit() else s for s in elems])
        header += f' hl_lines="{hl_lines}"'

    header += r''

    footer = r'```'

    content = _include_file(env, filename, start_line, end_line, relative, dedent)

    return '\n'.join([header, content, footer])

# def _include_download_file(
#         env,
#         filename,
#         disp_filename=None,
#         abs_url=None,
#         relative=True,
#         **kwargs
#         ):

#     filename = Path(filename)
#     if not disp_filename: display_filename = filename.name

#     if not abs_url:
#         base = Path("")
#         if relative:
#             base = Path(env.page.url).parent
#         abs_url = env.config.site_url + Path(base , filename).as_posix()
