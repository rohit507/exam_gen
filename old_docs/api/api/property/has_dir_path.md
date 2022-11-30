# `exam_gen.property.has_dir_path`: Items With a Well-Defined Root Directory

## ::: exam_gen.property.has_dir_path
    handler: python
    selection:
      inherited_members: True
      filters:
        - "!^_[^_]*"
        - "!log"
        - "__init__"
    rendering:
      show_root_toc_entry: false
      show_if_no_docstring: True
