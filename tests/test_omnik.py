"""Basic tests for the Omnik Inverter device."""
import asyncio
from unittest.mock import patch

import aiohttp
import pytest
from aresponses import Response, ResponsesMockServer

from omnikinverter import (
    OmnikInverter,
    OmnikInverterConnectionError,
    OmnikInverterWrongSourceError,
)
from omnikinverter.exceptions import OmnikInverterAuthError, OmnikInverterError

from . import load_fixtures


@pytest.mark.asyncio
async def test_json_request(aresponses: ResponsesMockServer) -> None:
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
async def test_internal_session(aresponses: ResponsesMockServer) -> None:
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
        assert omnik_inverter.session is None


@pytest.mark.asyncio
async def test_internal_session_close_while_in_progress(
    aresponses: ResponsesMockServer,
) -> None:
    """Test internal session is closed/cleaned up when closed during request."""

    # Delay response so connection can be closed during request
    async def response_handler(_: aiohttp.ClientResponse) -> Response:
        await asyncio.sleep(0.2)
        return aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        )

    aresponses.add("example.com", "/test", "GET", response_handler)

    omnik_inverter = OmnikInverter(host="example.com")
    await asyncio.gather(
        omnik_inverter.request("test"), omnik_inverter.close(), return_exceptions=True
    )
    assert omnik_inverter.session is None


@pytest.mark.asyncio
async def test_internal_session_error(aresponses: ResponsesMockServer) -> None:
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
async def test_wrong_js_source(aresponses: ResponsesMockServer) -> None:
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
async def test_wrong_html_source(aresponses: ResponsesMockServer) -> None:
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
async def test_html_no_auth(aresponses: ResponsesMockServer) -> None:
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
async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout from Omnik Inverter."""
    # Faking a timeout by sleeping
    async def response_handler(_: aiohttp.ClientResponse) -> Response:
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
async def test_content_type(aresponses: ResponsesMockServer) -> None:
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
async def test_client_error() -> None:
    """Test request client error from Omnik Inverter."""
    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(host="example.com", session=session)
        with patch.object(
            session, "request", side_effect=aiohttp.ClientError
        ), pytest.raises(OmnikInverterConnectionError):
            assert await client.request("test")


@pytest.mark.asyncio
async def test_http_error404(aresponses: ResponsesMockServer) -> None:
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
async def test_unexpected_response(aresponses: ResponsesMockServer) -> None:
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


@pytest.mark.asyncio
async def test_tcp_serial_number_unset() -> None:
    """Make sure exception is raised when serial_number is needed but not provided."""
    client = OmnikInverter(host="example.com", source_type="tcp")
    with pytest.raises(OmnikInverterAuthError) as excinfo:
        assert await client.tcp_request()

    assert str(excinfo.value) == "serial_number is missing from the request"
