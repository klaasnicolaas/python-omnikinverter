"""Test the models."""

import json
from collections.abc import Callable

import pytest
from aiohttp import ClientSession
from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from omnikinverter import Device, Inverter, OmnikInverter, OmnikInverterData
from omnikinverter.exceptions import (
    OmnikInverterError,
    OmnikInverterWrongSourceError,
    OmnikInverterWrongValuesError,
)

from . import load_fixtures


async def test_inverter_js_webdata(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    omnik_client: OmnikInverter,
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

    inverter: Inverter = await omnik_client.inverter()
    assert inverter == snapshot


async def test_device_js_webdata(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    omnik_client: OmnikInverter,
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

    device: Device = await omnik_client.device()
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
        inverter: Inverter = await client.inverter()
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
        device: Device = await client.device()
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
    inverter: Inverter = await client.inverter()
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
    device: Device = await client.device()
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
        inverter: Inverter = await client.inverter()
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
        inverter: Inverter = await client.inverter()
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
        device: Device = await client.device()
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
        inverter: Inverter = await client.inverter()
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
        device: Device = await client.device()
        assert device == snapshot


@pytest.mark.parametrize(
    ("source_type", "path", "fixture"),
    [
        ("javascript", "/js/status.js", "status_webdata.js"),
        ("json", "/status.json", "status.json"),
        ("html", "/status.html", "status.html"),
    ],
)
async def test_data_single_request(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    source_type: str,
    path: str,
    fixture: str,
) -> None:
    """Test that Inverter and Device data are fetched with a single request."""
    aresponses.add(
        "example.com",
        path,
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixtures(fixture),
        ),
    )

    async with ClientSession() as session:
        client = OmnikInverter(
            host="example.com",
            source_type=source_type,
            username="klaas",
            password="supercool",  # noqa: S106
            session=session,
        )
        data: OmnikInverterData = await client.data()

    aresponses.assert_plan_strictly_followed()
    assert data.inverter == snapshot(name="inverter")
    assert data.device == snapshot(name="device")


async def test_data_unknown_source_type() -> None:
    """Test exception on wrong source type."""
    client = OmnikInverter(host="example.com", source_type="blah")
    with pytest.raises(OmnikInverterError) as excinfo:
        assert await client.data()

    assert str(excinfo.value) == "Unknown source type `blah`"


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
            assert await client.inverter()


async def test_inverter_unknown_source_type() -> None:
    """Test exception on wrong source type."""
    client = OmnikInverter(host="example.com", source_type="blah")
    with pytest.raises(OmnikInverterError) as excinfo:
        assert await client.inverter()

    assert str(excinfo.value) == "Unknown source type `blah`"


async def test_device_unknown_source_type() -> None:
    """Test exception on wrong source type."""
    client = OmnikInverter(host="example.com", source_type="blah")
    with pytest.raises(OmnikInverterError) as excinfo:
        assert await client.device()

    assert str(excinfo.value) == "Unknown source type `blah`"


@pytest.mark.parametrize("current_power", [0, "0"])
def test_inverter_json_zero_power(current_power: int | str) -> None:
    """Test that zero power from the JSON source is not treated as missing."""
    data = json.loads(load_fixtures("status.json"))
    data["i_pow_n"] = current_power

    inverter = Inverter.from_json(data)
    assert inverter.solar_current_power == 0


def test_inverter_json_empty_value() -> None:
    """Test that an empty value from the JSON source is treated as missing."""
    data = json.loads(load_fixtures("status.json"))
    data["i_pow"] = ""

    inverter = Inverter.from_json(data)
    assert inverter.solar_rated_power is None


def test_inverter_json_invalid_value() -> None:
    """Test exception on a non-numeric value from the JSON source."""
    data = json.loads(load_fixtures("status.json"))
    data["i_pow_n"] = "n/a"

    with pytest.raises(OmnikInverterWrongSourceError) as excinfo:
        Inverter.from_json(data)

    assert (
        str(excinfo.value) == "Your inverter returned an invalid value for `i_pow_n`."
    )


def test_inverter_js_too_few_values() -> None:
    """Test exception on JS data with fewer values than expected."""
    with pytest.raises(OmnikInverterWrongSourceError):
        Inverter.from_js('var webData="NLDN1234,V5,V4";')


@pytest.mark.parametrize("parser", [Device.from_html, Device.from_js])
def test_device_wrong_source(parser: Callable[[str], Device]) -> None:
    """Test exception on data without the expected Device values."""
    with pytest.raises(OmnikInverterWrongSourceError):
        parser("<html>Not an Omnik</html>")
