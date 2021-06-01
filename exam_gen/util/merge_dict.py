from copy import *

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

def merge_dicts(base, *others):

    output = copy(base)

    for other in others:
        if other != None:
            for (key, val) in other.items():
                if key not in output:
                    output[key] = val
                elif isinstance(output[key], dict) and isinstance(val,dict):
                    output[key] = merge_dicts(output[key], val)
                elif isinstance(output[key], dict):
                    raise RuntimeError("Attempting to overwrite dict in "
                                   "recursive dict merge.")
                else:
                    output[key] = val

    return output
