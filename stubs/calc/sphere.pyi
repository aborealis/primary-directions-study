"""Stub of calc.sphere — class of the celestial sphere."""


from calc.helpers.custom_types import Planet, StellarObject, Vector
from calc.helpers.time import LocalTime

class Sphere:
    """Type annotation for class of celestial sphere"""
    localtime: LocalTime
    julian_day: float
    ramc: float
    lst: float

    def __init__(self, localtime: LocalTime, geo_lat: float) -> None: ...

    # ---------------------
    # Coordinate transformations
    # ---------------------
    def set_equatorial(self, rasc: float, dec: float) -> Vector: ...
    def set_ecliptical(self, lon: float, lat: float) -> Vector: ...
    def set_horizontal(self, azm: float, alt: float) -> Vector: ...

    def asc_diff(self,
                 dec: float,
                 pole: float | None = None) -> float | None: ...

    def obl_asc(self,
                rasc: float,
                dec: float,
                pole: float | None = None) -> float | None: ...

    def umd(self, rasc: float) -> float: ...
    def dsa(self, dec: float) -> float | None: ...

    # ---------------------
    # Main properties of the sphere
    # ---------------------
    @property
    def asc(self) -> float: ...
    @property
    def mc(self) -> float: ...
    @property
    def is_night(self) -> bool: ...

    # ---------------------
    # House cusps
    # ---------------------
    @property
    def cusps_placidus(self) -> list[StellarObject]: ...
    @property
    def cusps_regio(self) -> list[StellarObject]: ...
    def cusp_placidus(self, num: int) -> list[Vector]: ...
    def regiomontanus_cusp(self, num: int) -> list[Vector]: ...

    # ---------------------
    # Planets and nodes
    # ---------------------
    @property
    def planets(self) -> list[Planet]: ...
    def planet(self, name: str) -> Planet | None: ...
    @property
    def true_nodes(self) -> list[StellarObject]: ...

    # ---------------------
    # Fixed stars
    # ---------------------
    @property
    def stars_horary(self) -> list[StellarObject]: ...
    @property
    def stars_royal(self) -> list[StellarObject]: ...
