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
    firmware_main: str | None
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
            firmware_main=data["i_ver_m"],
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
                    return float(data_list[position]) / 100
                return data_list[position]
            except AttributeError as exception:
                raise OmnikInverterWrongSourceError(
                    "Your inverter has no data source from a javascript file."
                ) from exception

        return Inverter(
            serial_number=get_values(0),
            model=get_values(3),
            firmware_main=get_values(1),
            firmware_slave=get_values(2),
            solar_rated_power=get_values(4),
            solar_current_power=get_values(5),
            solar_energy_today=get_values(6),
            solar_energy_total=get_values(7),
        )
