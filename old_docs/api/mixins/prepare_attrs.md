# PrepareAttrs Metaclass

!!! Todo

    - Move the metaclass to `prepare_attrs.metaclass` and the decorator stuff
      its owm submodule.

## Generated Documentation

::: exam_gen.mixins.prepare_attrs
    handler: python
    selection:
      filters:
        - "!__"
        - "__prepare_attrs__"
    rendering:
      heading_level: 3
      show_source: True
      show_root_toc_entry: false

## General Docs

This metaclass makes it easier to control and manipulate the variables available
during the class definition process, and has a lot of utility in making class-based
EDSLs more elegant.

Python already has the `__init_subclass__` and `__dict__` mechanisms for working
with declaration statements in a class definition. These are great, but they're only
capable of handling the environment of a class after a user has interacted with it.
`PrepareAttrs` gives EDSL authors a way to prepare that environment beforehand and
get a lot of additional power.

!!! warning
    Only the final section has a full example. The other sections of this page use
    working but flawed examples to build up necessary information needed to
    understand the full function of the final example.


## Creating pre-init class attributes

We can use `PrepareAttrs` to magically make a useful attribute

``` python

class Test(metaclass=PrepareAttrs):

  @classmethod
  def __prepare_attrs__(cls,name,bases,env):
     env['test_var'] = 15
     return env

```

Now any classes that derive from `Test` can use `test_var` within their class
definition, ala:

``` python

class Subtest(Test):

   subtest_var = test_var + 20

   def run(self):
      print((self.test_var,self.subtest_var))

Subtest().run()
```

The whole thing when run should print `(15,35)`.

!!! note
    `test_var` and `subtest_var` become properties of the `Subtest`
    *class*, not any particular subtest object. If you're using a mutable
    value like a dictionary then updates will be shared between all the
    various objects involved unless you copy them in the object's `__new__`
    or `__init__` functions.

## Using `prepare_attrs` in a DSL

In general this is meant to be used along with `__init_subclass__` to enable
more declarative DSLs in python, by allowing users to assign and manipulate
terms directly in their new class definitions

Here we're creating a rather contrived exampled where we allow subclasses to
work with options directly and then validate them after the fact.

```python
class ValidateOptions(metaclass=PrepareAttrs):


  @classmethod
  def __prepare_attrs__(cls,name,bases,env):
     env['do_this'] = True
     env['do_that'] = True
     env['do_both'] = True
     return env

  @classmethod
  def __init_subclass__(cls,**kwargs):

     super().__init_subclass__(**kwargs)

     do_this = cls.__dict__['do_this']
     do_that = cls.__dict__['do_that']
     do_both = cls.__dict__['do_both']

     if (do_this and do_that) != do_both:
       raise RuntimeError("Invalid Class Options")

class Test1(ValidateOptions):
  do_this = False
  do_both = do_this and do_that

class Test2(ValidateOptions):
  do_both = False
```

Notice how the user can both update and refer to settings information in their
class definitions. This opens up the class definition as a place for declarations
instead of just defining functions. Classes provide a nice modular grouping for
your users as they interact with whatever system you're building a DSL for.

That said, this example does have a few issues:

  - The first issue is inheritance of properties. Consider adding the following
    class to our example:

    ```python
    class Test3(Test1):
      def __init__(self):
        print(self.do_this)

    Test3()
    ```

    It would print `True` on init despite our `Test1` class overriding the
    definition for `do_this`.
  - Similarly, out current setup doesn't take into account what happens when
    a child class overloads `__prepare_attr__`. In particular if we have the
    following:

    ```python
    class Test4(ValidateOptions):

      @classmethod
      def __prepare_attrs__(cls,name,bases,env):
         env['something'] = True
         return env

    class Test5(Test4):
      var = do_this
    ```

    We will get an error because `do_this` isn't defined into the context of
    `Test5`.

We'll discuss how to deal with these issues in the next few examples.

## Overloading `prepare_attrs`

Before we deal with properly inheriting user made changes, we should look at
how various calls to `prepare_attr` are handled when we have a sequence of
classes inheriting from each other.

```python
from exam_gen.mixins.prepare_attrs import *

class Base(metaclass=PrepareAttrs):

  @classmethod
  def __prepare_attrs__(cls,name,bases,env):
     print((name,cls.__name__,"Base.__prepare_attrs__"))
     return env

class Test1(Base): pass

print("") # Space out print statements

class Test2(Test1):

  @classmethod
  def __prepare_attrs__(cls,name,bases,env):
    env = super().__prepare_attrs__(name,bases,env)
    print((name,cls.__name__,"Test2.__prepare_attrs__"))
    return env

print("") # Space out print statements

class Test3(Test2): pass
```

When run, the above example should print the following:

```bash
('Test1', 'Base', 'Base.__prepare_attrs__')

('Test2', 'Base', 'Base.__prepare_attrs__')
('Test2', 'Test1', 'Base.__prepare_attrs__')

('Test3', 'Base', 'Base.__prepare_attrs__')
('Test3', 'Test1', 'Base.__prepare_attrs__')
('Test3', 'Test2', 'Base.__prepare_attrs__')
('Test3', 'Test2', 'Test2.__prepare_attrs__')
```

The first line of that output means "While generating the attrs for `Test1`
we are calling `Base.__prepare_attrs__` with a class parameter of `Base`."
and likewise for the rest of the lines.

As expected, `Test 1` has a single call from `Base`'s definition of
`prepare_attrs`, which has access to the post-initialization version of the
`Base` class.

Looking at `Test2`'s calls we see something interesting. There are two separate
calls to `Base.__prepare_attrs__`, that have access to the post-init class
definitions of `Base` and `Test1`. **We can use this to implement overloading.**
This is also why we ask for idempotence in your definitions of `__prepare_attrs__`.

Finally, we can take a look at `Test3`'s initialization:

```python
('Test3', 'Base', 'Base.__prepare_attrs__')
('Test3', 'Test1', 'Base.__prepare_attrs__')
('Test3', 'Test2', 'Base.__prepare_attrs__')
('Test3', 'Test2', 'Test2.__prepare_attrs__')
```

This is what we want. Whatever preparation `Base.__prepare_attrs__` does, it
gets to do that prep for every class in `Test3`'s lineage. Likewise
`Test2.__prepare_attrs__` gets to do that prep for `Test3`'s environment.

This is all because of that call to `super()` and without it we would get
the following:

```python
('Test3', 'Base', 'Base.__prepare_attrs__')
('Test3', 'Test1', 'Base.__prepare_attrs__')
('Test3', 'Test2', 'Test2.__prepare_attrs__')
```

And completely forgo `('Test3', 'Test2', 'Base.__prepare_attrs__')` and the
corresponding call to `Base.__prepare_attrs__`. Meaning that any changes
to `Test2` that are handled by `Base`'s handler would be missing. This would
break any effort to update terms at each successive definition.

## Putting it all together

So we're going to be making two classes that allow people to define and
manipulate metadata about a class. Together they should provide a full example
of how to use `PrepareAttrs` properly.

### The `Metadata` class

The `Metadata` class allows the user to work with a single variable at class
definition time, `metadata` which is a standard dictionary the user can edit.
It uses `__prepare_attrs__` to prepare the class environment, then in
`__init_subclass__` it prints that environment out to console.

```python
from pprint import *
from exam_gen.mixins.prepare_attrs import *

class Metadata(metaclass=PrepareAttrs):

  @classmethod
  def __prepare_attrs__(cls,name,bases,env):
     print((name,cls.__name__,"Metadata.__prepare_attrs__"))
     # Call metadata for superclasses if needed
     if hasattr(super(),"__prepare_attrs__"):
       env = super().__prepare_attrs__(name,bases,env)

     # If we don't have any metadata create it
     if 'metadata' not in env:
       env['metadata'] = {}

     # If the metadata has been changed in a class then
     # we can update it here.
     if hasattr(cls,'metadata'):
       env['metadata'].update(cls.metadata)

     return env

  @classmethod
  def __init_subclass__(cls, **kwargs):
    print((cls.__name__,"ClassInfo.__init_subclass__"))
    if hasattr(cls,"metadata"):
      pprint({
        'Class': cls.__name__,
        'mro': [par.__qualname__ for par in cls.__mro__],
        'Metadata at __init__': cls.metadata
      })
```

As `__init_subclass__` amounts to a bunch of print statements
we can focus on `__prepare_attrs__`. It meets the basic criteria
we found in previous sections:

  - Properly calls `super().__prepare_attrs__` and keeps any updates
    that superclasses make to `env`.
  - Does not re-initialize values in `env` if they already exist.
  - Incorporates post-initialization changes from the `cls` parameter
    if they exist. (here via `Dict.update()` though other examples
    will probably be more complex.
  - Returns the new modified `env` when finished.

### Adding `ClassInfo` to `metadata`

This class inherits from `Metadata` and is largely identical. The only
exceptions are a different print statement at the beginning and how
instead of updating the metadata with each class call, it adds some
information about parent classes:

```python
env['metadata']['Base Classes'] = [base.__qualname__ for base in bases]
```

Initializing this class produces the following output:

```python
('ClassInfo', 'Metadata', 'Metadata.__prepare_attrs__')
('ClassInfo', 'ClassInfo.__init_subclass__')
{'Class': 'ClassInfo',
 'Metadata at __init__': {},
 'mro': ['ClassInfo', 'Metadata', 'object']}
```

Which has the expected calls to `Metadata.__prepare_attrs__`, and since
you can't call `ClassInfo.__prepare_attrs__` before there's a `ClassInfo`
object there's no changes to the metadata other than the fact it exists.

### Setting metadata values

Then we have `Test1`, `Test2`, and `Test3`, which only set some metadata
values:

```python
class Test1(Metadata):
  metadata['Name'] = "Walter"

class Test2(Metadata):
  metadata['Count'] = 2

class Test3(Metadata):
  metadata['Name'] = "Beeswax"
```

And the corresponding output only shows that the values are set, and
is otherwise uninteresting:

```python
('Test1', 'Metadata', 'Metadata.__prepare_attrs__')
('Test1', 'ClassInfo.__init_subclass__')
{'Class': 'Test1',
 'Metadata at __init__': {'Name': 'Walter'},
 'mro': ['Test1', 'Metadata', 'object']}

('Test2', 'Metadata', 'Metadata.__prepare_attrs__')
('Test2', 'ClassInfo.__init_subclass__')
{'Class': 'Test2',
 'Metadata at __init__': {'Count': 2},
 'mro': ['Test2', 'Metadata', 'object']}

('Test3', 'Metadata', 'Metadata.__prepare_attrs__')
('Test3', 'ClassInfo.__init_subclass__')
{'Class': 'Test3',
 'Metadata at __init__': {'Name': 'Beeswax'},
 'mro': ['Test3', 'Metadata', 'object']}
```

### Inheritance order and overloading

One of python's quirks is that the order of parent classes in your class
declaration breaks ties in overloading. We want our metadata overloading
system to have the same behavior. Both `Test1` and `Test3` define `name`
so we can test this with the following:

```python
class Test4(Test1,Test3): pass

class Test5(Test3,Test1,ClassInfo): pass
```

Which produces the following output:

```python
('Test4', 'Metadata', 'Metadata.__prepare_attrs__')
('Test4', 'Test3', 'Metadata.__prepare_attrs__')
('Test4', 'Test1', 'Metadata.__prepare_attrs__')
('Test4', 'ClassInfo.__init_subclass__')
{'Class': 'Test4',
 'Metadata at __init__': {'Name': 'Walter'},
 'mro': ['Test4', 'Test1', 'Test3', 'Metadata', 'object']}

('Test5', 'Metadata', 'Metadata.__prepare_attrs__')
('Test5', 'ClassInfo', 'ClassInfo.__prepare_attrs__')
('Test5', 'ClassInfo', 'Metadata.__prepare_attrs__')
('Test5', 'Test1', 'Metadata.__prepare_attrs__')
('Test5', 'Test3', 'Metadata.__prepare_attrs__')
('Test5', 'ClassInfo.__init_subclass__')
{'Class': 'Test5',
 'Metadata at __init__': {'Base Classes': ['Test3', 'Test1', 'ClassInfo'],
                          'Name': 'Beeswax'},
 'mro': ['Test5', 'Test3', 'Test1', 'ClassInfo', 'Metadata', 'object']}
```

Note how the correct name ends up being set in the metadata. In addition
`Test5` has both `ClassInfo` and `Metadata` correctly called during
prep phase.

### Referencing properties set with `prepare_attrs`

The following test cases access information within the metadata in addition
to manipulating it. `Test6` uses `+=` to read and increment a value, similar
functions could allow for many interesting and complex interactions in EDSLs.
`Test7` on the other hand is a simple test that confirms the class declaration
environment functions just like any other imperative code environment.

```python
class Test6(Test1,Test2):
  metadata['Count'] += 8

class Test7(Test6,Test5):
  metadata['Fruit'] = "Pineapple"
  metadata['Info'] = "Test7 has metadata for {}".format(metadata.keys())
  metadata['Pie'] = "Key Lime"
```

The output for `Test6` confirms that the count from `Test2` was correctly
incremented as the class was initialized.

```python
('Test6', 'Metadata', 'Metadata.__prepare_attrs__')
('Test6', 'Test2', 'Metadata.__prepare_attrs__')
('Test6', 'Test1', 'Metadata.__prepare_attrs__')
('Test6', 'ClassInfo.__init_subclass__')
{'Class': 'Test6',
 'Metadata at __init__': {'Count': 10, 'Name': 'Walter'},
 'mro': ['Test6', 'Test1', 'Test2', 'Metadata', 'object']}
```

The output for `Test7` is a bit more verbose, but we can see that `Pie` was not
included in `Info`, as `metadata` didn't have that key when the value for
`Info` was generated.


??? Output
    ```python
    ('Test7', 'Metadata', 'Metadata.__prepare_attrs__')
    ('Test7', 'ClassInfo', 'ClassInfo.__prepare_attrs__')
    ('Test7', 'ClassInfo', 'Metadata.__prepare_attrs__')
    ('Test7', 'Test2', 'Metadata.__prepare_attrs__')
    ('Test7', 'Test1', 'Metadata.__prepare_attrs__')
    ('Test7', 'Test3', 'Metadata.__prepare_attrs__')
    ('Test7', 'Test5', 'ClassInfo.__prepare_attrs__')
    ('Test7', 'Test5', 'Metadata.__prepare_attrs__')
    ('Test7', 'Test6', 'Metadata.__prepare_attrs__')
    ('Test7', 'ClassInfo.__init_subclass__')
    {'Class': 'Test7',
     'Metadata at __init__': {'Base Classes': ['Test6', 'Test5'],
                              'Count': 10,
                              'Fruit': 'Pineapple',
                              'Info': "Test7 has metadata for dict_keys(['Base "
                                      "Classes', 'Count', 'Name', 'Fruit'])",
                              'Name': 'Walter',
                              'Pie': 'Key Lime'},
     'mro': ['Test7',
             'Test6',
             'Test5',
             'Test3',
             'Test1',
             'Test2',
             'ClassInfo',
             'Metadata',
             'object']}
    ```



### Complete Example

??? Example
    ```python
    from pprint import *
    from exam_gen.mixins.prepare_attrs import *

    class Metadata(metaclass=PrepareAttrs):

      @classmethod
      def __prepare_attrs__(cls,name,bases,env):
         print((name,cls.__name__,"Metadata.__prepare_attrs__"))
         # Call metadata for superclasses if needed
         if hasattr(super(),"__prepare_attrs__"):
           env = super().__prepare_attrs__(name,bases,env)

         # If we don't have any metadata create it
         if 'metadata' not in env:
           env['metadata'] = {}

         # If the metadata has been changed in a class then
         # we can update it here.
         if hasattr(cls,'metadata'):
           env['metadata'].update(cls.metadata)

         return env

      @classmethod
      def __init_subclass__(cls, **kwargs):
        print((cls.__name__,"ClassInfo.__init_subclass__"))
        if hasattr(cls,"metadata"):
          pprint({
            'Class': cls.__name__,
            'mro': [par.__qualname__ for par in cls.__mro__],
            'Metadata at __init__': cls.metadata
          })

    print("")

    class ClassInfo(Metadata):
      @classmethod
      def __prepare_attrs__(cls,name,bases,env):
         print((name,cls.__name__,"ClassInfo.__prepare_attrs__"))
         # Call metadata for superclasses if needed
         if hasattr(super(),"__prepare_attrs__"):
           env = super().__prepare_attrs__(name,bases,env)

         # If we don't have any metadata create it
         if 'metadata' not in env:
           env['metadata'] = {}

         # If the metadata has been changed in a class then
         # we can update it here.
         if hasattr(cls,'metadata'):
           env['metadata']['Base Classes'] = [base.__qualname__ for base in bases]

         return env

    print("")

    class Test1(Metadata):
      metadata['Name'] = "Walter"

    print("")

    class Test2(Metadata):
      metadata['Count'] = 2

    print("")

    class Test3(Metadata):
      metadata['Name'] = "Beeswax"

    print("")

    class Test4(Test1,Test3): pass

    print("")

    class Test5(Test3,Test1,ClassInfo): pass

    print("")

    class Test6(Test1,Test2):
      metadata['Count'] += 8

    print("")

    class Test7(Test6,Test5):
      metadata['Fruit'] = "Pineapple"
      metadata['Info'] = "Test7 has metadata for {}".format(metadata.keys())
      metadata['Pie'] = "Key Lime"
    ```

??? Output
    ```
    ('ClassInfo', 'Metadata', 'Metadata.__prepare_attrs__')
    ('ClassInfo', 'ClassInfo.__init_subclass__')
    {'Class': 'ClassInfo',
     'Metadata at __init__': {},
     'mro': ['ClassInfo', 'Metadata', 'object']}

    ('Test1', 'Metadata', 'Metadata.__prepare_attrs__')
    ('Test1', 'ClassInfo.__init_subclass__')
    {'Class': 'Test1',
     'Metadata at __init__': {'Name': 'Walter'},
     'mro': ['Test1', 'Metadata', 'object']}

    ('Test2', 'Metadata', 'Metadata.__prepare_attrs__')
    ('Test2', 'ClassInfo.__init_subclass__')
    {'Class': 'Test2',
     'Metadata at __init__': {'Count': 2},
     'mro': ['Test2', 'Metadata', 'object']}

    ('Test3', 'Metadata', 'Metadata.__prepare_attrs__')
    ('Test3', 'ClassInfo.__init_subclass__')
    {'Class': 'Test3',
     'Metadata at __init__': {'Name': 'Beeswax'},
     'mro': ['Test3', 'Metadata', 'object']}

    ('Test4', 'Metadata', 'Metadata.__prepare_attrs__')
    ('Test4', 'Test3', 'Metadata.__prepare_attrs__')
    ('Test4', 'Test1', 'Metadata.__prepare_attrs__')
    ('Test4', 'ClassInfo.__init_subclass__')
    {'Class': 'Test4',
     'Metadata at __init__': {'Name': 'Walter'},
     'mro': ['Test4', 'Test1', 'Test3', 'Metadata', 'object']}

    ('Test5', 'Metadata', 'Metadata.__prepare_attrs__')
    ('Test5', 'ClassInfo', 'ClassInfo.__prepare_attrs__')
    ('Test5', 'ClassInfo', 'Metadata.__prepare_attrs__')
    ('Test5', 'Test1', 'Metadata.__prepare_attrs__')
    ('Test5', 'Test3', 'Metadata.__prepare_attrs__')
    ('Test5', 'ClassInfo.__init_subclass__')
    {'Class': 'Test5',
     'Metadata at __init__': {'Base Classes': ['Test3', 'Test1', 'ClassInfo'],
                              'Name': 'Beeswax'},
     'mro': ['Test5', 'Test3', 'Test1', 'ClassInfo', 'Metadata', 'object']}

    ('Test6', 'Metadata', 'Metadata.__prepare_attrs__')
    ('Test6', 'Test2', 'Metadata.__prepare_attrs__')
    ('Test6', 'Test1', 'Metadata.__prepare_attrs__')
    ('Test6', 'ClassInfo.__init_subclass__')
    {'Class': 'Test6',
     'Metadata at __init__': {'Count': 10, 'Name': 'Walter'},
     'mro': ['Test6', 'Test1', 'Test2', 'Metadata', 'object']}

    ('Test7', 'Metadata', 'Metadata.__prepare_attrs__')
    ('Test7', 'ClassInfo', 'ClassInfo.__prepare_attrs__')
    ('Test7', 'ClassInfo', 'Metadata.__prepare_attrs__')
    ('Test7', 'Test2', 'Metadata.__prepare_attrs__')
    ('Test7', 'Test1', 'Metadata.__prepare_attrs__')
    ('Test7', 'Test3', 'Metadata.__prepare_attrs__')
    ('Test7', 'Test5', 'ClassInfo.__prepare_attrs__')
    ('Test7', 'Test5', 'Metadata.__prepare_attrs__')
    ('Test7', 'Test6', 'Metadata.__prepare_attrs__')
    ('Test7', 'ClassInfo.__init_subclass__')
    {'Class': 'Test7',
     'Metadata at __init__': {'Base Classes': ['Test6', 'Test5'],
                              'Count': 10,
                              'Fruit': 'Pineapple',
                              'Info': "Test7 has metadata for dict_keys(['Base "
                                      "Classes', 'Count', 'Name', 'Fruit'])",
                              'Name': 'Walter',
                              'Pie': 'Key Lime'},
     'mro': ['Test7',
             'Test6',
             'Test5',
             'Test3',
             'Test1',
             'Test2',
             'ClassInfo',
             'Metadata',
             'object']}
    ```
