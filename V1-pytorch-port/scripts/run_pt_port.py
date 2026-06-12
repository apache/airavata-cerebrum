#!/usr/bin/env python
"""Run the PyTorch V1 GLIF network and save outputs."""
import argparse
import numpy as np
import torch
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.pytorch_port.network import V1GLIFNetwork
from src.shared.stimulus import generate_step_current
from src.shared.utils import save_outputs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--out", default="results/numerical/pt_out.npz")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = yaml.safe_load(f)

    device = torch.device(args.device)
    net = V1GLIFNetwork(
        n_neurons=cfg["n_neurons"],
        dt=cfg["dt"],
        tau_syn=cfg.get("tau_syn", 0.005),
    ).to(device)
    net.eval()

    stim_np = generate_step_current(
        n_neurons=cfg["n_neurons"],
        n_timesteps=cfg["n_timesteps"],
        amplitude=cfg.get("amplitude", 1.0),
    )
    # (T, N) → (T, 1, N)
    stim = torch.from_numpy(stim_np).unsqueeze(1).to(device)

    with torch.no_grad():
        spikes, voltages = net(stim)

    save_outputs(
        args.out,
        spikes=spikes.squeeze(1).cpu().numpy(),
        voltages=voltages.squeeze(1).cpu().numpy(),
    )
    print(f"Saved PT outputs → {args.out}")
    print(f"  Mean firing rate: {spikes.mean().item():.4f}")


if __name__ == "__main__":
    main()
