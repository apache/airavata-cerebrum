"""Shared plotting helpers for raster plots, voltage traces, comparisons."""
from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt


def raster_plot(
    spikes: np.ndarray,
    dt: float = 0.001,
    ax: plt.Axes | None = None,
    title: str = "Spike raster",
) -> plt.Axes:
    """Plot spike raster. spikes: (T, N) binary array."""
    ax = ax or plt.gca()
    times, neurons = np.where(spikes)
    ax.scatter(times * dt, neurons, s=1, c="k", marker="|")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Neuron index")
    ax.set_title(title)
    return ax


def compare_traces(
    tf_trace: np.ndarray,
    pt_trace: np.ndarray,
    label: str = "voltage",
    dt: float = 0.001,
    neuron_idx: int = 0,
) -> plt.Figure:
    """Side-by-side trace comparison between TF and PT outputs."""
    fig, axes = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
    t = np.arange(tf_trace.shape[0]) * dt
    axes[0].plot(t, tf_trace[:, neuron_idx], label="TensorFlow", color="tab:blue")
    axes[0].plot(t, pt_trace[:, neuron_idx], label="PyTorch", color="tab:orange",
                 linestyle="--")
    axes[0].legend()
    axes[0].set_ylabel(label)
    axes[0].set_title(f"Neuron {neuron_idx} — {label} comparison")
    diff = tf_trace[:, neuron_idx] - pt_trace[:, neuron_idx]
    axes[1].plot(t, diff, color="tab:red")
    axes[1].axhline(0, color="k", linewidth=0.5)
    axes[1].set_ylabel("TF − PT")
    axes[1].set_xlabel("Time (s)")
    fig.tight_layout()
    return fig
