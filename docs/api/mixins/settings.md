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

??? Random Test Code
    ```python
    from pprint import *
    from inspect import *
    # from exam_gen.util.dynamic_call import *
    # from exam_gen.mixins.yaml_rep import *
    from exam_gen.mixins.settings.map import *

    class Foo: pass

    settings = Settings(
        context = Foo,
        long_desc = """
        Here's a quick test of a settings group description with some
        complex components. **Like** *some* formatting.

        !!! Note
            Or this admonition.
        """,
        path = "settings"
        )

    # pprint(settings._as_dict())

    settings.new_setting(
        name = "test",
        desc = "A test setting, that does something.",
        options = {
            "option_1" : "this is option 1",
            "option_2" : "this is option **2**",
            }
        )

    # settings.new_setting_group(
    #     name = "group",
    #     desc = """
    #     Here's some more compllex formatting in a group description.

    #     > Like a quote

    #     !!! Note
    #         And another admontition
    #     """,
    #     )

    ## pprint(settings._as_dict())
    print(settings.test)
    settings.test = 4
    print(settings.test)
    settings.test += 4
    print(settings.test)

    settings_new = settings._clone()
    pprint(settings._as_dict())
    pprint(settings_new._as_dict())
    settings_new.test += 123
    print(settings.test)
    print(settings_new.test)


    # pprint(settings._as_dict())
    # pprint(settings._gen_docs())
    ```

??? Jinja Stuff
    ```python
    from jinja2 import Environment, meta

    docs_template_string = """
    {{long_desc}}
    {% if table != {} %}

    **{{table_title}}:**
    <table markdown="1">
    <tr markdown="1">
    <th markdown="1">
    {{table_header}}
    </th>
    <th markdown="1">
    {{desc_header}}
    </th>
    </tr>
    {% for (name, desc) in table.items() %}
    <tr markdown="1">
    <td markdown="1">
    `{{name}}`
    </td>
    <td markdown="1">
    {{desc}}
    </th>
    </tr>
    {% endfor %}
    </table>
    {% endif %}
    """

    print(meta.find_undeclared_variables(Environment().parse(docs_template_string)))
    ```

??? Example

    Code:

    ```python
    from pprint import *
    from inspect import *
    # from exam_gen.util.dynamic_call import *
    # from exam_gen.mixins.yaml_rep import *
    from exam_gen.mixins.settings.map import *

    class Foo(SettingsManager):

        settings.new_setting(
            "test",
            desc = "test setting"
            )
        settings.test = 3

        pass

    class Bar(Foo):
        settings.new_setting(
            "test2",
            desc = "test setting 2"
            )
        settings.test2 = 2
        settings.test2 += settings.test
        settings.test = 4

    class Buzz(Foo):
        settings.new_setting(
            "test3",
            desc = "test setting 3"
            )
        settings.test3 = "hello"
        settings.test3 += " " + str(settings.test)
        settings.test = 12

    class Bing(Bar, Buzz): pass
    class Bong(Buzz, Bar): pass

    foo = Foo()
    bar = Bar()
    buzz = Buzz()
    bing = Bing()
    bong = Bong()
    foo.settings.test = 14

    pprint({
        'Foo': {
            'test': str(Foo.settings.test),
        },
        'foo': {
            'test': str(foo.settings.test),
        },
        'Bar': {
            'test': str(Bar.settings.test),
            'test2': str(Bar.settings.test2),
        },
        'bar': {
            'test': str(bar.settings.test),
            'test2': str(bar.settings.test2),
        },
        'Buzz': {
            'test': str(Buzz.settings.test),
            'test3': str(Buzz.settings.test3),
        },
        'buzz': {
            'test': str(buzz.settings.test),
            'test3': str(buzz.settings.test3),
        },
        'Bing': {
            'test': str(Bing.settings.test),
            'test2': str(Bing.settings.test2),
            'test3': str(Bing.settings.test3),
        },
        'bing': {
            'test': str(bing.settings.test),
            'test2': str(bing.settings.test2),
            'test3': str(bing.settings.test3),
        },
        'Bong': {
            'test': str(Bong.settings.test),
            'test2': str(Bong.settings.test2),
            'test3': str(Bong.settings.test3),
        },
        'bong': {
            'test': str(bong.settings.test),
            'test2': str(bong.settings.test2),
            'test3': str(bong.settings.test3),
        },
        }
    )
    ```

    Output:

    ```python
    {'Bar': {'test': '4', 'test2': '5'},
     'Bing': {'test': '4', 'test2': '5', 'test3': 'hello 3'},
     'Bong': {'test': '12', 'test2': '5', 'test3': 'hello 3'},
     'Buzz': {'test': '12', 'test3': 'hello 3'},
     'Foo': {'test': '3'},
     'bar': {'test': '4', 'test2': '5'},
     'bing': {'test': '4', 'test2': '5', 'test3': 'hello 3'},
     'bong': {'test': '12', 'test2': '5', 'test3': 'hello 3'},
     'buzz': {'test': '12', 'test3': 'hello 3'},
     'foo': {'test': '14'}}
    ```

!!! Todo
    Implement freezing of settings data later.

## Generated Documentation

::: exam_gen.mixins.settings
