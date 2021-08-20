
import os
from .macros.file_macros import _include_block

module_name = "Documentation Macros"

def define_env(env):
    """
    This is the hook for the functions (new form)
    """

    env.macros.cwd = os.getcwd()

    @env.macro
    def include_file(*vargs, **kwargs):
        return _include_file(env, *vargs, **kwargs)


    @env.macro
    def include_block(*vargs, **kwargs):
        return _include_block(env, *vargs, **kwargs)

def on_post_build(env):
    "Post build action"
    pass
