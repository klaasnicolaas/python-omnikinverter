"""Test the models."""
import aiohttp
import pytest

from omnikinverter import Device, Inverter, OmnikInverter

from . import load_fixtures


@pytest.mark.asyncio
async def test_inverter_js_webdata(aresponses):
    """Test request from a Inverter - JS Webdata source."""
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

    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(host="example.com", session=session)
        inverter: Inverter = await client.inverter()
        assert inverter
        assert inverter.serial_number == "12345678910"
        assert inverter.firmware == "NL2-V9.8-5931"
        assert inverter.firmware_slave == "V5.3-00157"
        assert inverter.model == "omnik2000tl2"
        assert inverter.solar_current_power == 1010
        assert inverter.solar_energy_today == 4.88
        assert inverter.solar_energy_total == 10531.9


@pytest.mark.asyncio
async def test_device_js_webdata(aresponses):
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

    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(host="example.com", session=session)
        device: Device = await client.device()
        assert device
        assert device.signal_quality == 96
        assert device.firmware == "H4.01.38Y1.0.09W1.0.08"
        assert device.ip_address == "192.168.0.10"


@pytest.mark.asyncio
async def test_inverter_js_devicearray(aresponses):
    """Test request from a Inverter - JS DeviceArray source."""
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

    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(host="example.com", session=session)
        inverter: Inverter = await client.inverter()
        assert inverter
        assert inverter.serial_number == "12345678910"
        assert inverter.firmware == "V4.08Build215"
        assert inverter.firmware_slave == "V4.12Build246"
        assert inverter.model == "Omnik1500tl"
        assert inverter.solar_current_power == 850
        assert inverter.solar_energy_today == 2.32
        assert inverter.solar_energy_total == 5200.2


@pytest.mark.asyncio
async def test_device_js_devicearray(aresponses):
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

    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(host="example.com", session=session)
        device: Device = await client.device()
        assert device
        assert device.signal_quality == 39
        assert device.firmware == "H4.01.51MW.2.01W1.0.64(2018-01-251-D)"
        assert device.ip_address == "192.168.0.10"


@pytest.mark.asyncio
async def test_inverter_json(aresponses):
    """Test request from a Inverter - JSON source."""
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

    async with aiohttp.ClientSession() as session:
        omnik = OmnikInverter(host="example.com", use_json=True, session=session)
        inverter: Inverter = await omnik.inverter()
        assert inverter
        assert inverter.serial_number == "12345678910"
        assert inverter.firmware == "V1.25Build23261"
        assert inverter.firmware_slave == "V1.40Build52927"
        assert inverter.model == "omnik2000tl2"
        assert inverter.solar_current_power == 1225
        assert inverter.solar_energy_today == 10.90
        assert inverter.solar_energy_total == 8674.0


@pytest.mark.asyncio
async def test_device_json(aresponses):
    """Test request from a Inverter - JSON source."""
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

    async with aiohttp.ClientSession() as session:
        omnik = OmnikInverter(host="example.com", use_json=True, session=session)
        device: Device = await omnik.device()
        assert device
        assert device.signal_quality is None
        assert device.firmware == "ME-111001-V1.0.6(2015-10-16)"
        assert device.ip_address == "192.168.0.10"
