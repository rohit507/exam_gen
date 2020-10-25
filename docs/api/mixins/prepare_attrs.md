# Prepare Attrs Metaclass 

This metaclass makes it easier to control and manipulate the variables available 
during the class definition process, and has a lot of utility in making class-based 
EDSLs more elegant. 

## Simple Example 

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
    
## DSL Example 

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
class definitions. 

This example does come with a few issues when it comes to sequential inheritance 
and overloading of things defined by parent classes. The next example will explain
how to get around those problems and others. 

## Complex Example 

!!! todo
    - Write example that focuses on gather information from parent classes.
    - Get overloading working. 
    - Show how to handle object creation and making sure there's a clear separation 
      between class attributes and object properties. 
    - Explain how this reacts with the python mro machinery.
    - Add a diagram of how these steps get resolved for a class. 
    

## Generated Documentation 

::: exam_gen.mixins.prepare_attrs
    handler: python
    selection:
      members: 
        - "PrepareAttrs"
      filters: 
        - "!__prepare__" 
    rendering: 
      heading_level: 3 
      show_source: false
      show_root_toc_entry: false
