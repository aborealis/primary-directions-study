"""
Typed dictionaries annotating the runtime data structures of the
simplified astrological model.

Requires the proprietary ``calc`` computation engine, which is not
distributed with this repository; without it this module cannot be used.
"""
from typing import TypedDict

# Real runtime import: with the proprietary calc package present it
# provides the actual Vector type; static type checking uses the
# stubs under stubs/calc/ instead.
from calc.helpers.custom_types import Vector


class PromissorDict(TypedDict):
    """Type annotation for promissor dictionary"""
    object: str
    vector: Vector
    score: int


class SignificatorDict(TypedDict):
    """Type annotation for significator dictionary"""
    object: str
    vector: Vector


class DirectionDict(TypedDict):
    """Type annotation for direction dictionary"""
    sign: str  # significator's name
    prom: str  # promissor's name
    year: float
    date: str  # in 'YYYY/MM/DD' format


class DirectionArcDict(TypedDict):
    """Type annotation for direction arc dictionary"""
    arc: float
    type: str  # 'D' for direct and 'C' for converse
