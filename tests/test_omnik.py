"""Basic tests for the Omnik Inverter device."""
import asyncio
from unittest.mock import patch

import aiohttp
import pytest

from omnikinverter import (
    OmnikInverter,
    OmnikInverterConnectionError,
    OmnikInverterWrongSourceError,
)
from omnikinverter.exceptions import OmnikInverterAuthError, OmnikInverterError

from . import load_fixtures


@pytest.mark.asyncio
async def test_json_request(aresponses):
    """Test JSON response is handled correctly."""
    aresponses.add(
        "example.com",
        "/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )
    async with aiohttp.ClientSession() as session:
        omnik_inverter = OmnikInverter("example.com", session=session)
        await omnik_inverter.request("test")
        await omnik_inverter.close()


@pytest.mark.asyncio
async def test_internal_session(aresponses):
    """Test JSON response is handled correctly."""
    aresponses.add(
        "example.com",
        "/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )
    async with OmnikInverter("example.com") as omnik_inverter:
        await omnik_inverter.request("test")


@pytest.mark.asyncio
async def test_internal_session_error(aresponses):
    """Test JSON response is handled correctly."""
    aresponses.add(
        "example.com",
        "/test",
        "GET",
        aresponses.Response(
            status=500,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )

    with pytest.raises(OmnikInverterConnectionError):
        async with OmnikInverter("example.com") as omnik_inverter:
            await omnik_inverter.request("test")


@pytest.mark.asyncio
async def test_wrong_js_source(aresponses):
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
        client = OmnikInverter(host="example.com", session=session)
        with pytest.raises(OmnikInverterWrongSourceError):
            assert await client.inverter()


@pytest.mark.asyncio
async def test_wrong_html_source(aresponses):
    """Test on wrong data source error raise."""
    aresponses.add(
        "example.com",
        "/status.html",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixtures("wrong_status.html"),
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(  # noqa: S106
            host="example.com",
            source_type="html",
            username="klaas",
            password="supercool",
            session=session,
        )
        with pytest.raises(OmnikInverterWrongSourceError):
            assert await client.inverter()


@pytest.mark.asyncio
async def test_html_no_auth(aresponses):
    """Test on html request without auth."""
    aresponses.add(
        "example.com",
        "/status.html",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(host="example.com", source_type="html", session=session)
        with pytest.raises(OmnikInverterAuthError):
            assert await client.inverter()


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
        client = OmnikInverter(host="example.com", session=session, request_timeout=0.1)
        with pytest.raises(OmnikInverterConnectionError):
            assert await client.inverter()


@pytest.mark.asyncio
async def test_content_type(aresponses):
    """Test request content type error from Omnik Inverter."""
    aresponses.add(
        "example.com",
        "/js/status.js",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "blabla/blabla"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(host="example.com", session=session)
        with pytest.raises(OmnikInverterError):
            assert await client.inverter()


@pytest.mark.asyncio
async def test_client_error():
    """Test request client error from Omnik Inverter."""
    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(host="example.com", session=session)
        with patch.object(
            session, "request", side_effect=aiohttp.ClientError
        ), pytest.raises(OmnikInverterConnectionError):
            assert await client.request("test")


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
        client = OmnikInverter(host="example.com", session=session)
        with pytest.raises(OmnikInverterError):
            assert await client.request("test")


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
        client = OmnikInverter(host="example.com", session=session)
        with pytest.raises(OmnikInverterError):
            assert await client.request("test")
