"""Testing functionality for the Omnik Inverter device."""
import os


def _fixture_path(filename: str) -> str:
    return os.path.join(os.path.dirname(__file__), "fixtures", filename)


def load_fixtures(filename: str) -> str:
    """Load a fixture."""
    with open(_fixture_path(filename), encoding="utf-8") as fptr:
        return fptr.read()


def load_fixture_bytes(filename: str) -> bytes:
    """Load a fixture as binary data."""
    with open(_fixture_path(filename), "rb") as fptr:
        return fptr.read()
