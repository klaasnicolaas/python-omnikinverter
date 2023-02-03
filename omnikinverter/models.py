"""Models for Omnik Inverter."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, cast

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
    alarm_code: str | None = None

    # TCP only
    inverter_active: bool | None = None
    solar_hours_total: int | None = None

    temperature: float | None = None

    dc_input_voltage: list[float] | None = None
    dc_input_current: list[float] | None = None

    ac_output_voltage: list[float] | None = None
    ac_output_current: list[float] | None = None
    ac_output_frequency: list[float] | None = None
    ac_output_power: list[float] | None = None

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

        def get_value(search: str) -> Any:
            if data[search] != "":
                return data[search]
            return None

        def validation(data_list: list[Any]) -> bool:
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
            alarm_code=get_value("i_alarm"),
            solar_rated_power=int(get_value("i_pow")),
            solar_current_power=int(get_value("i_pow_n")),
            solar_energy_today=float(get_value("i_eday")),
            solar_energy_total=float(get_value("i_eall")),
        )

    @staticmethod
    def from_html(data: str) -> Inverter:
        """Return Inverter object from the Omnik Inverter response.

        Args:
            data: The HTML (webscraping) data from the Omnik Inverter.

        Returns:
            An Inverter object.
        """

        def get_value(search_key: str) -> Any:
            try:
                match = cast(
                    re.Match[str],
                    re.search(f'(?<={search_key}=").*?(?=";)', data.replace(" ", "")),
                ).group(0)
                if match != "":
                    if search_key in ["webdata_now_p", "webdata_rate_p"]:
                        return int(match)
                    if search_key in ["webdata_today_e", "webdata_total_e"]:
                        return float(match)
                    return match
                return None
            except AttributeError as exception:
                raise OmnikInverterWrongSourceError(
                    "Your inverter has no data source from a html file."
                ) from exception

        return Inverter(
            serial_number=get_value("webdata_sn"),
            model=get_value("webdata_pv_type"),
            firmware=get_value("webdata_msvn"),
            firmware_slave=get_value("webdata_ssvn"),
            alarm_code=get_value("webdata_alarm"),
            solar_rated_power=get_value("webdata_rate_p"),
            solar_current_power=get_value("webdata_now_p"),
            solar_energy_today=get_value("webdata_today_e"),
            solar_energy_total=get_value("webdata_total_e"),
        )

    @staticmethod
    def from_js(data: str) -> Inverter:
        """Return Inverter object from the Omnik Inverter response.

        Args:
            data: The JS (webscraping) data from the Omnik Inverter.

        Returns:
            An Inverter object.
        """

        def get_value(position: int) -> Any:
            try:
                if data.find("webData") != -1:
                    matches = (
                        cast(re.Match[str], re.search(r'(?<=webData=").*?(?=";)', data))
                        .group(0)
                        .split(",")
                    )
                else:
                    matches = (
                        cast(
                            re.Match[str],
                            re.search(r'(?<=myDeviceArray\[0\]=").*?(?=";)', data),
                        )
                        .group(0)
                        .split(",")
                    )

                if matches[position] != "":
                    if position in [4, 5, 6, 7]:
                        if position in [4, 5]:
                            return int(matches[position].replace(" ", ""))

                        if position == 6:
                            energy_value = float(matches[position]) / 100
                        if position == 7:
                            energy_value = float(matches[position]) / 10
                        return energy_value
                    return matches[position].replace(" ", "")
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
            alarm_code=get_value(8),
            solar_rated_power=get_value(4),
            solar_current_power=get_value(5),
            solar_energy_today=get_value(6),
            solar_energy_total=get_value(7),
        )

    @staticmethod
    def from_tcp(data: dict[str, Any]) -> Inverter:
        """Return Inverter object from the Omnik Inverter response.

        Args:
            data: The binary data from the Omnik Inverter.

        Returns:
            An Inverter object.
        """

        return Inverter(
            **data,
            model=None,  # Not able to deduce this from raw message yet
            solar_rated_power=None,
            solar_current_power=sum(
                p for p in data["ac_output_power"] if p is not None
            ),
        )


@dataclass
class Device:
    """Object representing an Device response from Omnik Inverter."""

    signal_quality: int | None = None
    firmware: str | None = None
    ip_address: str | None = None

    @staticmethod
    def from_json(data: dict[str, Any]) -> Device:
        """Return Device object from the Omnik Inverter response.

        Args:
            data: The JSON data from the Omnik Inverter.

        Returns:
            An Device object.
        """
        return Device(
            signal_quality=None,
            firmware=data["g_ver"].replace("VER:", ""),
            ip_address=data["ip"],
        )

    @staticmethod
    def from_html(data: str) -> Device:
        """Return Device object from the Omnik Inverter response.

        Args:
            data: The HTML (webscraping) data from the Omnik Inverter.

        Returns:
            An Device object.
        """

        for correction in [" ", "%"]:
            data = data.replace(correction, "")

        def get_value(search_key: str) -> Any:
            match = cast(
                re.Match[str], re.search(f'(?<={search_key}=").*?(?=";)', data)
            ).group(0)

            if match != "":
                if search_key in ["cover_sta_rssi"]:
                    return int(match)
                return match
            return None

        return Device(
            signal_quality=get_value("cover_sta_rssi"),
            firmware=get_value("cover_ver"),
            ip_address=get_value("cover_sta_ip"),
        )

    @staticmethod
    def from_js(data: str) -> Device:
        """Return Device object from the Omnik Inverter response.

        Args:
            data: The JS (webscraping) data from the Omnik Inverter.

        Returns:
            An Device object.
        """
        for correction in [" ", "%"]:
            data = data.replace(correction, "")

        def get_value(search_key: str) -> Any:
            match = cast(
                re.Match[str], re.search(f'(?<={search_key}=").*?(?=";)', data)
            ).group(0)

            if match != "":
                if search_key == "m2mRssi":
                    return int(match)
                return match
            return None

        return Device(
            signal_quality=get_value("m2mRssi"),
            firmware=get_value("version"),
            ip_address=get_value("wanIp"),
        )
