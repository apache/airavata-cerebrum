"""Framework-agnostic utility helpers."""
from __future__ import annotations
import numpy as np
from pathlib import Path


def save_outputs(path: str | Path, **arrays: np.ndarray) -> None:
    """Save named numpy arrays to a compressed .npz file."""
    np.savez_compressed(path, **arrays)


def load_outputs(path: str | Path) -> dict[str, np.ndarray]:
    data = np.load(path)
    return {k: data[k] for k in data.files}


def relative_error(a: np.ndarray, b: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """Element-wise relative error |a-b| / (|b| + eps)."""
    return np.abs(a - b) / (np.abs(b) + eps)


def max_relative_error(a: np.ndarray, b: np.ndarray, eps: float = 1e-8) -> float:
    return float(relative_error(a, b, eps).max())
