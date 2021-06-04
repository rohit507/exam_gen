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

## yaml diff model

 - Data Structure for a yaml like representation of a term.
 - Contruction of a term from a ..

nvm, the hard part of this is the chaining and stuff.

## General Build process model

Ok, so I want to have a flow as follows:

 - `<class>/config.py` : Config File
    - determines class specific information like roster and grades file and
      formatting touch
 - `<class>/<roster_file>` : Roster(s)
 - `<class>/<grades>` : Raw grades files
 - `<class>/<build>/roster.yaml` : parsed roster
 - `<class>/<build>/grades.yaml` : parsed grades
 - `<class>/<build>/<student>/` : student specific build information
    - symlinks to assets and templates
    - various `.yaml` files with problem data and exam data
    - generated support files
    - generated build files
 - `<class>/<build>/<other_target>` : build information for other target files
 - `<class>/<output>/` : result files for various targets


And base items as follows:

 - `<templates>/<template_files>`
 - `<assets>/<asset_files>`
