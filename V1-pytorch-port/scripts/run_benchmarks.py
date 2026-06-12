#!/usr/bin/env python
"""GPU / memory / multi-GPU benchmarks for TF and PT."""
import argparse, json, time, sys
from pathlib import Path
import numpy as np
import yaml
import torch

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.pytorch_port.network import V1GLIFNetwork

try:
    import py3nvml.py3nvml as nvml
    nvml.nvmlInit()
    HAS_NVML = True
except Exception:
    HAS_NVML = False


def benchmark_pytorch(cfg: dict, device_str: str = "cuda") -> dict:
    device = torch.device(device_str if torch.cuda.is_available() else "cpu")
    n, T, B = cfg["n_neurons"], cfg["n_timesteps"], cfg.get("batch_size", 8)

    net = V1GLIFNetwork(n_neurons=n, dt=cfg["dt"]).to(device)
    net.eval()
    ext = torch.randn(T, B, n, device=device)

    # Warmup
    with torch.no_grad():
        net(ext)
    if device.type == "cuda":
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats(device)

    # Timed run
    t0 = time.perf_counter()
    with torch.no_grad():
        for _ in range(cfg.get("n_repeats", 10)):
            net(ext)
    if device.type == "cuda":
        torch.cuda.synchronize()
    elapsed = (time.perf_counter() - t0) / cfg.get("n_repeats", 10)

    peak_mb = (
        torch.cuda.max_memory_allocated(device) / 1e6
        if device.type == "cuda" else 0
    )

    return {
        "framework": "pytorch",
        "device": device_str,
        "n_neurons": n,
        "T": T,
        "batch_size": B,
        "mean_step_ms": elapsed * 1000,
        "peak_vram_mb": peak_mb,
        "n_gpus": torch.cuda.device_count(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/benchmark.yaml")
    parser.add_argument("--out", default="results/performance/benchmarks.json")
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = yaml.safe_load(f)

    results = []
    for device in ("cpu", "cuda"):
        if device == "cuda" and not torch.cuda.is_available():
            print(f"Skipping {device} (not available)")
            continue
        r = benchmark_pytorch(cfg, device)
        results.append(r)
        print(f"[PT/{device}]  {r['mean_step_ms']:.1f} ms/step  |  VRAM {r['peak_vram_mb']:.0f} MB")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved benchmark results → {args.out}")


if __name__ == "__main__":
    main()
