"""Exceptions for Omnik Inverter."""


class OmnikInverterError(Exception):
    """Generic Omnik Inverter exception."""


class OmnikInverterAuthError(OmnikInverterError):
    """Omnik Inverter Authentication exception."""


class OmnikInverterConnectionError(OmnikInverterError):
    """Omnik Inverter connection exception."""


class OmnikInverterWrongSourceError(OmnikInverterError):
    """Omnik Inverter wrong data source url exception."""


class OmnikInverterWrongValuesError(OmnikInverterError):
    """Omnik Inverter gives wrong values.

    This error appears when your inverter
    shows the same value for both day and
    total production.
    """
