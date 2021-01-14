# USer setup

This should provide the ability to write a setup function when subclassing
that allows init-like configuration

  - Superclasses should be able to register parameters to that setup function
    with docs on what they mean.
  - Each class w/ whatever bunch of superclasses should have docs on each of
    the possible parameters and what they may or may not mean.
  - When the setup function is called, so will the appropriate parameter
    generating functions be called, and the results passed to their children.
  - There's a pre and post user setup hook that can be called added to by
    subclasses.

Functionally basic, I think it looks like:

  - **__pre_user_setup__**:
      - Basic dunder which should call `super()`
  - **__post_user_setup__**:
      - Basic dunder which should call `super()`
      - Param: user_setup return val
  - **decorator_func**:
      - Add params to attr of function
  - **__user_setup__**:
      - Call pre-setup hook
      - For args: call_arg_retrival_hook
      - Call user_setup
      - Call post_setup hook (w/ return from user_setup)
      - Return user_setup value,
  - **__init_subclass__**:
      - Iterate over all dir-entries:
          - If func then check if decorator make attr exists
              - If yes, add to list of params
          - error if multiple entries assign to same param.
      - Generate docs for list of params, assign to setup function.
      - Done.
