from pyyaml import yaml

class Yamlable():

    yaml_tag = None

    @classmethod
    def from_yaml(cls, loader, node):
        return data

    @classmethod
    def to_yaml(cls, dumper, data):
        return node

    def __init_subclass__(cls):
        # Set yaml tag
        # register constructor
        # register representer
