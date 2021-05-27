import yaml
import shutil
import jsonpickle.pickler as json_p
import jsonpickle.unpickler as json_u
import collections

from pathlib import *

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

__all__ = ["dump_str",
           "dump_yaml",
           "dump_obj",
           "delete_folders"]

def _format_path(path):
    if isinstance(path, collections.Iterable):
        return Path(*path)
    else:
        return Path(path)

def dump_str(data, *, path):
    path = _format_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    file_handle = path.open(mode='w')
    file_handle.write(data)
    file_handle.close()

def dump_yaml(data, *, path):
    dump_str(yaml.dump(data), path=path)

def dump_obj(data, *, path):
    obj = json_p.Pickler(keys=True, warn=True).flatten(data)
    dump_yaml(obj, path=path)

def delete_folders(*paths):
    for path in paths:
        shutil.rmtree(path, ignore_errors=True)
