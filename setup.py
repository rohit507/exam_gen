import setuptools

# TODO : Set up flags based on https://packaging.python.org/guides/distributing-packages-using-setuptools/#setup-args
# TODO : Set up package data files ala https://setuptools.readthedocs.io/en/latest/userguide/datafiles.html
# TODO : data file tutorial https://kiwidamien.github.io/making-a-python-package-vi-including-data-files.html
setuptools.setup(
    include_package_data=True,
    package_data = {
        '': ['templates/*.jn2*'],
    }
)
