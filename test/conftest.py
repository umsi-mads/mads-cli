import os
import pytest


@pytest.fixture
def env():
    """Fixture to reset the environment before tests"""

    orig = os.environ.copy()
    yield os.environ
    os.environ.clear()
    os.environ.update(orig)
