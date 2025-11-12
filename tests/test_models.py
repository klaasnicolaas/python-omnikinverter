"""Test the models."""

import pytest
from aiohttp import ClientSession
from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from omnikinverter import Device, Inverter, OmnikInverter
from omnikinverter.exceptions import (
    OmnikInverterError,
    OmnikInverterWrongValuesError,
)

from . import load_fixtures


async def test_inverter_js_webdata(
    aresponses: ResponsesMockServer, snapshot: SnapshotAssertion
) -> None:
    """Test request from an Inverter - JS Webdata source."""
    aresponses.add(
        "example.com",
        "/js/status.js",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/x-javascript"},
            text=load_fixtures("status_webdata.js"),
        ),
    )

    async with ClientSession() as session:
        client = OmnikInverter(host="example.com", session=session)
        inverter: Inverter = (await client.perform_request()).inverter()
        assert inverter == snapshot


async def test_device_js_webdata(
    aresponses: ResponsesMockServer, snapshot: SnapshotAssertion
) -> None:
    """Test request from a Device - JS Webdata source."""
    aresponses.add(
        "example.com",
        "/js/status.js",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/x-javascript"},
            text=load_fixtures("status_webdata.js"),
        ),
    )

    async with ClientSession() as session:
        client = OmnikInverter(host="example.com", session=session)
        device: Device = (await client.perform_request()).device()
        assert device == snapshot


async def test_inverter_html(
    aresponses: ResponsesMockServer, snapshot: SnapshotAssertion
) -> None:
    """Test request from an Inverter - HTML source."""
    aresponses.add(
        "example.com",
        "/status.html",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixtures("status.html"),
        ),
    )

    async with ClientSession() as session:
        client = OmnikInverter(
            host="example.com",
            source_type="html",
            username="klaas",
            password="supercool",  # noqa: S106
            session=session,
        )
        inverter: Inverter = (await client.perform_request()).inverter()
        assert inverter == snapshot


async def test_device_html(
    aresponses: ResponsesMockServer, snapshot: SnapshotAssertion
) -> None:
    """Test request from a Device - HTML source."""
    aresponses.add(
        "example.com",
        "/status.html",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixtures("status.html"),
        ),
    )

    async with ClientSession() as session:
        client = OmnikInverter(
            host="example.com",
            source_type="html",
            username="klaas",
            password="supercool",  # noqa: S106
            session=session,
        )
        device: Device = (await client.perform_request()).device()
        assert device == snapshot


async def test_inverter_without_session(
    aresponses: ResponsesMockServer, snapshot: SnapshotAssertion
) -> None:
    """Test request from an Inverter - HTML source and without session."""
    aresponses.add(
        "example.com",
        "/status.html",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixtures("status_solis.html"),
        ),
    )

    client = OmnikInverter(
        host="example.com",
        source_type="html",
        username="klaas",
        password="supercool",  # noqa: S106
    )
    inverter: Inverter = (await client.perform_request()).inverter()
    assert inverter == snapshot


async def test_device_without_session(
    aresponses: ResponsesMockServer, snapshot: SnapshotAssertion
) -> None:
    """Test request from a Device - HTML source and without session."""
    aresponses.add(
        "example.com",
        "/status.html",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixtures("status_solis.html"),
        ),
    )

    client = OmnikInverter(
        host="example.com",
        source_type="html",
        username="klaas",
        password="supercool",  # noqa: S106
    )
    device: Device = (await client.perform_request()).device()
    assert device == snapshot


async def test_inverter_js_devicearray(
    aresponses: ResponsesMockServer, snapshot: SnapshotAssertion
) -> None:
    """Test request from an Inverter - JS DeviceArray source."""
    aresponses.add(
        "example.com",
        "/js/status.js",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/x-javascript"},
            text=load_fixtures("status_devicearray.js"),
        ),
    )

    async with ClientSession() as session:
        client = OmnikInverter(host="example.com", session=session)
        inverter: Inverter = (await client.perform_request()).inverter()
        assert inverter == snapshot


async def test_inverter_js_devicearray_sofar2200tl(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
) -> None:
    """Test request from an SOFAR 2200TL Inverter - JS DeviceArray source."""
    aresponses.add(
        "example.com",
        "/js/status.js",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/x-javascript"},
            text=load_fixtures("status_devicearray_sofar220tl.js"),
        ),
    )

    async with ClientSession() as session:
        client = OmnikInverter(host="example.com", session=session)
        inverter: Inverter = (await client.perform_request()).inverter()
        assert inverter == snapshot


async def test_device_js_devicearray(
    aresponses: ResponsesMockServer, snapshot: SnapshotAssertion
) -> None:
    """Test request from a Device - JS DeviceArray source."""
    aresponses.add(
        "example.com",
        "/js/status.js",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/x-javascript"},
            text=load_fixtures("status_devicearray.js"),
        ),
    )

    async with ClientSession() as session:
        client = OmnikInverter(host="example.com", session=session)
        device: Device = (await client.perform_request()).device()
        assert device == snapshot


async def test_inverter_json(
    aresponses: ResponsesMockServer, snapshot: SnapshotAssertion
) -> None:
    """Test request from an Inverter - JSON source."""
    aresponses.add(
        "example.com",
        "/status.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("status.json"),
        ),
    )

    async with ClientSession() as session:
        client = OmnikInverter(host="example.com", source_type="json", session=session)
        inverter: Inverter = (await client.perform_request()).inverter()
        assert inverter == snapshot


async def test_device_json(
    aresponses: ResponsesMockServer, snapshot: SnapshotAssertion
) -> None:
    """Test request from a Device - JSON source."""
    aresponses.add(
        "example.com",
        "/status.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("status.json"),
        ),
    )

    async with ClientSession() as session:
        client = OmnikInverter(host="example.com", source_type="json", session=session)
        device: Device = (await client.perform_request()).device()
        assert device == snapshot


async def test_wrong_values(aresponses: ResponsesMockServer) -> None:
    """Test on wrong inverter values."""
    aresponses.add(
        "example.com",
        "/status.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("wrong_status.json"),
        ),
    )

    async with ClientSession() as session:
        client = OmnikInverter(host="example.com", source_type="json", session=session)
        with pytest.raises(OmnikInverterWrongValuesError):
            assert (await client.perform_request()).inverter()


async def test_inverter_unknown_source_type() -> None:
    """Test exception on wrong source type."""
    client = OmnikInverter(host="example.com", source_type="blah")
    with pytest.raises(OmnikInverterError) as excinfo:
        assert (await client.perform_request()).inverter()

    assert str(excinfo.value) == "Unknown source type `blah`"


async def test_device_unknown_source_type() -> None:
    """Test exception on wrong source type."""
    client = OmnikInverter(host="example.com", source_type="blah")
    with pytest.raises(OmnikInverterError) as excinfo:
        assert (await client.perform_request()).device()

    assert str(excinfo.value) == "Unknown source type `blah`"
