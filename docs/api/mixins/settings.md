# Settings Manager

Classes that inherit from `SettingsManager` will gain a `settings` property
that acts like a dictionary of various runtime options.
It also will perform validation of options, auto-generate documentation, and
provide other features that enable a smoother user experience.


## User Docs

### Reading Options

#### In class declarations

``` python
class Foo:
  test_file = settings.data_file_dir + "/test.txt"
```

#### At Runtime

```python
class Foo:
   def init(self):
      self.test_file = self.settings.data_file_dir + "/test.txt"
```

### Settings Options

#### Single Option

In class decls:

```python
class Foo:
  settings.template_file = "template.txt"
```

At runtime:

```python
class Foo:
  def init(self):
    self.settings.template_file = "template.txt"
```

#### Bulk Update

In class decls:

```python
class Foo:
  settings += {
    'template_file': "template.txt",
    'shuffle_choices': range(0,settings.num_choices - 1)
    'metadata': {
      'author': "Jane Doe",
      'date_written': "12/31/2014"
    }
```

At runtime:

```python
class Foo:
  def init(self):
    self.settings += {
      'template_file': "template.txt",
      'shuffle_choices': range(0,self.settings.num_choices - 1)
      'metadata': {
        'author': "Jane Doe",
        'date_written': "12/31/2014"
      }
```

## Developer Docs

### Adding new options

Looks similar to user writing of options with additional `define_option`
function, that has various kwargs.

```python
def Foo(SettingsManager):
  settings.num_cats = define_option(
      default = None,
      short_desc = "Number of cats",
      ...
    )
```

Also works in bulk mode:

```Python
def Foo(SettingsManager):
  settings += {
      'num_cats' : define_option(
          default = None,
          short_desc = "Number of cats",
          ...
      ),
      'dog_park': "Midtown Park",
      'dog_breed': define_option(...)
    }
```

We cover the various possible arguments in the following subsections.

!!! Important
    New options can only be defined in class declarations. Unlike the user
    options, trying to define or update options at runtime is an error.

#### Documentation

  - `short_desc` : Short string describing option
  - `long_desc` : Long string (in docs style markdown) describing option.
    Will be trimmed and dedented before use.

#### Defaults

  - `default` : The default value if not overridden by user or other subclass

#### Validation

  - `validator` :
      - lambda or function that returns true if the value is valid and false
        otherwise. First argument is the option itself, second optional arg
        is the entire settings object as a whole.

        Single arg:

        ```python
        def Foo(SettingsManager):
          settings.num_choices = define_option(
              default = 4,
              validator = lambda n: n > 1 and n <= 26,
              ...
            )
        ```

        Dual arg:

        ```python
        def Foo(SettingsManager):
          settings.data_file = define_option(
              default = 4,
              validator = lambda file, settings: file_exists(settings.data_dir + file),
              ...
            )
        ```

        !!! Important
            Accessing `settings` without the dual arg version of the validator might
            get the wrong value for a setting, before sublasses or the user changes it.
  - `validation_error`: Error message for an invalid option
    - `string`: Can be a static string
    - `lambda`: Can be a lambda or function that returns a string with between 1 and 3 params.
      - `val`: The value being validated
      - `settings`: The root settings object in its current state
      - `metadata`: (As yet undefined) Metadata about where the error occurred and stuff.

!!! Note
    Validation is generally not automatic and needs to be invoked by a subclass
    of `SettingsManager`, as we can't expect settings information to be in a valid state at
    every point in the class definition process.

#### Automatic Derivation

  - `derivation`: Lambda or function that will generate the value from other settings
    information. The parameter is the root settings object.
  - `derive_on_read`: Bool for whether we should try to derive this value automatically
    on a read attempt. (Default: `True`)

#### Mandatory settings

  - `required` : Bool for whether the setting must be defined at validation time. Treats
    an unset value or `None` as a validation error. (default = `False`)

#### Read-Only settings

  - `read_only`: Bool for whether the setting should be writable. Read only terms can
    only be changed by using `update_option` to set `read_only` to `False` first.

#### Update functions

  - `update_with` : lambda or function with 2 or 3 arguments that intercepts any attempts
    to set a value directly and allows you to merge or format the values as needed.
    - Arg 1 `old`: The old value. Will be the default or `None` if no value is set
    - Arg 2 `new`: The new value
    - Optional Arg 3 `settings` : the root settings object you're working with.
      - Note: modifying other settings with this might cause inconsistent results in
        edge cases.

#### Copy function

  - `copy_with` : one parameter lambda or function to be used when we're copying a
    settings object internally. We need to internally deep copy the full settings tree
    when we're generating each subclass's data.

### Aliases

Use `define_alias` to make two options refer to the same value.

```python
def Foo(SettingsManager):
  settings.num_cats = define_alias('animal_counts.cats')
```

The input should be relative to the root settings object and either:
  - A `.` delineated string like in the example
  - Or a list like `['animal_counts','cats']` which would be equivalent to the example.

### Updating existing options

Use `update_option` to change the properties of a term which already exists.

Options are identical to `define_option` and will overwrite those options. These are
separate functions and come with appropriate existence checks.

### Overloading and inheritance

### Integrating validation

!!! Todo
    Probably we'll have some sort of `validate`, `validate_given`, and `validate_all`
    functions or something.

### Error messages

### Documentation generation

### Option provenance tracking

### Duplication on object init

## Internal/Implementation Documentation

Okay, so in order to get the nice behavior I want for mkdocs the docstrings
of tables should look like the following:

```markdown
<table markdown="1">
<tr markdown="block">
<th markdown="1">
Month **test**
</th>
<th markdown="1">
Savings
</th>
</tr>

<tr markdown="block">
<td markdown="1">
January
</td>
<td markdown="block">

  - list
  - other list

!!! Todo
    Here's an admonition
</td>
/tr>

</table>
```

Note how everything happens at the same indentation level, and how nested
markdown blocks are not further indented.

In an ideal world we'd be able to tell whether the contents of block have
span or block level markdown code, but for now we'll just use the existence
of newlines as a proxy.

That way we can at least try to spit out the more human readable markdown
format when it's possible. Otherwise, if there's block level code then we can
produce the (uglier) table version.

#### Wrapt for nicer interface to validation and stuff.

So there's a library `wrapt` (with instructions
[here](https://wrapt.readthedocs.io/en/latest/wrappers.html)) that would let
us wrap the various settings objects in a proxy type with some custom
attributes.

I think it would be super nice looking to do it this way, but impl complexity
cost is probably too high.

## Generated Documentation

::: exam_gen.mixins.settings.data
    handler: python
    rendering:
      heading_level: 3
      show_source: false
      show_root_toc_entry: false
