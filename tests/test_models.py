"""Test the models."""
import aiohttp
import pytest

from omnikinverter import Inverter, OmnikInverter

from . import load_fixtures


@pytest.mark.asyncio
async def test_js_webdata(aresponses):
    """Test request from a JS Webdata source."""
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
        omnik = OmnikInverter(host="example.com", session=session)
        inverter: Inverter = await omnik.inverter()
        assert inverter
        assert inverter.serial_number == "12345678910"
        assert inverter.firmware_main == "NL2-V9.8-5931"
        assert inverter.firmware_slave == "V5.3-00157"
        assert inverter.model == "omnik2000tl2"
        assert inverter.solar_current_power == 1010
        assert inverter.solar_energy_today == 4.88
        assert inverter.solar_energy_total == 10531.9


@pytest.mark.asyncio
async def test_js_devicearray(aresponses):
    """Test request from a JS DeviceArray source."""
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
        omnik = OmnikInverter(host="example.com", session=session)
        inverter: Inverter = await omnik.inverter()
        assert inverter
        assert inverter.serial_number == "12345678910"
        assert inverter.firmware_main == "V4.08Build215"
        assert inverter.firmware_slave == "V4.12Build246"
        assert inverter.model == "Omnik1500tl"
        assert inverter.solar_current_power == 850
        assert inverter.solar_energy_today == 2.32
        assert inverter.solar_energy_total == 5200.2


@pytest.mark.asyncio
async def test_json(aresponses):
    """Test request from a JSON source."""
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
        assert inverter.firmware_slave == "V1.40Build52927"
        assert inverter.firmware_main == "V1.25Build23261"
        assert inverter.model == "omnik2000tl2"
        assert inverter.solar_current_power == 1225
        assert inverter.solar_energy_today == 10.90
        assert inverter.solar_energy_total == 8674.0
