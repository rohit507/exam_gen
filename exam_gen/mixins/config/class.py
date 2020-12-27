import exam_gen.util.logging as logging
from exam_gen.util.attrs_wrapper import attrs
from exam_gen.mixins.config.value import ConfigValue
from exam_gen.mixins.config.group import ConfigGroup
from exam_gen.mixins.config.format import ConfigDocFormat, default_format

log = logging.new(__name__, level="DEBUG")

def new_config_superclass(
        class_name,
        var_name,
        docstring = "",
        var_docstring = "",
        doc_style = default_format,
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

    def prepare_attrs(cls, name, bases, env):
        if hasattr(super(cls), "__prepare_attrs__"):
            env = super(cls).__prepare_attrs__(name, bases, env)

        class_config = ConfigGroup(doc = var_doc, ctxt = cls, path = [var_name])
        if var_name in env:
            log.debug(prepare_attrs_debug_msg(
                "Updating config for {name} with data from prepare_attrs of {supr}.",
                name, cls, bases, class_config, env[var_name]))

            class_config.update(env[var_name])


        superclass_config = getattr(cls, __var_name, None)
        if superclass_config != None:
            log.debug(prepare_attrs_debug_msg(
                "Updating config for {name} with post-init data from {cls}.",
                name, cls, bases, class_config, superclass_config))
            class_config.update(superclass_config)

        env[var_name] = class_config

        return env

    def init_subclass(cls, **kwargs):

        log.debug("Running init class for {class_name} on class {cls}",
                  class_name=class_name, cls=cls)

        super(config_classes[class_name], cls).__init_subclass__(**kwargs)

        class_config = getattr(cls, var_name, None)
        if class_config == None:
            assert False, "Internal Error: w/ config class gen."
        class_config = class_config.clone(ctxt=cls)
        setattr(cls, __var_name, class_config)
        docstring = ConfigDocFormat.render_docs(
            attr.evolve(
                doc_style,
                doc = var_docstring,
                **kwargs),
            class_config)

        def property_getter(self):
            return getattr(self,__var_name)

        property_getter.__doc__ = docstring

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
        namespace["__init__"] = init
        namespace["__doc__"] = class_doc

        return namespace

    return types.new_class(
        class_name,
        (),
        {'metaclass':PrepareAttrs},
        exec_body = populate_class_namespace,
    )

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
            us.value_dict(),
            indent = 8),
        their_path_string = them.path_string(),
        their_ctxt = them.ctxt,
        their_value = pformat(
            them.value_dict(),
            indent=8),
        supr=super(cls)
        )

    template = """
        During PrepareAttrs of {name} with {cls}:
        {msg}

          {name} Data:
            Bases: {bases}
            Path: {our_path_string}
            Context: {our_ctxt}
            Data: {our_values}

          {cls} Data:
            Path: {their_path_string}
            Context: {their_ctxt}
            Data: {their_values}
        """

    return textwrap.dedent(template).format(
        msg=msg.format(properties),
        **properties,
    )
