"""Joblibhadoop resources module."""

import os.path

ENVIRONMENT_YML_FILENAME = 'joblib-hadoop-environment.yml'


def conda_environment_filename():
    """Return the conda environment filename."""
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ENVIRONMENT_YML_FILENAME)

