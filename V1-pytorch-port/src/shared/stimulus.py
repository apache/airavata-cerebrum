"""Framework-agnostic stimulus generation (numpy-based)."""
from __future__ import annotations
import numpy as np


def generate_step_current(
    n_neurons: int,
    n_timesteps: int,
    amplitude: float = 1.0,
    start: int = 50,
    stop: int | None = None,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Return (n_timesteps, n_neurons) step-current stimulus."""
    if stop is None:
        stop = n_timesteps
    stimulus = np.zeros((n_timesteps, n_neurons), dtype=np.float32)
    stimulus[start:stop] = amplitude
    return stimulus


def generate_noise_current(
    n_neurons: int,
    n_timesteps: int,
    mean: float = 0.0,
    std: float = 0.1,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    return rng.normal(mean, std, size=(n_timesteps, n_neurons)).astype(np.float32)
