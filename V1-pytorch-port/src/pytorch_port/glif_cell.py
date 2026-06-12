"""
PyTorch port of the GLIF (Generalized Leaky Integrate-and-Fire) neuron cell.

Each call to `forward` advances all neurons by one timestep dt.

State dict keys:
  voltage   : (batch, N)  – membrane potential
  threshold : (batch, N)  – adaptive threshold
  i_asc     : (batch, N)  – after-spike current (can be extended to K components)
"""
from __future__ import annotations
from dataclasses import dataclass, field

import torch
import torch.nn as nn
import torch.nn.functional as F


# ──────────────────────────────────────────────────────────────────────────────
# Surrogate gradient spike function
# ──────────────────────────────────────────────────────────────────────────────
class _SpikeFunction(torch.autograd.Function):
    """Heaviside spike with piecewise-linear surrogate gradient."""

    @staticmethod
    def forward(ctx, v_minus_theta: torch.Tensor) -> torch.Tensor:
        ctx.save_for_backward(v_minus_theta)
        return (v_minus_theta >= 0).float()

    @staticmethod
    def backward(ctx, grad_output: torch.Tensor) -> torch.Tensor:
        (diff,) = ctx.saved_tensors
        surrogate = torch.clamp(1.0 - diff.abs(), min=0.0)
        return grad_output * surrogate


spike_function = _SpikeFunction.apply


# ──────────────────────────────────────────────────────────────────────────────
# GLIF Cell
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class GLIFParams:
    """Biophysical parameters for a population of N neurons."""
    n_neurons:   int
    dt:          float = 0.0005        # s
    # Membrane
    C_m:         float | torch.Tensor = 1.0     # pF
    g_L:         float | torch.Tensor = 0.1     # nS
    E_L:         float | torch.Tensor = -70.0   # mV
    V_reset:     float | torch.Tensor = -70.0   # mV
    # Threshold
    theta_inf:   float | torch.Tensor = -50.0   # mV
    tau_theta:   float | torch.Tensor = 0.02    # s
    # After-spike current
    tau_asc:     float | torch.Tensor = 0.1     # s
    b_asc:       float | torch.Tensor = 0.0     # pA  (injected after spike)


class GLIFCell(nn.Module):
    """
    Single-step GLIF neuron layer.

    Parameters
    ----------
    params : GLIFParams
        Biophysical parameters. Scalar or per-neuron tensors.

    Notes
    -----
    For now all parameters are *fixed* (not learned). To make them learnable,
    wrap in nn.Parameter:  self.g_L = nn.Parameter(torch.tensor(params.g_L))
    """

    def __init__(self, params: GLIFParams) -> None:
        super().__init__()
        p = params
        n = p.n_neurons

        def _buf(v) -> torch.Tensor:
            return torch.full((n,), v, dtype=torch.float32) if isinstance(v, float) else v.float()

        self.register_buffer("dt",        torch.tensor(p.dt))
        self.register_buffer("C_m",       _buf(p.C_m))
        self.register_buffer("g_L",       _buf(p.g_L))
        self.register_buffer("E_L",       _buf(p.E_L))
        self.register_buffer("V_reset",   _buf(p.V_reset))
        self.register_buffer("theta_inf", _buf(p.theta_inf))
        self.register_buffer("tau_theta", _buf(p.tau_theta))
        self.register_buffer("tau_asc",   _buf(p.tau_asc))
        self.register_buffer("b_asc",     _buf(p.b_asc))

        self.n_neurons = n

    # ── State helpers ──────────────────────────────────────────────────────────
    def initial_state(self, batch: int, device: torch.device | None = None):
        d = device or next(self.buffers()).device
        return {
            "voltage":   self.E_L.expand(batch, -1).clone().to(d),
            "threshold": self.theta_inf.expand(batch, -1).clone().to(d),
            "i_asc":     torch.zeros(batch, self.n_neurons, device=d),
        }

    # ── Forward ───────────────────────────────────────────────────────────────
    def forward(
        self,
        i_syn: torch.Tensor,           # (batch, N) synaptic + external current [pA]
        state: dict[str, torch.Tensor],
    ) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
        """
        Returns
        -------
        spikes : (batch, N) float  — 1 if neuron fired this step
        new_state : updated state dict
        """
        v, theta, i_asc = state["voltage"], state["threshold"], state["i_asc"]

        # ── Voltage update (Euler) ─────────────────────────────────────────
        dv = (self.dt / self.C_m) * (
            -self.g_L * (v - self.E_L)
            + i_syn
            + i_asc
        )
        v_new = v + dv

        # ── Spike detection (surrogate grad) ──────────────────────────────
        spikes = spike_function(v_new - theta)

        # ── Reset (soft — weighted by spike) ──────────────────────────────
        v_new = (1.0 - spikes) * v_new + spikes * self.V_reset

        # ── Threshold adaptation ───────────────────────────────────────────
        dtheta = (self.dt / self.tau_theta) * (self.theta_inf - theta)
        theta_new = theta + dtheta

        # ── After-spike current ────────────────────────────────────────────
        i_asc_new = i_asc * torch.exp(-self.dt / self.tau_asc) + spikes * self.b_asc

        new_state = {"voltage": v_new, "threshold": theta_new, "i_asc": i_asc_new}
        return spikes, new_state
