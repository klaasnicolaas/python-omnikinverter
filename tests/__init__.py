"""Testing functionality for the Omnik Inverter device."""

from pathlib import Path


def _fixture_path(filename: str) -> Path:
    return Path(__file__).parent / "fixtures" / filename


def load_fixtures(filename: str) -> str:
    """Load a fixture."""
    return _fixture_path(filename).read_text(encoding="utf-8")


def load_fixture_bytes(filename: str) -> bytes:
    """Load a fixture as binary data."""
    return _fixture_path(filename).read_bytes()
