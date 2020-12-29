# exam_gen.mixins.config

!!! Todo "Feature Todo List"
    **ConfigValue:**

      - Add some way to set the types of config value
      - Maybe add some way to dynamically set options or sub-tables to values
        that can be extended as needed.

    **ConfigGroup:**

      - Add some way to validate values and initialize values based on
        other settings.
      - Add checks and errors for when new subgroups and values are overwriting
        existing ones.

    **ConfigDocFormat:**

      - Add a way to hide specific values and subgroups from documentation
        output.
      - Don't override the docstring for config groups that are empty but have
        a docstring.

    **config_superclass:**

      - Split out into two functions, one which uses prepare_attr to create
        an arbitrary namepace variable and another which is specifically for
        creating a config superclass.
          - Move the former to the `prepare_attrs` module.
          - Fix the inheritance stuff where needed to make this work.

::: exam_gen.mixins.config
    handler: python
    selection:
      filters:
         - "!__"
    rendering:
      heading_level: 2
      show_source: True
      show_root_toc_entry: False
      show_object_full_path: True
