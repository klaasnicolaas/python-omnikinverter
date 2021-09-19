"""Models for Omnik Inverter."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .exceptions import OmnikInverterWrongSourceError, OmnikInverterWrongValuesError


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

        Raises:
            OmnikInverterWrongValuesError: Inverter pass on
                incorrect data (day and total are equal).
        """
        data = json.loads(data)

        def get_value(search):
            if data[search] != "":
                return data[search]
            return None

        def validation(data_list):
            """Check if the values are not equal to each other.

            Args:
                data_list: List of values to check.

            Returns:
                Boolean value.
            """
            res = all(ele == data_list[0] for ele in data_list)
            return res

        if validation([data["i_eday"], data["i_eall"]]):
            raise OmnikInverterWrongValuesError(
                "Inverter pass on incorrect data (day and total are equal)"
            )

        return Inverter(
            serial_number=get_value("i_sn"),
            model=get_value("i_modle"),
            firmware=get_value("i_ver_m"),
            firmware_slave=get_value("i_ver_s"),
            solar_rated_power=get_value("i_pow"),
            solar_current_power=int(get_value("i_pow_n")),
            solar_energy_today=float(get_value("i_eday")),
            solar_energy_total=float(get_value("i_eall")),
        )

    @staticmethod
    def from_js(data: dict[str, Any]) -> Inverter:
        """Return Inverter object from the Omnik Inverter response.

        Args:
            data: The JS (webscraping) data from the Omnik Inverter.

        Returns:
            An Inverter object.
        """

        def get_value(position):
            if data.find("webData") != -1:
                matches = re.search(r'(?<=webData=").*?(?=";)', data)
            else:
                matches = re.search(r'(?<=myDeviceArray\[0\]=").*?(?=";)', data)

            try:
                data_list = matches.group(0).split(",")
                if data_list[position] != "":
                    if position in [4, 5, 6, 7]:
                        if position in [4, 5]:
                            return int(data_list[position])

                        if position == 6:
                            energy_value = float(data_list[position]) / 100
                        if position == 7:
                            energy_value = float(data_list[position]) / 10
                        return energy_value
                    return data_list[position].replace(" ", "")
                return None
            except AttributeError as exception:
                raise OmnikInverterWrongSourceError(
                    "Your inverter has no data source from a javascript file."
                ) from exception

        return Inverter(
            serial_number=get_value(0),
            model=get_value(3),
            firmware=get_value(1),
            firmware_slave=get_value(2),
            solar_rated_power=get_value(4),
            solar_current_power=get_value(5),
            solar_energy_today=get_value(6),
            solar_energy_total=get_value(7),
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

        def get_value(value_type):
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
            signal_quality=get_value("signal"),
            firmware=get_value("version"),
            ip_address=get_value("ip"),
        )
