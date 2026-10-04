"""Stub of calc.helpers.custom_types — vector and zodiacal data types."""

from collections.abc import Callable
from datetime import datetime
from typing import NamedTuple, TypedDict

class Equatorial:
    """Vector in the equatorial coordinate system"""

    rasc: float
    dec: float

    def __init__(self, rasc: float, dec: float) -> None: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def aslist(self) -> list[float]: ...


class Horizontal:
    """Vector in the horizontal coordinate system"""

    azm: float
    alt: float

    def __init__(self, azm: float, alt: float) -> None: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def aslist(self) -> list[float]: ...


class Ecliptical:
    """Vector in the ecliptical coordinate system"""

    lon: float
    lat: float

    def __init__(self, lon: float, lat: float) -> None: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def aslist(self) -> list[float]: ...


class Cartesian:
    """Cartesian coordinates"""

    def __init__(self, x: float, y: float, z: float) -> None: ...
    def __str__(self) -> str: ...
    def aslist(self) -> list[float]: ...


class DataForVectorInit(NamedTuple):
    """Structured dataset for initializing a vector object"""

    coords_equatorial: Equatorial
    method_ecliptical: Callable[[], Ecliptical]
    method_horizontal: Callable[[], Horizontal]
    to_xyz: Callable[[float, float], Cartesian]
    method_obl_asc: Callable[[float, float], float | None]
    method_asc_diff: Callable[[float], float | None]
    method_umd: Callable[[float], float]
    method_dsa: Callable[[float], float | None]


class Vector:
    """
    When a vector is initialized on the celestial sphere, an instance
    of this class is returned. All its properties are defined as
    functions — they are computed only upon explicit access, not at
    initialization. This saves computational resources.
    """

    def __init__(self, data_for_vector: DataForVectorInit) -> None: ...

    # ---------------------
    # Coordinates
    # ---------------------
    @property
    def equatorial(self) -> Equatorial: ...
    @property
    def ecliptical(self) -> Ecliptical: ...
    @property
    def horizontal(self) -> Horizontal: ...
    @property
    def equatorial_xyz(self) -> Cartesian: ...
    @property
    def ecliptical_xyz(self) -> Cartesian: ...
    @property
    def horizontal_xyz(self) -> Cartesian: ...

    # ---------------------
    # Ascensions & meridian
    # ---------------------
    @property
    def obl_asc(self) -> float | None: ...
    @property
    def asc_diff(self) -> float | None: ...
    @property
    def umd(self) -> float: ...
    @property
    def dsa(self) -> float | None: ...

    # ---------------------
    # String representations
    # ---------------------
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...


class Speed:
    """Planet speed"""

    def __init__(self,
                 planet: int,
                 speed_in_lon: float,
                 speed_in_lat: float) -> None: ...
    def __str__(self) -> str: ...


class Planet(NamedTuple):
    """Zodiacal coordinates of a planet"""

    name: str
    vector: Vector
    speed: Speed

    def __repr__(self) -> str: ...


class StellarObject(NamedTuple):
    """
    Zodiacal data for cusps, stars, nodes, antiscia, and planetary aspects.
    """

    name: str | int
    vector: Vector

    def __repr__(self) -> str: ...


class ModernStyle(NamedTuple):
    """Representation of date and time in modern style"""

    naive_datetime: datetime   # Wall clock time
    time_zone_hrs: float       # Time zone in hours
    geo_lon: float             # Geographic longitude; negative for west
    is_gregorian: bool = True  # Calendar type


class OldStyle(NamedTuple):
    """Representation of date and time in old style"""

    naive_datetime: datetime   # Solar time (local apparent time)
    geo_lon: float             # Geographic longitude; negative for west
    is_gregorian: bool = True  # Calendar type
    # LMT (Local Mean Time) or LAT (Local Apparent Time)
    is_lat: bool = True


class DirectionArcDict(TypedDict):
    """Type annotation for direction arc dictionary"""

    arc: float
    type: str  # 'D' for direct and 'C' for converse
