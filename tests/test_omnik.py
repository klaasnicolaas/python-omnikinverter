"""Test for retrieving information from the Omnik Inverter device."""
import asyncio

import aiohttp
import pytest

from omnikinverter import (
    Inverter,
    OmnikInverter,
    OmnikInverterConnectionError,
    OmnikInverterWrongSourceError,
)

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
        assert inverter.serial_number == "12345678910"
        assert inverter.firmware_main == "NL2-V9.8-5931"
        assert inverter.firmware_slave == "V5.3-00157"
        assert inverter.model == "omnik2000tl2"
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
        assert inverter.serial_number == "12345678910"
        assert inverter.firmware_slave == "V1.40Build52927"
        assert inverter.firmware_main == "V1.25Build23261"
        assert inverter.model == "omnik2000tl2"
        assert inverter.solar_current_power == 1225
        assert inverter.solar_energy_today == 10.90
        assert inverter.solar_energy_total == 8674.0


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
            text=load_fixtures("wrong_status.js"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        omnik = OmnikInverter(host="example.com", use_json=False, session=session)
        with pytest.raises(OmnikInverterWrongSourceError):
            assert await omnik.inverter()


@pytest.mark.asyncio
async def test_timeout(aresponses):
    """Test request timeout from Omnik Inverter."""
    # Faking a timeout by sleeping
    async def response_handler(_):
        await asyncio.sleep(0.2)
        return aresponses.Response(body="Goodmorning!", text=load_fixtures("status.js"))

    aresponses.add("example.com", "/js/status.js", "GET", response_handler)

    async with aiohttp.ClientSession() as session:
        omnik = OmnikInverter(host="example.com", use_json=False, session=session)
        with pytest.raises(OmnikInverterConnectionError):
            assert await omnik.inverter()
