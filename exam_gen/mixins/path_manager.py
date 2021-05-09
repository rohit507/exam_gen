import inspect
import os
import exam_gen.util.logging as logging
from pathlib import *
from pprint import *
import textwrap

log = logging.new(__name__, level="DEBUG")

class PathManager():
    """
    Helps handle path and file lookup information esp. handling links that are
    written relative to a specific file or definition.

    Parameters:

      root_dir (Path): A path to the root directory for this object.

      parent_obj (PathManager): A parent object that should have a
        `root_dir` in the same directory or a parent directory of this one.

      parent_path (Path): A path that should be a parent of, or equal to, this
        object's root directory. Usually derived from `parent_obj`.
    """

    def __init__(self,
                 *vargs,
                 root_dir=None,
                 parent_obj=None,
                 parent_path=None,
                 **kwargs):

        if root_dir != None: self.root_dir = root_dir
        if parent_obj != None: self.parent_obj = parent_obj
        if parent_path != None: self.parent_path = parent_path

        super(PathManager, self).__init__(*vargs, **kwargs)

        log.debug(
            textwrap.dedent(
            """
            Initializing paths for `%s`:

              Root Dir: %s

              Parent Path: %s

              Use Class Root: %s

              Parent Obj:
            %s
            """
            ),
            self,
            self.root_dir,
            self.parent_path,
            self.use_class_root,
            textwrap.indent(pformat(self.parent_obj), "    "),
        )

        if self.parent_path:

            if isinstance(self.parent_path,Path):
                parent_path = self.parent_path
            elif isinstance(self.parent_path, str):
                parent_path = Path(self.parent_path)
            else:
                assert False, ("`parent_path` field must have type `Path` or"
                              " `str`.")

            if not root_dir.is_absolute():
                assert False, ("`root_dir` must be an absolute path")

        elif issubclass(self.parent_obj, PathManager):

            log.debug("Pulling Parent Path from: %s", pformat(self.parent_obj))

            parent_path = self.parent_obj.root_dir

        else:

            log.debug("No Parent Path from: \n%s\n\n%s\n\n%s",
                      issubclass(self.parent_obj, PathManager),
                      PathManager,
                      pformat(self.parent_obj.__mro__))

        log.debug(
            textwrap.dedent(
            """
            Final Parent Path for `%s`: %s
            """
            ),self,parent_path)

        root_dir = None


        if self.root_dir != None:

            if isinstance(self.root_dir, Path):
                root_dir = self.root_dir
            elif isinstance(self.root_dir, str):
                root_dir = Path(self.root_dir)
            else:
                assert False, ("`root_dir` field must have type `Path` or"
                              " `str`.")

            if not root_dir.is_absolute():
                assert False, ("`root_dir` must be an absolute path")

        elif parent_path != None or self.use_class_root:

            class_root = Path(inspect.getsourcefile(type(self))).parent

            if self.use_class_root or class_root.is_relative_to(parent_path):
                root_dir = class_root
            elif class_root.is_relative_to(Path.cwd()):
                root_dir = class_root
            else:
                assert False, ("class must be defined in the directory, or "
                               "a subdirectory of, `cwd()` or `parent_path`."
                               "Alternately, explicitly specify `root_dir`.")
        else:
          assert False, ("No root directory specified. Try adding "
                         "`root_dir == __file__` as a class variable or "
                         "adding `root_dir=__file__` as an initialization "
                         "parameter.")

        self.root_dir = root_dir
        self.parent_path = parent_path
