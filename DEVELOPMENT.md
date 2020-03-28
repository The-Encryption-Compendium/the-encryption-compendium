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
pip install -r requirements.dev.txt
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
