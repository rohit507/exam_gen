import exam_gen.util.logging as logging
from exam_gen.mixins.config import *
from pathlib import *
import shutil
from exam_gen.builders import Builder
from exam_gen.mixins.path_manager import PathManager

log = logging.new(__name__, level="WARNING")

class Buildable(SettingsManager, PathManager):
    """
    Different pieces of metadata and settings that are part of the build
    process.
    """

    settings.new_value("assets", default=list(), doc=
        """
        A list of static files that should be copied into the directory where
        we're going build each exam. Glob patterns (e.g. `assets/*.png` or
        `**/test.txt`)

        !! Note
           This will copy files relative to the class where it's set.

           If you have:
            - An `Exam` in `proj_dir/midterm.py` asking for `assets/foo.txt`
            - And `Question` in `prod_dir/q1/timer.py` asking for `bar.png` and
              `assets/bar.txt`

           Then you'll get:
            - `proj_dir/assets/foo.txt` copied into `build_dir/assets/foo.txt`
            - `proj_dir/q1/assets/bar.txt` copied into `build_dir/assets/bar.txt`
            - `proj_dir/q1/bar.png` copied into `build_dir/bar.png`

           There is no guaranteed behavior if this would result in some file
           being clobbered.
        """)

    settings.new_group("build", doc=
        """
        Various settings that control how exams and questions
        are built.
        """)


    def setup_build_dir(self, data_dir, build_dir, build_settings=None):
        """
        Copies files from the source directory to the appropriate build
        directory.

        Note: This is a key override function for other classes.
        """

        log_data = dict()
        log_data['files_copied'] = list()

        for glob_pattern in self.settings.assets:

            log.debug("\n\n root dir: %s \n\n file pattern: %s",
                      self.root_dir, glob_pattern)


            input_files = list(self.root_dir.glob(glob_pattern))

            assert (len(input_files) > 0), (
                "Did not find any matching file assets to copy into build "
                " directory. \n\n root dir: {} \n\n file pattern: {}"
                ).format(self.root_dir, glob_pattern)

            for in_file in input_files:
                rel_path = in_file.relative_to(self.root_dir)
                out_file = build_dir / rel_path

                shutil.copyfile(in_file, out_file)

                log.debug("Copying file from %s to %s", in_file, out_file)

                log_data['files_copied'].append({
                    'from': str(in_file), 'to': str(out_file)})

        return log_data # will be dumped into data file for debug


    def generate_build_files(self, data_dir, build_dir, build_settings=None):
        """
        This will generate any additional files needed for building the exam.
        This should be overridden by any class inheriting the 'buildable'
        trait.

        In most cases this will do something like:
          - Initialize the object if needed
          - Run the user-provided code to update the settings and populate
            template fields
          - Evaluate the templates and write the output information to either
            files or internal variables.
          - Save information like
        """

        if type(self) == Buildable:
            raise NotImplementedError("Implement this function in a subclass")

        log_data = dict()
        outputs = dict()
        return (outputs, log_data)

    def run_build_command(self,
                          data_dir,
                          build_dir,
                          build_settings=None):
        """
        Run the actual command needed to construct the output files,
        return information on which files were created as well as logging
        information.
        """

        if type(self) == Buildable:
            raise NotImplementedError("Implement this function in a subclass")

        log_data = dict()
        outputs = dict()
        return (outputs, log_data)
