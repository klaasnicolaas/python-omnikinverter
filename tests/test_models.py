"""Test the models."""

import pytest
from aiohttp import ClientSession
from aresponses import ResponsesMockServer

from omnikinverter import Device, Inverter, OmnikInverter
from omnikinverter.exceptions import (
    OmnikInverterError,
    OmnikInverterWrongValuesError,
)

from . import load_fixtures


async def test_inverter_js_webdata(aresponses: ResponsesMockServer) -> None:
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
        assert inverter
        assert inverter.serial_number == "12345678910"
        assert inverter.firmware == "NL2-V9.8-5931"
        assert inverter.firmware_slave == "V5.3-00157"
        assert inverter.model == "omnik4000tl2"
        assert inverter.alarm_code == "F13"
        assert inverter.solar_rated_power == 4000
        assert inverter.solar_current_power == 140
        assert inverter.solar_energy_today == 0.3
        assert inverter.solar_energy_total == 15363.7


async def test_device_js_webdata(aresponses: ResponsesMockServer) -> None:
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
        assert device
        assert device.signal_quality == 96
        assert device.firmware == "H4.01.38Y1.0.09W1.0.08"
        assert device.ip_address == "192.168.0.10"


async def test_inverter_html(aresponses: ResponsesMockServer) -> None:
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
        assert inverter
        assert inverter.serial_number == "12345678910"
        assert inverter.firmware == "V5.07Build245"
        assert inverter.firmware_slave is None
        assert inverter.model == "Omnik2500tl"
        assert inverter.alarm_code == "F13"
        assert inverter.solar_rated_power == 2500
        assert inverter.solar_current_power == 219
        assert inverter.solar_energy_today == 0.23
        assert inverter.solar_energy_total == 6454.5


async def test_device_html(aresponses: ResponsesMockServer) -> None:
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
        assert device
        assert device.signal_quality is None
        assert device.firmware == "ME_08_0102_2.03"
        assert device.ip_address == "192.168.0.106"


async def test_inverter_without_session(aresponses: ResponsesMockServer) -> None:
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
    assert inverter
    assert inverter.serial_number == "1234567890ABCDE"
    assert inverter.firmware == "001F"
    assert inverter.firmware_slave == "002F"
    assert inverter.model == "0079"
    assert inverter.alarm_code is None
    assert inverter.solar_rated_power is None
    assert inverter.solar_current_power == 5850
    assert inverter.solar_energy_today == 9.80
    assert inverter.solar_energy_total == 44.0


async def test_device_without_session(aresponses: ResponsesMockServer) -> None:
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
    assert device
    assert device.signal_quality == 96
    assert device.firmware == "MW_08_512_0501_1.82"
    assert device.ip_address == "192.168.178.3"


async def test_inverter_js_devicearray(aresponses: ResponsesMockServer) -> None:
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
        assert inverter
        assert inverter.serial_number == "12345678910"
        assert inverter.firmware == "V4.08Build215"
        assert inverter.firmware_slave == "V4.12Build246"
        assert inverter.model == "Omnik1500tl"
        assert inverter.solar_rated_power is None
        assert inverter.solar_current_power == 850
        assert inverter.solar_energy_today == 2.32
        assert inverter.solar_energy_total == 5200.2


async def test_inverter_js_devicearray_sofar2200tl(
    aresponses: ResponsesMockServer,
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
        assert inverter
        assert inverter.serial_number == "1234567890"
        assert inverter.firmware == "V450"
        assert inverter.firmware_slave is None
        assert inverter.model == "SOFAR2200TL"
        assert inverter.solar_rated_power == 2000
        assert inverter.solar_current_power == 400
        assert inverter.solar_energy_today == 5.67
        assert inverter.solar_energy_total == 12307.0


async def test_device_js_devicearray(aresponses: ResponsesMockServer) -> None:
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
        assert device
        assert device.signal_quality == 39
        assert device.firmware == "H4.01.51MW.2.01W1.0.64(2018-01-251-D)"
        assert device.ip_address is None


async def test_inverter_json(aresponses: ResponsesMockServer) -> None:
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
        assert inverter
        assert inverter.serial_number is None
        assert inverter.firmware == "V1.25Build23261"
        assert inverter.firmware_slave == "V1.40Build52927"
        assert inverter.model == "omnik2000tl2"
        assert inverter.alarm_code == "F23"
        assert inverter.solar_rated_power == 2000
        assert inverter.solar_current_power == 1225
        assert inverter.solar_energy_today == 10.90
        assert inverter.solar_energy_total == 8674.0


async def test_device_json(aresponses: ResponsesMockServer) -> None:
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
        assert device
        assert device.signal_quality is None
        assert device.firmware == "ME-111001-V1.0.6(2015-10-16)"
        assert device.ip_address == "192.168.0.10"


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
