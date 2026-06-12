#!/usr/bin/env python
"""Compare TF and PyTorch numerical outputs and produce a report."""
import argparse
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.shared.utils import load_outputs, relative_error, max_relative_error
from src.shared.plotting import raster_plot, compare_traces
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tf-results",  default="results/numerical/tf_out.npz")
    parser.add_argument("--pt-results",  default="results/numerical/pt_out.npz")
    parser.add_argument("--out-dir",     default="results/numerical")
    args = parser.parse_args()

    tf = load_outputs(args.tf_results)
    pt = load_outputs(args.pt_results)
    out_dir = Path(args.out_dir)

    print("=" * 60)
    print("Numerical Comparison: TensorFlow vs PyTorch")
    print("=" * 60)

    for key in ("spikes", "voltages"):
        if key not in tf or key not in pt:
            continue
        err = max_relative_error(tf[key], pt[key])
        match = "✅" if err < 1e-4 else "⚠️ " if err < 1e-2 else "❌"
        print(f"  {match}  {key:12s}  max_rel_err = {err:.3e}")

    # Raster comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 4))
    raster_plot(tf["spikes"], ax=axes[0], title="TF spikes")
    raster_plot(pt["spikes"], ax=axes[1], title="PT spikes")
    fig.savefig(out_dir / "raster_comparison.png", dpi=120, bbox_inches="tight")
    print(f"\nSaved raster plot → {out_dir}/raster_comparison.png")

    # Voltage trace
    if "voltages" in tf and "voltages" in pt:
        fig2 = compare_traces(tf["voltages"], pt["voltages"], label="voltage (mV)")
        fig2.savefig(out_dir / "voltage_comparison.png", dpi=120, bbox_inches="tight")
        print(f"Saved voltage plot → {out_dir}/voltage_comparison.png")


if __name__ == "__main__":
    main()
