import hashlib

import exam_gen.util.logging as logging

log = logging.new(__name__, level="WARNING")

__all__ = ["stable_hash"]

def stable_hash(*vargs):
    """
    Creates a stable, readable(ish) hash of a set of input parameters.
    Arguments can be strings, bytes objects, integers, or iterables containing
    any of the former.

    Argument Types:

      - str: left as is
      - int: rendered as hexadecimal str
      - bytes: turned into a hex string
      - iterables: turned into single string w/ recursive call
      - other: error

    result:

      (str): all normalized args are concatenated, hashed, and the lowest 32
      bits of the result are returned as a hexadecimal string.
    """

    hasher = hashlib.shake_128()

    def run_hasher(v):
        if isinstance(v, str):
            hasher.update(bytes(v,'utf-8'))
        elif isinstance(v, bytes):
            hasher.update(v)
            pass
        elif isinstance(b, Iterable):
            for elem in v: run_hasher(elem)
        else:
            hasher.update(bytes(str(v),'utf-8'))

    for arg in vargs: run_hasher(arg)

    return hasher.digest(4).hex()
