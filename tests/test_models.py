"""Test the models."""
import aiohttp
import pytest

from omnikinverter import Device, Inverter, OmnikInverter
from omnikinverter.exceptions import OmnikInverterWrongValuesError

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
        assert inverter.solar_rated_power is None
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
async def test_inverter_html(aresponses):
    """Test request from a Inverter - HTML source."""
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

    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(  # noqa: S106
            host="example.com",
            source_type="html",
            username="klaas",
            password="supercool",
            session=session,
        )
        inverter: Inverter = await client.inverter()
        assert inverter
        assert inverter.serial_number == "12345678910"
        assert inverter.firmware == "V5.07Build245"
        assert inverter.firmware_slave is None
        assert inverter.model == "Omnik2500tl"
        assert inverter.solar_rated_power == 2500
        assert inverter.solar_current_power == 219
        assert inverter.solar_energy_today == 0.23
        assert inverter.solar_energy_total == 6454.5


@pytest.mark.asyncio
async def test_device_html(aresponses):
    """Test request from a Inverter - HTML source."""
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

    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(  # noqa: S106
            host="example.com",
            source_type="html",
            username="klaas",
            password="supercool",
            session=session,
        )
        device: Device = await client.device()
        assert device
        assert device.signal_quality is None
        assert device.firmware == "ME_08_0102_2.03"
        assert device.ip_address == "192.168.0.106"


@pytest.mark.asyncio
async def test_inverter_html_solis(aresponses):
    """Test request from a Inverter - HTML source."""
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

    client = OmnikInverter(  # noqa: S106
        host="example.com",
        source_type="html",
        username="klaas",
        password="supercool",
    )
    inverter: Inverter = await client.inverter()
    assert inverter
    assert inverter.serial_number == "1234567890ABCDE"
    assert inverter.firmware == "001F"
    assert inverter.firmware_slave == "002F"
    assert inverter.model == "0079"
    assert inverter.solar_rated_power is None
    assert inverter.solar_current_power == 5850
    assert inverter.solar_energy_today == 9.80
    assert inverter.solar_energy_total == 44.0


@pytest.mark.asyncio
async def test_device_html_solis(aresponses):
    """Test request from a Inverter - HTML source."""
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

    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(  # noqa: S106
            host="example.com",
            source_type="html",
            username="klaas",
            password="supercool",
            session=session,
        )
        device: Device = await client.device()
        assert device
        assert device.signal_quality == 96
        assert device.firmware == "MW_08_512_0501_1.82"
        assert device.ip_address == "192.168.178.3"


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
        assert inverter.solar_rated_power is None
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
        assert device.ip_address is None


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
        client = OmnikInverter(host="example.com", source_type="json", session=session)
        inverter: Inverter = await client.inverter()
        assert inverter
        assert inverter.serial_number is None
        assert inverter.firmware == "V1.25Build23261"
        assert inverter.firmware_slave == "V1.40Build52927"
        assert inverter.model == "omnik2000tl2"
        assert inverter.solar_rated_power is None
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
        client = OmnikInverter(host="example.com", source_type="json", session=session)
        device: Device = await client.device()
        assert device
        assert device.signal_quality is None
        assert device.firmware == "ME-111001-V1.0.6(2015-10-16)"
        assert device.ip_address == "192.168.0.10"


@pytest.mark.asyncio
async def test_wrong_values(aresponses):
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

    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(host="example.com", source_type="json", session=session)
        with pytest.raises(OmnikInverterWrongValuesError):
            assert await client.inverter()
