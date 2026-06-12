"""Full V1 GLIF network (PyTorch)."""
from __future__ import annotations
import torch
import torch.nn as nn
from .glif_cell import GLIFCell, GLIFParams
from .synapses import ExponentialSynapse, DenseConnectivity


class V1GLIFNetwork(nn.Module):
    """
    Minimal V1 GLIF network:
      - N recurrently connected GLIF neurons
      - Exponential synaptic filter
      - Dense connectivity (sparse variant via `sparse=True`)
    """

    def __init__(
        self,
        n_neurons: int = 230,
        dt: float = 0.0005,
        tau_syn: float = 0.005,
        **glif_kwargs,
    ) -> None:
        super().__init__()
        params = GLIFParams(n_neurons=n_neurons, dt=dt, **glif_kwargs)
        self.cell = GLIFCell(params)
        connectivity = DenseConnectivity(n_neurons, n_neurons)
        self.synapse = ExponentialSynapse(connectivity, tau_syn=tau_syn, dt=dt)
        self.n_neurons = n_neurons
        self.dt = dt

    def forward(
        self,
        ext_current: torch.Tensor,   # (T, batch, N) external drive
        initial_state: dict | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Run the network for T timesteps.

        Returns
        -------
        all_spikes   : (T, batch, N)
        all_voltages : (T, batch, N)
        """
        T, batch, _ = ext_current.shape
        device = ext_current.device

        cell_state = initial_state or self.cell.initial_state(batch, device)
        syn_state = self.synapse.initial_state(batch, self.n_neurons, device)

        spikes_list, voltages_list = [], []
        for t in range(T):
            i_syn, syn_state = self.synapse(
                cell_state["voltage"].detach(),   # recurrent input from prev step
                syn_state,
            )
            i_total = i_syn + ext_current[t]
            spikes, cell_state = self.cell(i_total, cell_state)
            spikes_list.append(spikes)
            voltages_list.append(cell_state["voltage"])

        return torch.stack(spikes_list), torch.stack(voltages_list)
