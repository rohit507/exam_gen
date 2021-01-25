import attr
import attr.validators as valid


@attr.s
class File:
    """
    A simple wrapper around a string to denote that it's a file name and
    meant to be used as such.
    """
    name = attr.ib(validator = valid.instance_of(str))
