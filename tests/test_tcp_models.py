"""Test the models from TCP source."""
import socket

import asynctest
import pytest

from omnikinverter import Device, Inverter, OmnikInverter, tcp
from omnikinverter.exceptions import (
    OmnikInverterConnectionError,
    OmnikInverterPacketInvalidError,
)

from . import load_fixture_bytes


async def test_inverter_tcp_start_marker() -> None:
    """Require start marker."""
    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(1, bytearray(b"broken data"))

    assert str(excinfo.value) == "Invalid start byte: 98"


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
    serial_number_bytes = serial_number.to_bytes(4, "little") * 2

    test_message_contents = b"foo"
    test_message = [
        len(test_message_contents),  # Length
        tcp.MESSAGE_RECV_SEP,
        tcp.MESSAGE_TYPE_STRING,
        *serial_number_bytes,
        *test_message_contents,
    ]
    false_checksum = 0xFE
    checksum = sum(test_message) & 0xFF

    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(
            serial_number,
            bytearray(
                [
                    tcp.MESSAGE_START,
                    *test_message,
                    false_checksum,
                    tcp.MESSAGE_END,
                ],
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
    serial_number_bytes = serial_number.to_bytes(4, "little") * 2

    test_message = [
        0,  # Length
        123,  # Invalid separator
        tcp.MESSAGE_TYPE_STRING,
        *serial_number_bytes,
    ]
    checksum = sum(test_message) & 0xFF

    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(
            serial_number,
            bytearray(
                [tcp.MESSAGE_START, *test_message, checksum, tcp.MESSAGE_END],
            ),
        )

    assert str(excinfo.value) == "Invalid receiver separator"


async def test_inverter_tcp_double_serial_match() -> None:
    """Require both serial numbers in the received buffer to be identical."""
    test_message = [
        0,  # Length
        tcp.MESSAGE_RECV_SEP,
        tcp.MESSAGE_TYPE_STRING,
        *(1).to_bytes(4, "little"),
        *(2).to_bytes(4, "little"),
    ]
    checksum = sum(test_message) & 0xFF

    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(
            3,
            bytearray(
                [tcp.MESSAGE_START, *test_message, checksum, tcp.MESSAGE_END],
            ),
        )

    assert str(excinfo.value) == "Serial number mismatch in reply 1 != 2"


async def test_inverter_tcp_end_marker() -> None:
    """Require end marker."""
    serial_number = 1
    # Serial number, twice
    serial_number_bytes = serial_number.to_bytes(4, "little") * 2

    test_message = [
        0,  # Length
        tcp.MESSAGE_RECV_SEP,
        tcp.MESSAGE_TYPE_STRING,
        *serial_number_bytes,
    ]
    checksum = sum(test_message) & 0xFF

    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(
            serial_number,
            bytearray(
                [
                    tcp.MESSAGE_START,
                    *test_message,
                    checksum,
                    123,  # Invalid end byte
                ],
            ),
        )

    assert str(excinfo.value) == "Invalid end byte"


async def test_inverter_tcp_known_message_type() -> None:
    """Require message type to be known."""
    serial_number = 1
    # Serial number, twice
    serial_number_bytes = serial_number.to_bytes(4, "little") * 2

    test_message = [
        0,  # Length
        tcp.MESSAGE_RECV_SEP,
        0,  # Unknown message type
        *serial_number_bytes,
    ]
    checksum = sum(test_message) & 0xFF

    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(
            serial_number,
            bytearray(
                [tcp.MESSAGE_START, *test_message, checksum, tcp.MESSAGE_END],
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
    serial_number_bytes = serial_number.to_bytes(4, "little") * 2

    test_message = [
        0,  # Length
        tcp.MESSAGE_RECV_SEP,
        tcp.MESSAGE_TYPE_STRING,  # Only provide a STRING message
        *serial_number_bytes,
    ]
    checksum = sum(test_message) & 0xFF

    with pytest.raises(OmnikInverterPacketInvalidError) as excinfo:
        assert tcp.parse_messages(
            serial_number,
            bytearray(
                [
                    tcp.MESSAGE_START,
                    *test_message,
                    checksum,
                    tcp.MESSAGE_END,
                ],
            ),
        )

    assert str(excinfo.value) == "None of the messages contained an information reply!"


class TestTcpWithSocketMock(asynctest.TestCase):  # type: ignore  # noqa
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

    async def test_inverter_tcp_offline(self) -> None:
        """Test request from an Inverter (offline) - TCP source."""
        serial_number = 1608449224
        socket_mock = asynctest.SocketMock()
        socket_mock.type = socket.SOCK_STREAM

        def send_side_effect(data: bytes) -> int:
            assert data == tcp.create_information_request(serial_number)
            asynctest.set_read_ready(socket_mock, self.loop)
            return len(data)

        def recv_side_effect(_max_bytes: int) -> bytes:
            return load_fixture_bytes("tcp_reply_offline.data")

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
        assert inverter.solar_current_power == 0

        assert inverter.model is None
        assert inverter.serial_number == "NLBN4020157P9024"
        assert inverter.temperature is None
        assert inverter.dc_input_voltage == [0.0, 0.0, 0.0]
        assert inverter.dc_input_current == [0.0, 0.0, 0.0]
        assert inverter.ac_output_voltage == [0.0, 0.0, 0.0]
        assert inverter.ac_output_current == [0.0, 0.0, 0.0]
        assert inverter.ac_output_frequency == [0.0, 0.0, 0.0]
        assert inverter.ac_output_power == [0.0, 0.0, 0.0]
        assert inverter.solar_energy_today == 4.7
        assert inverter.solar_energy_total == 15818.0
        assert inverter.solar_hours_total == 0
        assert inverter.inverter_active is False
        assert not inverter.firmware
        assert not inverter.firmware_slave

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
        socket_mock.recv.side_effect = OSError("Connection broken")

        with pytest.raises(OmnikInverterConnectionError) as excinfo:
            assert await client.inverter()

        assert (
            str(excinfo.value)
            == "Failed to communicate with the Omnik Inverter device over TCP"
        )


async def test_connection_failed() -> None:
    """Test on failed connection attempt - TCP source."""
    serial_number = 1

    client = OmnikInverter(
        # Pass an invalid address to simulate a failed connection attempt
        host="!!!",
        source_type="tcp",
        serial_number=serial_number,
    )

    with pytest.raises(OmnikInverterConnectionError) as excinfo:
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
