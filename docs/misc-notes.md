# Notes 

This is just a scratchpad for notes taken during the development process. All the 
stuff here should be eventually moved somewhere else in these docs.

#### **TODO ::**  Parse this stuff out into the docs or elsewhere as apropos. 

  - We're using [`pipenv`](https://pipenv.pypa.io/en/latest/install/#next-steps) to 
    do environment and dependency management for this project. 
    - Installing `pipenv` took running `sudo apt install pipenv` on Ubuntu. 
      - Other install options are found 
        [here](https://pipenv.pypa.io/en/latest/install/#installing-pipenv).
    - Open shell in project directory with `pipenv shell` 
    - Install a package with `pipenv install <pip-package>` 
    - Run a command with `pipenv run <command>` 
    - **Note:** If you're inside a `pipenv shell` you can drop the `pipenv run` prefix
      from all of the commands here that have them.
    
  - We're using [`mkdocs`](https://www.mkdocs.org) for documentation. 
    - We're using [`mkdocstrings`](https://github.com/pawamoy/mkdocstrings) to include
      generated docstrings in the mkdocs output. 
      - Look at [this page](https://pawamoy.github.io/mkdocstrings/usage/) for more 
        detailed usage directions. 
    - The theme is [`mkdocs-material`](https://squidfunk.github.io/mkdocs-material/). 
    - Run doc server with `pipenv run mkdocs serve` and open [http://127.0.0.1:8000/]() .
    - Build a static stite with `pipenv run mkdocs build`, results will be placed 
      in the `site/` directory. 

  - Using best practices taken from [https://sourcery.ai/blog/python-best-practices/]():
    - Import Sort: `pipenv run isort`
    - PEP 8 Convention Check: `pipenv run flake8`
    - Static Type Check: `pipenv run mypy` 
    - Tests and Coverage: `pipenv run pytest --cov --cov-fail-under=100` 
    
  - We're using the instructions 
    [here](https://setuptools.readthedocs.io/en/latest/userguide/quickstart.html) 
    to setup `setuptools` and the core python packaging infrastucture. 
    - 
  
  
# Things To Do 

  - TODO: Figure out what the `options.install_requires` actually means. 
  - TODO: Remove unneccesary dependencies from `Pipfile.lock` 

