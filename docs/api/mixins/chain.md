# Data Chaining

This is a set of utility functions and a superclass to allowing distribution
and collection of data through a nested object of some sort.

This is for doing things like:
  - Assigning problem numbers
  - Gather Score Information
  - Providing Stable Random Seeds

And a bunch of other really common tasks that will happen repeatedly in
processing.

## Hooks

### Preorder Traverse

Do a preorder fold through all elements

  - `Var` : The variable to be set
  - `Collector` : The intermediate state that's passed

## Collect

  - `Gather` : Gather some value.
  - `Reduce` : Reduce the terms together.
  - `Members` : Members to gather the values from.
