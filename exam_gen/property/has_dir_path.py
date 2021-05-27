import attr
import inspect
import textwrap
import os

from pprint import *
from pathlib import *

import exam_gen.util.logging as logging

log = logging.new(__name__, level="WARNING")

@attr.s
class HasDirPath():
    """
    Helps handle path and file lookup information esp. handling links that are
    written relative to a specific file or definition.

    Parameters:

      root_dir (Path): A path to the root directory for this object.

      parent_obj (HasDirPath): A parent object that should have a
        `root_dir` in the same directory or a parent directory of this one.

      parent_path (Path): A path that should be a parent of, or equal to, this
        object's root directory. Usually derived from `parent_obj`.
    """

    root_dir = attr.ib(default=None, kw_only=True)

    parent_obj = attr.ib(default=None, kw_only=True)

    parent_path = attr.ib(default=None, kw_only=True)

    use_class_root = attr.ib(default=False, kw_only=True)

    def __attrs_post_init__(self):

        if hasattr(super(),'__attrs_post_init__'):
            super().__attrs_post_init__()

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

        self._init_parent_path()
        self._init_root_dir()

    def _init_parent_path(self):

        parent_path = None

        if self.parent_path:

            parent_path = Path(self.parent_path)
            assert parent_path.is_absolute(), (
                "`parent_path` must be an absolute path")

        elif ((type(self.parent_obj) == HasDirPath) or
            issubclass(type(self.parent_obj), HasDirPath)):

            log.debug("Pulling Parent Path from: %s", pformat(
                self.parent_obj.__dict__))

            parent_path = self.parent_obj.root_dir

        else:

            log.debug("No Parent Path from: \n%s\n\n%s",
                      issubclass(type(self.parent_obj), HasDirPath),
                      type(self.parent_obj))

        self.parent_path = parent_path


    def _init_root_dir(self):

        root_dir = None

        if self.root_dir != None:

            root_dir = Path(self.root_dir)

            assert root_dir.is_absolute(), (
                "`root_dir` must be an absolute path")

        elif self.parent_path != None or self.use_class_root:

            class_root = Path(inspect.getsourcefile(type(self))).parent

            if self.use_class_root or class_root.is_relative_to(self.parent_path):
                root_dir = class_root
            elif class_root.is_relative_to(Path.cwd()):
                root_dir = class_root
            else:
                root_dir = self.parent_path

        else:
          assert False, ("No root directory specified. Try adding "
                         "`root_dir == __file__` as a class variable or "
                         "adding `root_dir=__file__` as an initialization "
                         "parameter.")

        self.root_dir = root_dir

    def lookup_file(self, filename):

        if Path(self.root_dir, filename).exists():
           return Path(self.root_dir, filename)
        elif (self.parent_path != None
              and Path(self.parent_path, filename).exists()):
            return Path(self.parent_path, filename)
        elif (self.parent_obj != None
              and issubclass(type(self.parent_obj), HasDirPath)):
            return parent_obj.lookup_file(filename)
        else:
            raise RuntimeError(("Could not find file '{}' in either "
                                "{} or {}").format(filename,
                                                   self.root_dir,
                                                   self.parent_path))
