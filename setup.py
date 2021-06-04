from setuptools import setup
import setuptools

print("running exam_gen setup.py")

# TODO : Set up flags based on https://packaging.python.org/guides/distributing-packages-using-setuptools/#setup-args
# TODO : Set up package data files ala https://setuptools.readthedocs.io/en/latest/userguide/datafiles.html
# TODO : data file tutorial https://kiwidamien.github.io/making-a-python-package-vi-including-data-files.html
setup(
    dependency_links=[],
    install_requires=[
        "attrs==21.2.0",
        "cloudpickle==1.6.0; python_version >= '3.5'",
        "doit==0.33.1",
        "graphlib==0.9.5",
        "jinja2==2.11.3",
        "jsonpickle==2.0.0",
        "makefun==1.11.3",
        "markupsafe==1.1.1",
        "pep517==0.10.0",
        "pyinotify==0.9.6; sys_platform == 'linux'",
        "pyyaml==5.4.1",
        "toml==0.10.2; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2'",
    ],
    include_package_data=True,
    package_data={"": ["templates/**.jn2*"],},
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["exam-gen = exam_gen.cli:main"]},
)
