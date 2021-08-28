"""Models for Omnik Inverter."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class Inverter:
    """Object representing an Inverter response from Omnik Inverter."""

    serial_number: str | None
    model: str | None
    firmware: str | None
    solar_current_power: int | None
    solar_energy_today: float | None
    solar_energy_total: float | None

    @staticmethod
    def from_js(data: dict[str, Any]) -> Inverter:
        """Return Inverter object from the Omnik Inverter response.

        Args:
            data: The data from the Omnik Inverter.

        Returns:
            An Inverter object.
        """

        def get_values(position):
            if data.find("webData") != -1:
                matches = re.search(r'(?<=webData=").*?(?=";)', data)
            else:
                matches = re.search(r'(?<=myDeviceArray\[0\]=").*?(?=";)', data)

            data_list = matches.group(0).split(",")
            if position in [6, 7]:
                return int(data_list[position]) / 100
            return data_list[position]

        return Inverter(
            serial_number=get_values(0),
            model=get_values(3),
            firmware=get_values(2),
            solar_current_power=get_values(5),
            solar_energy_today=get_values(6),
            solar_energy_total=get_values(7),
        )
