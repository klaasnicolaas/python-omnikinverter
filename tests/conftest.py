"""Shared client fixtures for Omnik tests."""

from collections.abc import AsyncGenerator

import pytest
from aiohttp import ClientSession

from omnikinverter import OmnikInverter


@pytest.fixture
async def omnik_client() -> AsyncGenerator[OmnikInverter, None]:
    """Provide a JavaScript client with an externally managed HTTP session."""
    async with ClientSession() as session:
        yield OmnikInverter(host="example.com", session=session)
