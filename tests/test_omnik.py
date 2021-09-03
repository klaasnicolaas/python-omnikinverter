"""Basic tests for the Omnik Inverter device."""
import asyncio

import aiohttp
import pytest

from omnikinverter import (
    OmnikInverter,
    OmnikInverterConnectionError,
    OmnikInverterWrongSourceError,
)
from omnikinverter.exceptions import OmnikInverterError

from . import load_fixtures


@pytest.mark.asyncio
async def test_wrong_source(aresponses):
    """Test on wrong data source error raise."""
    aresponses.add(
        "example.com",
        "/js/status.js",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/x-javascript"},
            text=load_fixtures("status_wrong.js"),
        ),
    )

    async with aiohttp.ClientSession() as session:
        omnik = OmnikInverter(host="example.com", session=session)
        with pytest.raises(OmnikInverterWrongSourceError):
            assert await omnik.inverter()


@pytest.mark.asyncio
async def test_timeout(aresponses):
    """Test request timeout from Omnik Inverter."""
    # Faking a timeout by sleeping
    async def response_handler(_):
        await asyncio.sleep(0.2)
        return aresponses.Response(
            body="Goodmorning!", text=load_fixtures("status_webdata.js")
        )

    aresponses.add("example.com", "/js/status.js", "GET", response_handler)

    async with aiohttp.ClientSession() as session:
        omnik = OmnikInverter(host="example.com", session=session)
        with pytest.raises(OmnikInverterConnectionError):
            assert await omnik.inverter()


@pytest.mark.asyncio
async def test_http_error404(aresponses):
    """Test HTTP 404 response handling."""
    aresponses.add(
        "example.com",
        "/omnik/test",
        "GET",
        aresponses.Response(text="Give me energy!", status=404),
    )

    async with aiohttp.ClientSession() as session:
        omnik = OmnikInverter(host="example.com", session=session)
        with pytest.raises(OmnikInverterError):
            assert await omnik.request("test")


@pytest.mark.asyncio
async def test_unexpected_response(aresponses):
    """Test unexpected response handling."""
    aresponses.add(
        "example.com",
        "/omnik/test",
        "GET",
        aresponses.Response(text="Give me energy!", status=200),
    )

    async with aiohttp.ClientSession() as session:
        omnik = OmnikInverter(host="example.com", session=session)
        with pytest.raises(OmnikInverterError):
            assert await omnik.request("test")
