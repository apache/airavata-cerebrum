"""Synaptic current computation (PyTorch)."""
from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F


class DenseConnectivity(nn.Module):
    """
    Dense recurrent/feedforward weight matrix.

    W shape: (N_post, N_pre)
    current_out = W @ spikes_in   [no bias]
    """

    def __init__(self, n_pre: int, n_post: int) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.zeros(n_post, n_pre))
        nn.init.normal_(self.weight, std=0.01)

    def forward(self, spikes: torch.Tensor) -> torch.Tensor:
        """spikes: (batch, n_pre) → current: (batch, n_post)"""
        return F.linear(spikes, self.weight)   # no bias


class SparseConnectivity(nn.Module):
    """
    Sparse recurrent weight matrix backed by a COO tensor.

    NOTE: Gradients through sparse tensors require PyTorch >= 2.0 and
    coalesced sparse tensors. Use DenseConnectivity for the first
    correctness pass, this class for the performance pass.
    """

    def __init__(
        self,
        n_pre: int,
        n_post: int,
        indices: torch.Tensor,  # (2, nnz) — row, col
        values: torch.Tensor,   # (nnz,)
    ) -> None:
        super().__init__()
        self.n_pre = n_pre
        self.n_post = n_post
        self.weight = nn.Parameter(
            torch.sparse_coo_tensor(indices, values, (n_post, n_pre)).coalesce()
        )

    def forward(self, spikes: torch.Tensor) -> torch.Tensor:
        """spikes: (batch, n_pre) → current: (batch, n_post)"""
        # sparse mm expects (N_post, N_pre) @ (N_pre, batch) → (N_post, batch)
        return torch.sparse.mm(self.weight, spikes.T).T


class ExponentialSynapse(nn.Module):
    """
    Single-exponential synaptic filter.

    s[t+1] = s[t] * decay + pre_spikes[t]
    I_syn  = W @ s[t]
    """

    def __init__(
        self,
        connectivity: nn.Module,
        tau_syn: float = 0.005,
        dt: float = 0.0005,
    ) -> None:
        super().__init__()
        self.connectivity = connectivity
        self.register_buffer("decay", torch.tensor(float(torch.exp(torch.tensor(-dt / tau_syn)))))

    def initial_state(self, batch: int, n_pre: int, device=None):
        return torch.zeros(batch, n_pre, device=device)

    def forward(
        self, pre_spikes: torch.Tensor, syn_state: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Returns
        -------
        i_syn : (batch, n_post) — synaptic current
        new_syn_state : (batch, n_pre)
        """
        new_state = syn_state * self.decay + pre_spikes
        i_syn = self.connectivity(new_state)
        return i_syn, new_state
