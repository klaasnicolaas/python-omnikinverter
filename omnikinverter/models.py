"""Models for Omnik Inverter."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .exceptions import OmnikInverterWrongSourceError


@dataclass
class Inverter:
    """Object representing an Inverter response from Omnik Inverter."""

    serial_number: str | None
    model: str | None
    firmware: str | None
    firmware_slave: str | None
    solar_rated_power: int | None
    solar_current_power: int | None
    solar_energy_today: float | None
    solar_energy_total: float | None

    @staticmethod
    def from_json(data: dict[str, Any]) -> Inverter:
        """Return Inverter object from the Omnik Inverter response.

        Args:
            data: The JSON data from the Omnik Inverter.

        Returns:
            An Inverter object.
        """

        data = json.loads(data)
        return Inverter(
            serial_number=data["i_sn"],
            model=data["i_modle"],
            firmware=data["i_ver_m"],
            firmware_slave=data["i_ver_s"],
            solar_rated_power=data["i_pow"],
            solar_current_power=int(data["i_pow_n"]),
            solar_energy_today=float(data["i_eday"]),
            solar_energy_total=float(data["i_eall"]),
        )

    @staticmethod
    def from_js(data: dict[str, Any]) -> Inverter:
        """Return Inverter object from the Omnik Inverter response.

        Args:
            data: The JS (webscraping) data from the Omnik Inverter.

        Returns:
            An Inverter object.
        """

        def get_values(position):
            if data.find("webData") != -1:
                matches = re.search(r'(?<=webData=").*?(?=";)', data)
            else:
                matches = re.search(r'(?<=myDeviceArray\[0\]=").*?(?=";)', data)

            try:
                data_list = matches.group(0).split(",")
                if position in [4, 5, 6, 7]:
                    if position in [4, 5]:
                        return int(data_list[position])

                    if position == 6:
                        energy_value = float(data_list[position]) / 100
                    if position == 7:
                        energy_value = float(data_list[position]) / 10
                    return energy_value

                return data_list[position].replace(" ", "")
            except AttributeError as exception:
                raise OmnikInverterWrongSourceError(
                    "Your inverter has no data source from a javascript file."
                ) from exception

        return Inverter(
            serial_number=get_values(0),
            model=get_values(3),
            firmware=get_values(1),
            firmware_slave=get_values(2),
            solar_rated_power=get_values(4),
            solar_current_power=get_values(5),
            solar_energy_today=get_values(6),
            solar_energy_total=get_values(7),
        )


@dataclass
class Device:
    """Object representing an Device response from Omnik Inverter."""

    signal_quality: int | None
    firmware: str | None
    ip_address: str | None

    @staticmethod
    def from_json(data: dict[str, Any]) -> Device:
        """Return Device object from the Omnik Inverter response.

        Args:
            data: The JSON data from the Omnik Inverter.

        Returns:
            An Device object.
        """

        data = json.loads(data)
        return Device(
            signal_quality=None,
            firmware=data["g_ver"].replace("VER:", ""),
            ip_address=data["ip"],
        )

    @staticmethod
    def from_js(data: dict[str, Any]) -> Device:
        """Return Device object from the Omnik Inverter response.

        Args:
            data: The JS (webscraping) data from the Omnik Inverter.

        Returns:
            An Device object.
        """

        def get_values(value_type):
            if value_type == "ip" and data.find("wanIp") != -1:
                match = re.search(r'(?<=wanIp=").*?(?=";)', data.replace(" ", ""))
                value = match.group(0)
            if value_type == "signal" and data.find("m2mRssi") != -1:
                match = re.search(r'(?<=m2mRssi=").*?(?=";)', data.replace(" ", ""))
                value = match.group(0).replace("%", "")
                return int(value)
            if value_type == "version" and data.find("version") != -1:
                match = re.search(r'(?<=version=").*?(?=";)', data.replace(" ", ""))
                value = match.group(0)
            return value

        return Device(
            signal_quality=get_values("signal"),
            firmware=get_values("version"),
            ip_address=get_values("ip"),
        )
