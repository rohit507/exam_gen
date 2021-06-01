import attr
import shutil

from .has_settings import HasSettings
from .has_dir_path import HasDirPath

import exam_gen.util.logging as logging

log = logging.new(__name__, level="WARNING")


class Buildable(HasSettings, HasDirPath):
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

    def setup_build(self, build_info):
        """
        Copies files from the source directory to the appropriate build
        directory.

        Note: This is a key override function for other classes.
        """


        data_dir = build_info.data_path
        build_dir = build_info.build_path

        log_data = dict()
        log_data['files_copied'] = list()

        for glob_pattern in self.settings.assets:

            input_files = list(self.root_dir.glob(glob_pattern))

            log.debug("\n\n root dir: %s "
                        "\n\n file pattern: %s"
                        "\n\n data_dir: %s"
                        "\n\n build_dir: %s"
                        "\n\n input_files: %s",
                        self.root_dir,
                        glob_pattern,
                        data_dir,
                        build_dir,
                        input_files)



            assert (len(input_files) > 0), (
                "Did not find any matching file assets to copy into build "
                " directory. \n\n root dir: {} \n\n file pattern: {}"
                ).format(self.root_dir, glob_pattern)

            for in_file in input_files:
                rel_path = in_file.relative_to(self.root_dir)
                out_file = build_dir / rel_path

                log.debug("\n\n root dir: %s "
                          "\n\n file pattern: %s"
                          "\n\n data_dir: %s"
                          "\n\n build_dir: %s"
                          "\n\n in_file: %s"
                          "\n\n out_file: %s"
                          "\n\n rel_path: %s",
                          self.root_dir,
                          glob_pattern,
                          data_dir,
                          build_dir,
                          in_file,
                          out_file,
                          rel_path)

                shutil.copyfile(in_file, out_file)

                log.debug("Copying file from %s to %s", in_file, out_file)

                log_data['files_copied'].append({
                    'from': str(in_file), 'to': str(out_file)})

        return log_data # will be dumped into data file for debug

    def finalize_build(self, build_info):
        """
        To be run once all the build subcommands are done, in order to
        generate the target file in the build directory.

        Note: This isn't run recursively on sub-documents by default.

        Returns:

           (log, success)
        """
        pass

    def output_build(self, build_info):
        """
        Copies the files from the build directory to the output directory
        Options to rename them should be in build_settings.
        """
        pass

    def cleanup_build(self, build_info):
        """
        Generic cleanup task for a build.

        Default: deletes the build directory
        """

        shutil.rmtree(build_dir)


"""
Build-Settings Options:

  - version : 'exam' or `solution`
  - output_file : the filename for the final output file
  - output_format : format str w/ `{sid}`, `{class}` as fields
"""
