import exam_gen.util.logging as logging
import textwrap
import types
import attr
from pprint import *
from exam_gen.util.attrs_wrapper import attrs
from exam_gen.mixins.prepare_attrs import PrepareAttrs
from exam_gen.mixins.config.value import ConfigValue
from exam_gen.mixins.config.group import ConfigGroup
from exam_gen.mixins.config.format import ConfigDocFormat, default_format

log = logging.new(__name__, level="DEBUG")

config_classes = dict()

def new_config_superclass(
        class_name,
        var_name,
        docstring = "",
        var_docstring = "",
        doc_style = default_format,
        bases = (),
        **kwargs
        ):
    """
    Generates a new superclass with a special configuration variable that
    subclasses can add to, and which is automatically documented properly.

    Parameters:

       class_name (str): The name of class to be generated.

       var_name (str): The name of the class's configuration variable.

       docstring (str): The dostring for the parent class. Will only appear
          when looking directly for the generated superclass.

       var_docstring (str): The docstring for the configuration variable. Will
          be visible in the collected docs for every subclass.

       doc_style (ConfigDocFormat): The documentation style object to use when
          generating the variable documentation for this class.

       **kwargs: Extra parameters that are passed to documentation style. Taken
          from `#!py exam_gen.mixins.config.format.ConfigDocFormat` so look
          there for specific flags you can set.
    """

    __var_name = "__" + var_name

    class_docstring = textwrap.dedent(docstring)

    def prepare_attrs(cls, name, bases, env):
        if hasattr(super(cls), "__prepare_attrs__"):
            env = super(cls).__prepare_attrs__(name, bases, env)

        class_config = ConfigGroup(doc = var_docstring, ctxt = cls, path = [var_name])
        if var_name in env:
            log.debug(prepare_attrs_debug_msg(
                "Updating config for %(name)s with data from prepare_attrs of %(supr).",
                name, cls, bases, class_config, env[var_name]))

            class_config.update(env[var_name])


        superclass_config = getattr(cls, __var_name, None)
        if superclass_config != None:
            log.debug(prepare_attrs_debug_msg(
                "Updating config for %(name) with post-init data from %(cls).",
                name, cls, bases, class_config, superclass_config))
            class_config.update(superclass_config)

        env[var_name] = class_config

        return env

    def init_subclass(cls, **kwargs):

        log.debug("Running init class for %s on class %s",
                  class_name, cls)

        super(config_classes[class_name], cls).__init_subclass__(**kwargs)

        if cls == config_classes[class_name]:
            cls.__doc__ = class_docstring

        class_config = getattr(cls, var_name, None)
        if class_config == None:
            assert False, "Internal Error: w/ config class gen."
        class_config = class_config.clone(ctxt=cls)
        setattr(cls, __var_name, class_config)
        v_docstring = ConfigDocFormat.render_docs(
            attr.evolve(
                doc_style,
                doc = textwrap.dedent(var_docstring),
                **kwargs),
            class_config)

        def property_getter(self):
            return getattr(self,__var_name)

        property_getter.__doc__ = v_docstring

        def property_setter(self, value):
            setattr(self, __var_name, value)

        property_class = type(
            "_{}_ConfigProperty".format(class_name),
            (type(property()),),
            { '__getattr__': class_config.__getattr__,
              '__setattr__': class_config.__setattr__,
            })

        setattr(cls, var_name, property_class(property_getter, property_setter))

    def new(cls, *vargs, **kwargs):
        inst = super(
            cls,
            self
        ).__new__(self, *vargs, **kwargs)

        class_config = getattr(inst, __var_name, None)
        if class_config == None:
            assert False, "Internal Error: w/ config class gen."
        instance_config = class_config.clone(ctxt=inst)
        setattr(inst, __var_name, instance_config)
        return inst

    def populate_class_namespace(namespace):
        namespace["__prepare_attrs__"] = classmethod(prepare_attrs)
        namespace["__init_subclass__"] = classmethod(init_subclass)
        namespace["__new__"] = new
        namespace["__doc__"] = textwrap.dedent(docstring)

        return namespace

    config_classes[class_name] = types.new_class(
        class_name,
        bases,
        {'metaclass':PrepareAttrs},
        exec_body = populate_class_namespace,
    )


    return config_classes[class_name]

def prepare_attrs_debug_msg(msg, name, cls, bases, us, them):
    """
    Generate an overly verbose debug message during class initialization.
    Mainly to help debug inheritance.
    """
    properties = dict(
        name = name,
        cls = cls.__qualname__,
        bases = bases,
        our_ctxt = us.ctxt,
        our_path_string = us.path_string(),
        our_values = pformat(
            us.value_dict,
            indent = 8),
        their_path_string = them.path_string(),
        their_ctxt = them.ctxt,
        their_value = pformat(
            them.value_dict,
            indent=8),
        supr=super(cls)
        )

    template = """
        During PrepareAttrs of %(name)s with %(cls):
        %(msg)s

          %(name)s Data:
            Bases: %(bases)s
            Path: %(our_path_string)s
            Context: %(our_ctxt)s
            Data: %(our_values)s

          %(cls)s Data:
            Path: %(their_path_string)s
            Context: %(their_ctxt)s
            Data: %(their_values)s
        """

    return textwrap.dedent(template).format(
        msg=msg.format(properties),
        **properties,
    )
