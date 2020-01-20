# Guide for developers
If you're interested in helping to develop The Encryption Compendium, please read this file first.

## Preparing a development environment
You should start by preparing a development environment for the site:

- Create a Python virtual environment with all of the dependencies that you need.
- Add a git hook to format your code (optional but requested if you want to commit code to this repository).
- Create a `.env` file defining configuration options.

### Creating a virtual environment
In this repository's root directory, create a new virtual environment with the project dependencies using

```
python3 -m venv venv \
  && source venv/bin/activate \
  && pip install -r requirements.txt
```

You should also install some additional dependencies that are used specifically for development and testing purposes:

```
pip install selenium tblib pylint black
```

If you want to run the functional tests you should also have [geckodriver](https://github.com/mozilla/geckodriver) installed. Download the [latest release of geckodriver](https://github.com/mozilla/geckodriver/releases) from its repository, and make sure that the `geckodriver` executable is somewhere on your system path.

### Code formatting
If you're planning on committing code to this repository, we ask that you use [Black](https://github.com/psf/black) to format your code, so that we have consistent code formatting across the project. We recommend using the script defined in [this gist](https://gist.github.com/kernelmethod/f324f9251faa29b7f042e40f710ab436) as a pre-commit hook; it will check that all of your Python files have correct syntax and that they are formatted appropriately before your code is committed. You can add this hook by running the following from the root directory of this repository:

```
mkdir .git/hooks
wget \
  "https://gist.githubusercontent.com/kernelmethod/f324f9251faa29b7f042e40f710ab436/raw/d58b6082ebc90d5e158656f70cea05dd000b5930/pre-commit" \
  -O .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Creating a `.env` file
The site uses a `.env` file to define configuration options. The default `.env` file is [`env.dist`](https://github.com/The-Encryption-Compendium/the-encryption-compendium/blob/master/env.dist). Before you can start running the site, you should copy `env.dist` to `.env` and define any configuration options that you might want to use.

- **Testing locally**: if you're going to be testing the site locally with `manage.py`, you only really need to define the following variables:
  - `DEVELOPMENT`: set to `yes`.
  - `DJANGO_SECRET_KEY`: some random string. You can create one pretty easily in the Python REPL as follows:

    ```python
    >>> import secrets, base64
    >>> random_bytes = base64.b64encode(secrets.token_bytes())
    >>> print(random_bytes.decode("utf-8"))
    ```

    or, as a `bash` one-liner:

    ```
    $ python3 -c "import base64 as b, secrets as s; b.b64encode(s.token_bytes()).decode('utf-8')"
    ```

  - `DATABASE_ENGINE`: you should probably just set this to `sqlite` (make sure you have [SQLite](https://sqlite.org/index.html) installed on your machine, of course).

## Running tests
This repository provides some basic unit tests and functional tests for development. To run these tests, follow the instructions for creating a development environment and create a `.env` file. Then run the following:

```
source ./venv/bin/activate
cd ./site
python3 manage.py test
```

If you have any problems running the tests, please make sure that you went through all of the steps to create a development environment (including installing geckodriver) before submitting an issue.

## Running the project
Currently, we provide the following methods for deploying the site:

- Running locally with `manage.py` (for development purposes)

### Run locally with `manage.py`
Create a `.env` file from `env.dist`, and then execute

```
source ./venv/bin/activate
cd ./site
python3 manage.py makemigrations
python3 manage.py migrate --run-syncdb
python3 manage.py runserver
```

This will create a new database, and then run a Django server on http://localhost:8000. You can also use `manage.py` to perform other actions, such as starting a session with your SQL database; run `python3 manage.py --help` to view all of the available options.

Note that if you're just testing locally, you'll probably want to set `DATABASE_ENGINE=sqlite3` in your `.env` file.
