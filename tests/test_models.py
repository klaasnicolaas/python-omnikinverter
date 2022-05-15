"""Test the models."""
import socket

import aiohttp
import asynctest
import pytest
from aresponses import ResponsesMockServer

from omnikinverter import Device, Inverter, OmnikInverter, tcp
from omnikinverter.exceptions import (
    OmnikInverterError,
    OmnikInverterPacketInvalidError,
    OmnikInverterWrongValuesError,
)

from . import load_fixture_bytes, load_fixtures


@pytest.mark.asyncio
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

    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(host="example.com", session=session)
        device: Device = await client.device()
        assert device
        assert device.signal_quality == 96
        assert device.firmware == "H4.01.38Y1.0.09W1.0.08"
        assert device.ip_address == "192.168.0.10"


@pytest.mark.asyncio
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

    client = OmnikInverter(  # noqa: S106
        host="example.com",
        source_type="html",
        username="klaas",
        password="supercool",
    )
    device: Device = await client.device()
    assert device
    assert device.signal_quality == 96
    assert device.firmware == "MW_08_512_0501_1.82"
    assert device.ip_address == "192.168.178.3"


@pytest.mark.asyncio
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

    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(host="example.com", session=session)
        device: Device = await client.device()
        assert device
        assert device.signal_quality == 39
        assert device.firmware == "H4.01.51MW.2.01W1.0.64(2018-01-251-D)"
        assert device.ip_address is None


@pytest.mark.asyncio
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

    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(host="example.com", source_type="json", session=session)
        device: Device = await client.device()
        assert device
        assert device.signal_quality is None
        assert device.firmware == "ME-111001-V1.0.6(2015-10-16)"
        assert device.ip_address == "192.168.0.10"


async def test_inverter_tcp_start_marker() -> None:
    """Require start marker."""

    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(1, bytearray(b"broken data"))

    assert str(excinfo.value) == "Invalid start byte"


async def test_inverter_tcp_data_too_short() -> None:
    """Require enough bytes available to satisfy length field."""

    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(1, bytearray([tcp.MESSAGE_START, 20]))

    assert (
        str(excinfo.value)
        == "Could only read 1 out of 32 expected bytes from TCP stream"
    )


async def test_inverter_tcp_checksum_correct() -> None:
    """Ensure the implementation validates CRC before accepting data."""

    serial_number = 1
    # Serial number, twice
    serial_number_bytes = list(serial_number.to_bytes(4, "little") * 2)

    test_message_contents = list(b"foo")
    test_message = (
        [
            len(test_message_contents),  # Length
            tcp.MESSAGE_RECV_SEP,
            tcp.MESSAGE_TYPE_STRING,
        ]
        + serial_number_bytes
        + test_message_contents
    )
    false_checksum = 0xFE
    checksum = sum(test_message) & 0xFF

    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(
            serial_number,
            bytearray(
                [tcp.MESSAGE_START]
                + list(test_message)
                + [false_checksum, tcp.MESSAGE_END]
            ),
        )

    assert (
        str(excinfo.value)
        == f"Checksum mismatch (calculated `{checksum}` got `{false_checksum}`)"
    )


async def test_inverter_tcp_recv_sep() -> None:
    """Require RECV_SEP "separator" between length and message_type."""

    serial_number = 1
    # Serial number, twice
    serial_number_bytes = list(serial_number.to_bytes(4, "little") * 2)

    test_message = [
        0,  # Length
        123,  # Invalid separator
        tcp.MESSAGE_TYPE_STRING,
    ] + serial_number_bytes
    checksum = sum(test_message) & 0xFF

    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(
            serial_number,
            bytearray(
                [tcp.MESSAGE_START] + list(test_message) + [checksum, tcp.MESSAGE_END]
            ),
        )

    assert str(excinfo.value) == "Invalid receiver separator"


async def test_inverter_tcp_double_serial_match() -> None:
    """Require both serial numbers in the received buffer to be identical."""

    test_message = (
        [
            0,  # Length
            tcp.MESSAGE_RECV_SEP,
            tcp.MESSAGE_TYPE_STRING,
        ]
        + list((1).to_bytes(4, "little"))
        + list((2).to_bytes(4, "little"))
    )
    checksum = sum(test_message) & 0xFF

    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(
            3,
            bytearray(
                [tcp.MESSAGE_START] + list(test_message) + [checksum, tcp.MESSAGE_END]
            ),
        )

    assert str(excinfo.value) == "Serial number mismatch in reply 1 != 2"


async def test_inverter_tcp_end_marker() -> None:
    """Require end marker."""

    serial_number = 1
    # Serial number, twice
    serial_number_bytes = list(serial_number.to_bytes(4, "little") * 2)

    test_message = [
        0,  # Length
        tcp.MESSAGE_RECV_SEP,
        tcp.MESSAGE_TYPE_STRING,
    ] + serial_number_bytes
    checksum = sum(test_message) & 0xFF

    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(
            serial_number,
            bytearray(
                [tcp.MESSAGE_START]
                + list(test_message)
                + [
                    checksum,
                    123,  # Invalid end byte
                ]
            ),
        )

    assert str(excinfo.value) == "Invalid end byte"


async def test_inverter_tcp_reply_identical_serial() -> None:
    """Require replied serial to be identical to the request."""

    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(1234, load_fixture_bytes("tcp_reply.data"))

    assert (
        str(excinfo.value)
        == "Replied serial number 987654321 not equal to request 1234"
    )


async def test_inverter_tcp_known_message_type() -> None:
    """Require message type to be known."""

    serial_number = 1
    # Serial number, twice
    serial_number_bytes = list(serial_number.to_bytes(4, "little") * 2)

    test_message = [
        0,  # Length
        tcp.MESSAGE_RECV_SEP,
        0,  # Unknown message type
    ] + serial_number_bytes
    checksum = sum(test_message) & 0xFF

    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(
            serial_number,
            bytearray(
                [tcp.MESSAGE_START] + list(test_message) + [checksum, tcp.MESSAGE_END]
            ),
        )

    assert (
        str(excinfo.value) == "Unknown Omnik message type 00 "
        "with contents `bytearray(b'')`"
    )


async def test_inverter_tcp_require_information_reply() -> None:
    """Require at least one of the messages to be an information reply."""

    serial_number = 1
    # Serial number, twice
    serial_number_bytes = list(serial_number.to_bytes(4, "little") * 2)

    test_message = [
        0,  # Length
        tcp.MESSAGE_RECV_SEP,
        tcp.MESSAGE_TYPE_STRING,
    ] + serial_number_bytes
    checksum = sum(test_message) & 0xFF

    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(
            serial_number,
            bytearray(
                [tcp.MESSAGE_START]
                + list(
                    test_message
                )  # Only contains a STRING message, no INFORMATION_REPLY
                + [checksum, tcp.MESSAGE_END]
            ),
        )

    assert str(excinfo.value) == "None of the messages contained an information reply!"


class TestTcpWithSocketMock(asynctest.TestCase):  # type: ignore
    """Test cases specific to the TCP backend."""

    async def test_inverter_tcp(self) -> None:
        """Test request from an Inverter - TCP source."""
        serial_number = 987654321
        socket_mock = asynctest.SocketMock()
        socket_mock.type = socket.SOCK_STREAM

        def send_side_effect(data: bytes) -> int:
            assert data == tcp.create_information_request(serial_number)
            asynctest.set_read_ready(socket_mock, self.loop)
            return len(data)

        def recv_side_effect(_max_bytes: int) -> bytes:
            return load_fixture_bytes("tcp_reply.data")

        socket_mock.send.side_effect = send_side_effect
        socket_mock.recv.side_effect = recv_side_effect

        client = OmnikInverter(
            host="example.com",
            source_type="tcp",
            serial_number=serial_number,
            _socket_mock=socket_mock,
        )

        inverter: Inverter = await client.inverter()

        assert inverter
        assert inverter.solar_rated_power is None
        assert inverter.solar_current_power == 2615

        assert inverter.model is None
        assert inverter.serial_number == "NLDN012345CS4321"
        assert inverter.temperature == 43.1
        assert inverter.dc_input_voltage == [187.3, 188.9, None]
        assert inverter.dc_input_current == [8.1, 7.800000000000001, None]
        assert inverter.ac_output_voltage == [239.60000000000002, None, None]
        assert inverter.ac_output_current == [10.8, None, None]
        assert inverter.ac_output_frequency == [50.06, None, None]
        assert inverter.ac_output_power == [2615.0, None, None]
        assert inverter.solar_energy_today == 7.4
        assert inverter.solar_energy_total == 65432.100000000006
        assert inverter.solar_hours_total == 54321
        assert inverter.inverter_active is True
        assert inverter.firmware == "NL1-V1.0-0077-4"
        assert inverter.firmware_slave == "V2.0-0024"

    async def test_connection_broken(self) -> None:
        """Test on connection broken after success - TCP source."""
        serial_number = 1
        socket_mock = asynctest.SocketMock()
        socket_mock.type = socket.SOCK_STREAM

        client = OmnikInverter(
            host="example.com",
            source_type="tcp",
            serial_number=serial_number,
            _socket_mock=socket_mock,
        )

        def send_side_effect(data: bytes) -> int:
            assert data == tcp.create_information_request(serial_number)
            asynctest.set_read_ready(socket_mock, self.loop)
            return len(data)

        socket_mock.send.side_effect = send_side_effect
        socket_mock.recv.side_effect = Exception("Connection broken")

        with pytest.raises(Exception) as excinfo:
            assert await client.inverter()

        assert str(excinfo.value) == "Connection broken"


async def test_connection_failed() -> None:
    """Test on failed connection attempt - TCP source."""
    serial_number = 1

    client = OmnikInverter(
        # Pass an invalid address to simulate a failed connection attempt
        host="!!!",
        source_type="tcp",
        serial_number=serial_number,
    )

    with pytest.raises(Exception) as excinfo:
        assert await client.inverter()

    assert (
        str(excinfo.value)
        == "Failed to open a TCP connection to the Omnik Inverter device"
    )


async def test_device_tcp_not_implemented() -> None:
    """Test request from a Device - TCP source."""
    serial_number = 123456

    client = OmnikInverter(
        host="example.com",
        source_type="tcp",
        serial_number=serial_number,
    )

    device: Device = await client.device()
    # No Device data can be extracted from TCP packets
    assert device.signal_quality is None
    assert device.firmware is None
    assert device.ip_address is None


@pytest.mark.asyncio
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

    async with aiohttp.ClientSession() as session:
        client = OmnikInverter(host="example.com", source_type="json", session=session)
        with pytest.raises(OmnikInverterWrongValuesError):
            assert await client.inverter()


@pytest.mark.asyncio
async def test_inverter_unknown_source_type() -> None:
    """Test exception on wrong source type."""
    client = OmnikInverter(host="example.com", source_type="blah")
    with pytest.raises(OmnikInverterError) as excinfo:
        assert await client.inverter()

    assert str(excinfo.value) == "Unknown source type `blah`"


@pytest.mark.asyncio
async def test_device_unknown_source_type() -> None:
    """Test exception on wrong source type."""
    client = OmnikInverter(host="example.com", source_type="blah")
    with pytest.raises(OmnikInverterError) as excinfo:
        assert await client.device()

    assert str(excinfo.value) == "Unknown source type `blah`"
