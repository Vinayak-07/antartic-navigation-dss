"""Numerical iceberg trajectory integration."""

from typing import Callable, Sequence

import numpy as np
from scipy.integrate import solve_ivp


def integrate_trajectory(initial_state: Sequence[float], duration_hours: float, derivative: Callable, **kwargs) -> np.ndarray:
    times = np.linspace(0.0, max(0.0, duration_hours) * 3600.0, max(2, int(duration_hours) + 1))
    result = solve_ivp(derivative, (times[0], times[-1]), list(initial_state), t_eval=times, method="RK45", **kwargs)
    return result.y.T
