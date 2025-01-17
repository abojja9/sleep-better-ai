import pytest
import tempfile
import os

@pytest.fixture(scope="session")
def test_db_path():
    """Create a temporary database file for testing"""
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)
    os.unlink(path)