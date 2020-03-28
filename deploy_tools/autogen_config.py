#!/usr/bin/env python3

"""
Script to automatically generate a configuration file for the site.
"""

import argparse
import base64
import os
import yaml

from base64 import b64encode
from secrets import token_bytes

"""
----------------------------------------
Global variables
----------------------------------------
"""

# Directory that this file is located in
DEPLOY_TOOLS_DIR = os.path.dirname(__file__)

# Path to YAML file with available options
AVAILABLE_OPTIONS_FILE = os.path.relpath(
    os.path.join(DEPLOY_TOOLS_DIR, "options.yaml"), os.getcwd()
)
AVAILABLE_OPTIONS = []

# Default location in which to safe the config file
SAVE_LOCATION = os.path.relpath(
    os.path.join(DEPLOY_TOOLS_DIR, os.pardir, ".env"), os.getcwd()
)

"""
----------------------------------------
Argument parsing
----------------------------------------
"""

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "--output",
    help="The filesystem path where the new configuration file should be saved.",
    default=SAVE_LOCATION,
)

"""
Add available configuration options from options.yaml.
"""

config_options = parser.add_argument_group(
    title="Configuration options",
    description=("Available configuration options for deploying the site."),
)

with open(AVAILABLE_OPTIONS_FILE, "r") as f:
    options = yaml.safe_load(f)
    for option in options:
        AVAILABLE_OPTIONS.append(option)

        # Add a new argument corresponding to the configuration
        # parameter.
        params = options[option]
        config_options.add_argument(
            f"-{option}",
            help=params.get("help"),
            default=params.get("default"),
            choices=params.get("choices"),
        )


"""
----------------------------------------
Main script
----------------------------------------
"""


def generate_secret():
    return b64encode(token_bytes()).decode("utf-8")


def create_config(args):
    """
    Create a new config file from the default config.
    """

    if os.path.exists(args.output):
        while True:
            overwrite = input(f"{args.output} already exists. Overwrite? (y/n): ")
            if overwrite.lower() == "n":
                print("Exiting...")
                return
            elif overwrite.lower() == "y":
                break
            else:
                print("Please enter y or n.")

    # Fill in some additional configuration options
    if args.DJANGO_SECRET_KEY is None:
        args.DJANGO_SECRET_KEY = generate_secret()
    if args.POSTGRES_PASSWORD is None:
        args.POSTGRES_PASSWORD = generate_secret()

    # Write all configuration options to the output file
    opts = []
    for opt_name in AVAILABLE_OPTIONS:
        opt = getattr(args, opt_name)
        if opt is None:
            opts.append(f"{opt_name}=")
        else:
            opts.append(f"{opt_name}={opt!r}")

    with open(args.output, "w") as f:
        f.write("\n".join(opts))

    print(f"Config saved to {os.path.abspath(args.output)}")


if __name__ == "__main__":
    args = parser.parse_args()
    create_config(args)
