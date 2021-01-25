from copy import copy, deepcopy
from pprint import pformat, pprint
from textwrap import dedent, indent
from collections import Iterable

import makefun
import inspect

import attr
import attr.validators as valid

import exam_gen.util.logging as logging
import exam_gen.mixins.user_setup.superclass as user_setup

log = logging.new(__name__, level="WARNING")

"""
Ok, so this is a random number generator that will descend through the
various sub-elements of a document when seeded and provide seeded generators
for different tasks.

I guess that for the moment we should just have a class that does the sub-seed
creation and a separate one that manages pushing the RNGs down from the root.

Since the latter needs some sort of knowledge of the tree structure of a doc.

Basically any class inheriting from this can:

  - Accept a Seed. (a 16 bit int as a hex string should be fine)
    - Hashlib.shake
  - Create new RNGs from the hash of the seed and another key.
  - If there's a user_setup, then this will register a new input variable and
    provide that key where appropriate.

  - Create a log of RNG seeds as a tree structure
     - If there's a tree of seeds provided, use that over the one that's
       generated.

Something something stability?
"""

def create_seed(*vargs):
    """
    Create a new seed value from one or more entries in a random way.
    Does some formatting to normalise the parameters before generating a
    result.

    normalization:

      - str: left as is
      - int: rendered as hexadecimal str
      - bytes: turned into a hex string
      - iterables: turned into single string w/ recursive call
      - other: error

    result:

      (str): all normalized args are concatenated, hashed, and the lowest 32
      bits of the result are returned as a hexadecimal string
    """
    pass

def create_gen(seed):
    """
    Creates a new rng from a seed string
    """
    pass

@attr.s
class SeedEntry():
    """
    An entry of just the stored static information on the seeds for a
    particular seeded rng.
    """

    _root_seed = attr.ib()
    _key_string = attr.ib()

    _key_seed = attr.ib(default=None)
    _indexed_seeds = attr.ib(factory=list)

    def to_seed_tuple(self):
        return (self._key_seed, self._indexed_seeds)

    @classmethod
    def from_seed_tuple(cls, root_seed, key, seed_tuple):
        (key_seed, indexed_seeds) = seed_tuple
        return cls(
            root_seed = root_seed,
            key = key,
            key_seed = key_seed,
            indexed_seeds = indexed_seeds,
        )

    @property
    def key_seed(self):
        if self._key_seed == None:
            self._key_seed = create_seed(self._root_seed, self._key_string)

        return self._key_seed

@attr.s
class StateEntry(SeedEntry):
    """
    Captures the current runtime state for a RNGSource including any
    previously generated keys that were imported from somewhere.
    """

    _rng = attr.ib(init=False, default=None)
    _index = attr.ib(init=False, default=0)
    _indexed_generators = attr.ib(init=False, factory=dict)


    @property
    def rng(self):
        if self._rng == None:
            self._rng = create_rng(self.key_seed)

        return self.rng

    def indexed_seed(self, index):

        seed = None

        # Out of bounds
        if index > self._index:
            raise RuntimeError("Requested RNG index too high")

        # Increment the rng and (maybe) create a new seed to use
        if index == self._index:
            seed = create_seed(self.rng.randbytes(4))
            self._index += 1

        # Override with preexisting seed
        if index < len(self._indexed_seeds):
            seed = self._indexed_seeds[index]

        # Extend the list if needs be
        if index == len(self._indexed_seeds):
            self._indexed_seeds.append(seed)
        else:
            self._indexed_seeds[index] = seed

        return seed

    def indexed_gen(self, index):

        if index in self._indexed_generators:
            return self._indexed_generators[index]
        else:
            seed = self.indexed_seed(index)
            rng = create_rng(seed)
            self._indexed_generators[index] = rng
            return rng

    def next_seed(self):
        return self.indexed_seed(self._index)

    def next_rng(self):
        return self.indexed_gen(self._index)




@attr.s
class RNGSource():

    _root_seed = attr.ib(
        default = None,
    )
    """
    The seed from which we derive all the other seeds for this source
    """

    _seed_tree = attr.ib(
        default = None,
        repr = False,
    )
    """
    A 'tree' of generated seeds we use to initialize assorted RNGs that will
    be used in various places
    """

    _key_tree = attr.ib(
        init = None,
        default = None,
    )
    """
    The state of our random system, generally the current index for a given
    key into our state tree, the random number generator that's used to produce
    the next seed, and the random number generator that's been created for
    each new key.
    """

    @property
    def key_tree(self):

        if self._root_seed == None:
            raise RuntimeError(
                "Must set a root seed for RNGSource before requesting rng.")

        if self._key_tree == None:
            k_tree = dict()

            if self._seed_tree != None:
                for (k,v) in self._seed_tree:
                    k_tree[k] = StateEntry.from_seed_tuple(
                        self.root_seed, k, v)

            self._key_tree = k_tree

        return self._key_tree

    @property
    def seed_tree(self):
        s_tree = dict()

        for (k,v) in self._key_tree:
            s_tree[k] = v.to_seed_tuple()

        return s_tree

    @seed_tree.setter
    def seed_tree(self, s_tree):
        if self._seed_tree != None:
            raise RuntimeError(
                "Can only set seed tree for an RNG source once.")

        if self._key_tree != None:
            raise RuntimeError(
                "Cannot set seed tree after requesting generator.")

        self._seed_tree = s_tree

    @property
    def root_seed(self):
        if self._root_seed == None:
            raise RuntimeError("Have not initialized RNG for this item")

        return self._root_seed

    def new_keyed_rng(self, key):
        if key not in self.key_tree:
            self.key_tree[key] = StateEntry(self.root_seed, key)

        return self.key_tree[key].next_rng()
