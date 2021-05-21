import yaml

from pathlib import *

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

__all__ = ["dump_str","dump_as_yaml"]

def _format_path(path):
    if isinstance(path, Iterable):
        return Path(*path)
    else:
        return Path(path)

def dump_str(data, *, path):
    file_handle = _format_path(path).open(mode='w')
    file_handle.write(data)
    file_handle.close()

def dump_as_yaml(data, *, path):
    file_handle = _format_path(path).open(mode='w')
    file_handle.write(yaml.dump(data))
    file_handle.close()
