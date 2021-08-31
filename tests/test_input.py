"""Test for retrieving information from the Omnik Inverter device."""
import aiohttp
import pytest

from omnikinverter import Inverter, OmnikInverter

from . import load_fixtures


@pytest.mark.asyncio
async def test_js_input(aresponses):
    """Test request from a JS input."""
    aresponses.add(
        "example.com",
        "/js/status.js",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/x-javascript"},
            text=load_fixtures("status.js"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        omnik = OmnikInverter(host="example.com", use_json=False, session=session)
        inverter: Inverter = await omnik.inverter()
        assert inverter
        assert inverter.firmware == "V5.3-00157"
        assert inverter.model == "omnik2000tl2"
        assert inverter.serial_number == "12345678910"
        assert inverter.solar_current_power == 1010
        assert inverter.solar_energy_today == 4.88
        assert inverter.solar_energy_total == 1053.19


@pytest.mark.asyncio
async def test_json_input(aresponses):
    """Test request from a JSON input."""
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
        assert inverter.firmware == "V1.25Build23261"
        assert inverter.model == "omnik2000tl2"
        assert inverter.serial_number == "12345678910"
        assert inverter.solar_current_power == 1225
        assert inverter.solar_energy_today == 10.90
        assert inverter.solar_energy_total == 8674.0
