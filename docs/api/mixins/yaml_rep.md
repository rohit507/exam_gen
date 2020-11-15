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
