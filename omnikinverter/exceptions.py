"""Exceptions for Omnik Inverter."""


class OmnikInverterError(Exception):
    """Generic Omnik Inverter exception."""


class OmnikInverterConnectionError(OmnikInverterError):
    """Omnik Inverter connection exception."""


class OmnikInverterWrongSourceError(OmnikInverterError):
    """Omnik Inverter wrong data source url exception."""


class OmnikInverterOfflineError(OmnikInverterError):
    """Omnik Inverter is powered by its own solar energy.

    No sun means no power and the inverter is off.
    When queried while off, this error will be raised.
    """
