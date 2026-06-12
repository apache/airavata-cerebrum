"""
Thin runner that loads the original TF V1 GLIF model and saves outputs
to NumPy arrays for comparison with the PyTorch port.

Usage:
    python -m src.tensorflow_baseline.runner \
        --config configs/default.yaml \
        --out results/numerical/tf_out.npz

Prerequisites:
    - The original repo cloned at `vendor/V1_GLIF_model/`
    - Conda env: tf_glif
"""
from __future__ import annotations
import sys
import argparse
from pathlib import Path
import numpy as np
import yaml

VENDOR_PATH = Path(__file__).parents[3] / "vendor" / "V1_GLIF_model"


def _add_vendor_to_path():
    if str(VENDOR_PATH) not in sys.path:
        sys.path.insert(0, str(VENDOR_PATH))


def run(config: dict) -> dict[str, np.ndarray]:
    _add_vendor_to_path()
    # TODO: import the actual TF model classes once vendor submodule is present
    # from models.network import V1Network
    # ...
    raise NotImplementedError(
        "Vendor submodule not yet added. "
        "Run: git submodule add https://github.com/JavierGalvan9/V1_GLIF_model vendor/V1_GLIF_model"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--out", default="results/numerical/tf_out.npz")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    results = run(config)
    np.savez_compressed(args.out, **results)
    print(f"Saved TF outputs → {args.out}")


if __name__ == "__main__":
    main()
