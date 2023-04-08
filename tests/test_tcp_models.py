"""Test the models from TCP source."""

from __future__ import annotations

import struct
from socket import SHUT_RDWR, SO_LINGER, SOL_SOCKET, socket
from threading import Thread
from typing import TYPE_CHECKING

import pytest

from omnikinverter import Device, Inverter, OmnikInverter, tcp
from omnikinverter.exceptions import (
    OmnikInverterAuthError,
    OmnikInverterConnectionError,
    OmnikInverterPacketInvalidError,
)

from . import load_fixture_bytes

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine


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


async def test_tcp_serial_number_unset() -> None:
    """Make sure exception is raised when serial_number is needed but not provided."""
    client = OmnikInverter(host="example.com", source_type="tcp")
    with pytest.raises(OmnikInverterAuthError) as excinfo:
        assert await client.tcp_request()

    assert str(excinfo.value) == "serial_number is missing from the request"


def tcp_server(
    serial_number: int,
    reply: str | Callable[[socket], None],
) -> tuple[Coroutine[None, None, None], int]:
    """Run a TCP socket server in a new thread, accepting a single connection."""
    # Create socket and generate random port
    sock = socket()
    sock.bind(("localhost", 0))
    (_, port) = sock.getsockname()
    sock.listen(1)

    def worker() -> None:
        """Accept a single connection and send predefined reply."""
        (conn, _) = sock.accept()

        data = conn.recv(1024)
        req = tcp.create_information_request(serial_number)
        assert data == req

        if isinstance(reply, str):
            conn.sendall(load_fixture_bytes(reply))
            conn.shutdown(SHUT_RDWR)
            conn.close()
        else:
            reply(conn)

        # Stop the server
        sock.close()

    thread = Thread(target=worker)
    thread.start()

    async def wait_for_server_thread() -> None:
        thread.join()

    return (wait_for_server_thread(), port)


async def test_inverter_tcp() -> None:
    """Test request from an Inverter - TCP source."""
    serial_number = 987654321

    (server_exit, port) = tcp_server(serial_number, "tcp_reply.data")

    client = OmnikInverter(
        host="localhost",
        source_type="tcp",
        serial_number=serial_number,
        tcp_port=port,
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

    await server_exit


async def test_inverter_tcp_offline() -> None:
    """Test request from an Inverter (offline) - TCP source."""
    serial_number = 1608449224

    (server_exit, port) = tcp_server(serial_number, "tcp_reply_offline.data")

    client = OmnikInverter(
        host="localhost",
        source_type="tcp",
        serial_number=serial_number,
        tcp_port=port,
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

    await server_exit


async def test_connection_broken() -> None:
    """Test closed connection after successful handshake - TCP source."""
    serial_number = 1

    def close_immediately(conn: socket) -> None:
        """Close the connection and send RST."""
        linger_on = 1
        linger_timeout = 0
        # Enabling linger with a timeout of 0 causes close() to abort the connection,
        # forcing "Connection reset by peer" on the client
        conn.setsockopt(
            SOL_SOCKET,
            SO_LINGER,
            struct.pack("ii", linger_on, linger_timeout),
        )
        conn.close()

    (server_exit, port) = tcp_server(serial_number, close_immediately)

    client = OmnikInverter(
        host="localhost",
        source_type="tcp",
        serial_number=serial_number,
        tcp_port=port,
    )

    with pytest.raises(OmnikInverterConnectionError) as excinfo:
        assert await client.inverter()

    assert (
        excinfo.value.args[0]
        == "Failed to communicate with the Omnik Inverter device over TCP"
    )

    await server_exit


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
