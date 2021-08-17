"""Exceptions for Omnik Inverter."""


class OmnikInverterError(Exception):
    """Generic Omnik Inverter exception."""


class OmnikInverterConnectionError(OmnikInverterError):
    """Omnik Inverter connection exception."""
