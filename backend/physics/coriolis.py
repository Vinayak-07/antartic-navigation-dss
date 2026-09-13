"""Latitude-dependent Coriolis helpers."""

import math


def coriolis_parameter(latitude: float, angular_velocity: float = 7.2921159e-5) -> float:
    return 2.0 * angular_velocity * math.sin(math.radians(latitude))
