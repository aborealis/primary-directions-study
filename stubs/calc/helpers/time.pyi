"""Stub of calc.helpers.time — local time handling."""

from datetime import datetime, timedelta

from calc.helpers.custom_types import ModernStyle, OldStyle

class LocalTime:
    """
    Functions and methods related to local time.
    In the case of old style (solar time), an OldStyle object is used
    as an argument. In the case of modern style, a ModernStyle object
    is used.

    For old style, the naive_datetime parameter represents wall clock
    time (when noon equals 12:00).

    For modern style, it represents solar time, when noon corresponds
    to the Sun's culmination.

    Some properties are defined as functions to be called only upon
    access, to save computational resources.
    """

    def __init__(self, time: ModernStyle | OldStyle) -> None: ...

    @property
    def julian_day(self) -> float:
        """
        Returns the Julian day in the specified calendar
        based on the given UTC datetime.
        """
        ...

    @property
    def gst(self) -> float:
        """
        Returns the Greenwich sidereal apparent time
        (local sidereal time at Greenwich).
        """
        ...

    @property
    def lst(self) -> float:
        """
        Returns the local sidereal time.
        Longitude in degrees is negative for western direction.
        """
        ...

    @property
    def equation_of_time(self) -> timedelta:
        """
        Returns the equation of time — the difference between
        local apparent (solar) time and local mean time
        (wall clock time).
        """
        ...

    def degree_to_hours(self, degree: float) -> str:
        """Converts any degree to HH:MM:SS format"""
        ...

    def datetime_from_jday_utc(self, jday_utc: float) -> datetime:
        """Returns the UTC datetime from the Julian day (also in UTC)"""
        ...


__all__ = ['LocalTime', 'ModernStyle', 'OldStyle']
