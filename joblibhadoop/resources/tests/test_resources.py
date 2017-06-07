"""Resource test module."""

import os.path
from joblibhadoop.resources import (conda_environment_filename,
                                    ENVIRONMENT_YML_FILENAME)


def test_environment_file_exists():
    """Checks if environment file exists."""

    assert os.path.exists(conda_environment_filename())
    assert (os.path.basename(conda_environment_filename()) ==
            ENVIRONMENT_YML_FILENAME)
