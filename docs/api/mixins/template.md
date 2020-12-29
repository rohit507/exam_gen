# exam_gen.mixins.template

Goal is to provide basic flow to using jinja templates w/ good error messages
for the assorted users.

  - Setting:
      - Template File
  - Add variables:
      - For rendering template
  - Render template in various formats
      - Things like: DEFAULT, SOLUTIONS, ANSWERED, GRADED, etc...
      - Capture large scale

Yeah ok, can't do anything clever with blocks really. Need to pass context
down and pass rendered content up.

I'm pretty sure this needs the changes to prepare_attrs to works well.

## Generated Documentation
::: exam_gen.mixins.template
    handler: python
    selection:
      filters:
         - "!__"
    rendering:
      heading_level: 2
      show_source: True
      show_root_toc_entry: False
      show_object_full_path: True
