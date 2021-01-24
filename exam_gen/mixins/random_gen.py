from copy import copy, deepcopy
from pprint import pformat, pprint
from textwrap import dedent, indent
from collections import Iterable

import makefun
import inspect

import attr
import attr.validators as valid

import exam_gen.util.logging as logging

log = logging.new(__name__, level="WARNING")

"""
Ok, so this is a random number generator that will descend through the
various sub-elements of a document when seeded and provide seeded generators
for different tasks.

I guess that for the moment we should just have a class that does the sub-seed
creation and a separate one that manages pushing the RNGs down from the root.

Since the latter needs some sort of knowledge of the tree structure of a doc.
"""
