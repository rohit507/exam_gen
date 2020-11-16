# Yaml Representation

We want to be able to dump and load all the different classes to a human
readable representation. Both for backups and debugging.

Requirements:

  - Somewhat sane method for making a class representable.
  - Some way to skip around the usual init process and load a file without
    recapitulating any side effects.
  - Some way to skip writing values that are unchanged from their defaults
    pre-`__init__`.
  - Some way to skip writing values that are deterministically derived from
    values that we do manage.
  - Some way to dump/load large strings to a separate file rather than
    keep them inline.

So yeah:

  - How do I do construction of the yaml node in a class hierarchy compliant
    way?
  - How can I allow for the splitting of source files in a reasonable way?

Hmm, I think the reasonable thing to do for now is to just leave this be as
something on the todo list. It's important but it's neither on the critical
path nor something that would be hurt by introduction later.

## Generated Documentation

::: exam_gen.mixins.yaml_rep
    handler: python
    rendering:
      heading_level: 3
      show_source: false
      show_root_toc_entry: false
