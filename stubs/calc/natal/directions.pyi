"""Stub of calc.natal.directions — natal directions and mundane positions."""


from calc.helpers.custom_types import DirectionArcDict, StellarObject, Vector
from calc.sphere import Sphere

def mund_antis_by_name(sphere: Sphere,
                       planet_num: int,
                       is_closest: bool) -> Vector | None:
    """
    Returns the closest (is_closest = True) or the farthest mundane
    antiscion of the planet with the given number 0..6
    """
    ...


def aspects_on_circle(sphere: Sphere,
                      planet_num: int
                      ) -> list[StellarObject]:
    """Returns the aspects on the circle of aspects for the given planet"""
    ...


def mundpos_regio(sphere: Sphere, vector: Vector) -> float:
    """
    Returns the oblique ascension of the given vector on its own
    circle of positions (the mundane position of the vector)
    """
    ...


def directions_regio(sphere: Sphere,
                     promittor: Vector,
                     significator: Vector) -> DirectionArcDict | None:
    """
    Finds the directional arc between the promittor (P) and the
    significator (S). If S precedes P, returns the arc from P to the
    circle of positions of S; otherwise returns the arc from S to the
    circle of positions of P (a converse direction).
    """
    ...
