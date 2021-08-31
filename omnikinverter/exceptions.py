"""Exceptions for Omnik Inverter."""


class OmnikInverterError(Exception):
    """Generic Omnik Inverter exception."""


class OmnikInverterConnectionError(OmnikInverterError):
    """Omnik Inverter connection exception."""


class OmnikInverterWrongSourceError(OmnikInverterError):
    """Omnik Inverter wrong data source url exception."""
