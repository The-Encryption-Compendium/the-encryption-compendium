# Guide for developers
If you're interested in helping to develop The Encryption Compendium, please read this file first.

## Preparing a development environment
You should start by preparing a development environment for the site:

- Create a Python virtual environment with all of the dependencies that you need.
- Create a `.env` file defining configuration options.
- Add pre-commit hooks to check for formatting errors, private keys, and so on.

```
python3 -m venv venv \
&& source venv/bin/activate \
&& pip install -r requirements.txt -r requirements.dev.txt \
&& python3 deploy_tools/autogen_config.py \
&& pre-commit install
```

and make sure to install the latest release of [geckodriver](https://github.com/mozilla/geckodriver) to a location on your `PATH`.

### Creating a virtual environment
In this repository's root directory, create a new virtual environment with the project dependencies using

```
python3 -m venv venv \
  && source venv/bin/activate \
  && pip install -r requirements.txt
```

You should also install some additional dependencies that are used specifically for development and testing purposes:

```
pip install -r requirements.dev.txt
```

If you want to run the functional tests you should also have [geckodriver](https://github.com/mozilla/geckodriver) installed. Download the [latest release of geckodriver](https://github.com/mozilla/geckodriver/releases) from its repository, and make sure that the `geckodriver` executable is somewhere on your system path.

### Creating a `.env` file
The site uses a `.env` file to define configuration options. You can run the `deploy_tools/autogen_config.py` script in order to generate a new config file. You can see all of the available configuration options by running

```
$ python3 deploy_tools/autogen_config.py --help
```

If you just want to get the site up and running locally as quickly as possible, you can just run

```
$ python3 deploy_tools/autogen_config.py
```

If you plan on testing locally with docker-compose, you should instead run

```
$ python3 deploy_tools/autogen_config.py -DATABASE_ENGINE=postgres
```

### Pre-commit hooks
If you're planning on committing code to this repository, we ask that you install the git hooks defined in `.pre-commit-config.yaml` (using the [pre-commit Python package](https://pre-commit.com/)). In addition to automatically formatting your code, these hooks will also check for syntax errors, look for secret keys you may have accidentally committed, and so on. The site's [CI system](https://travis-ci.com/github/The-Encryption-Compendium/the-encryption-compendium) will automatically check that the pre-commit hooks are satisfied whenever you push code to a branch.

To install the hooks, run

```
$ pre-commit install
```

after installing the development requirements with `pip install -r requirements.dev.txt`.

## Running tests
This repository provides some basic unit tests and functional tests for development. To run these tests, follow the instructions for creating a development environment and create a `.env` file. Then run the following:

```
source ./venv/bin/activate
cd ./src
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
cd ./src
python3 manage.py makemigrations
python3 manage.py migrate --run-syncdb
python3 manage.py runserver
```

This will create a new database, and then run a Django server on http://localhost:8000. You can also use `manage.py` to perform other actions, such as starting a session with your SQL database; run `python3 manage.py --help` to view all of the available options.

Note that if you're just testing locally, you'll probably want to set `DATABASE_ENGINE=sqlite3` in your `.env` file.
