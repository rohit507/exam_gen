import exam_gen.mixins.config.format as fmt
import exam_gen.mixins.config.superclass as cls

default_format = fmt.default_format
DocFormat = fmt.ConfigDocFormat
new_superclass = cls.new_config_superclass

__all__ = ['default_format', 'DocFormat', 'new_superclass']
