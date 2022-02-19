"""Data model and conversions for tcp-based communication with the Omnik Inverter."""
from ctypes import BigEndianStructure, c_char, c_ubyte, c_uint, c_ushort
from typing import Any, Optional

from .exceptions import OmnikInverterPacketInvalidError

MESSAGE_END = 0x16
MESSAGE_START = 0x68
UINT16_MAX = 65535


class _AcOutput(BigEndianStructure):
    _fields_ = [
        ("frequency", c_ushort),
        ("power", c_ushort),
    ]

    def get_power(self) -> Optional[int]:
        """Retrieve AC power.

        Returns:
            The power field, or None if it is unset.
        """
        return None if self.power == UINT16_MAX else self.power

    def get_frequency(self) -> Optional[float]:
        """Retrieve AC frequency.

        Returns:
            The frequency field in Hertz, or None if it is unset.
        """
        return None if self.frequency == UINT16_MAX else self.frequency * 0.01


class _TcpData(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        # Unlikely for all these bytes to represent the model,
        # this mapping has to be built out over time.
        ("model", c_char * 3),
        # The s/n from the request, twice, in little-endian
        ("double_serial_number", (c_ubyte * 4) * 2),
        ("padding0", c_char * 3),
        ("serial_number", c_char * 16),
        ("temperature", c_ushort),
        ("dc_input_voltage", c_ushort * 3),
        ("dc_input_current", c_ushort * 3),
        ("ac_output_current", c_ushort * 3),
        ("ac_output_voltage", c_ushort * 3),
        ("ac_output", _AcOutput * 3),
        ("solar_energy_today", c_ushort),
        ("solar_energy_total", c_uint),
        ("solar_hours_total", c_uint),
        ("inverter_active", c_ushort),
        ("padding1", c_ubyte * 4),
        ("unknown0", c_ushort),
        ("padding2", c_ubyte * 10),
        ("firmware", c_char * 16),
        ("padding3", c_ubyte * 4),
        ("firmware_slave", c_char * 16),
        ("padding4", c_ubyte * 4),
    ]


def _pack_message(message: bytearray) -> bytearray:
    checksum = sum(message) & 0xFF

    message.insert(0, MESSAGE_START)
    message.append(checksum)
    message.append(MESSAGE_END)

    return message


def _unpack_message(message: bytearray) -> bytearray:
    if message.pop(0) != MESSAGE_START:
        raise OmnikInverterPacketInvalidError("Invalid start byte")
    if message.pop() != MESSAGE_END:
        raise OmnikInverterPacketInvalidError("Invalid end byte")

    message_checksum = message.pop()
    checksum = sum(message) & 0xFF
    if message_checksum != checksum:
        raise OmnikInverterPacketInvalidError(
            f"Checksum mismatch (calculated `{checksum}` got `{message_checksum}`)"
        )

    return message


def create_information_request(serial_number: int) -> bytearray:
    """Compute a magic message to which the Omnik will reply with raw statistics.

    Args:
        serial_number: Integer with the serial number of your Omnik device.

    Returns:
        A bytearray with the raw message data, to be sent over a TCP socket.
    """
    request_data = bytearray([0x02, 0x40, 0x30])
    serial_bytes = serial_number.to_bytes(length=4, byteorder="little")
    request_data.extend(serial_bytes)
    request_data.extend(serial_bytes)
    request_data.extend([0x01, 0x00])
    return _pack_message(request_data)


def parse_information_reply(serial_number: int, data: bytes) -> dict[str, Any]:
    """Perform a raw TCP request to the Omnik device.

    Args:
        serial_number: Serial number passed to
            `clk.create_information_request()`, used to validate the reply.
        data: Raw data reply from the Omnik Inverter.

    Returns:
        A Python dictionary (text) with the response from
        the Omnik Inverter.

    Raises:
        OmnikInverterPacketInvalidError: Received data fails basic validity checks.
    """

    data = _unpack_message(bytearray(data))
    tcp_data = _TcpData.from_buffer_copy(data)

    if any(
        serial_number != int.from_bytes(b, byteorder="little")
        for b in tcp_data.double_serial_number
    ):
        raise OmnikInverterPacketInvalidError("Serial number mismatch in reply")

    if tcp_data.unknown0 != UINT16_MAX:  # pragma: no cover
        print(f"Unexpected unknown0 `{tcp_data.unknown0}`")

    if tcp_data.padding0 != b"\x81\x02\x01":  # pragma: no cover
        print(f"Unexpected padding0 `{tcp_data.padding0}`")

    # For all data that's expected to be zero, print it if it's not. Perhaps
    # there are more interesting fields on different inverters waiting to be
    # uncovered.
    for idx in range(1, 5):  # pragma: no cover
        name = f"padding{idx}"
        padding = getattr(tcp_data, name)
        if sum(padding):
            print(f"Unexpected `{name}`: `{padding}`")

    def extract_model(magic: bytes) -> str:
        return {
            b"\x7d\x41\xb0": "omnik3000tl",
            # http://www.mb200d.nl/wordpress/2015/11/omniksol-4k-tl-wifi-kit/#more-590:
            b"\x81\x41\xb0": "omnik4000tl",
            b"\x9a\x41\xb0": "omnik4000tl2",
        }.get(magic, f"Unknown device model from magic {magic!r}")

    def list_divide_10(integers: list[int]) -> list[Optional[float]]:
        return [None if v == UINT16_MAX else v * 0.1 for v in integers]

    def int_to_bool(num: int) -> bool:
        return {
            0: False,
            1: True,
        }[num]

    # Only these fields will be extracted from the structure
    field_extractors = {
        "model": extract_model,
        "serial_number": None,
        "temperature": 0.1,
        "dc_input_voltage": list_divide_10,
        "dc_input_current": list_divide_10,
        "ac_output_current": list_divide_10,
        "ac_output_voltage": list_divide_10,
        "ac_output": None,
        "solar_energy_today": 0.01,
        "solar_energy_total": 0.1,
        "solar_hours_total": None,
        "inverter_active": int_to_bool,
        "firmware": None,
        "firmware_slave": None,
    }

    result = {}

    for (name, extractor) in field_extractors.items():
        value = getattr(tcp_data, name)
        if name == "ac_output":
            # Flatten the list of frequency+power AC objects

            result["ac_output_frequency"] = [o.get_frequency() for o in value]
            result["ac_output_power"] = [o.get_power() for o in value]
            continue

        if isinstance(extractor, float):
            value *= extractor
        elif extractor is not None:
            value = extractor(value)
        elif isinstance(value, bytes):
            value = value.decode(encoding="utf-8")

        result[name] = value

    return result
