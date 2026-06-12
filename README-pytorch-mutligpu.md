# V1 GLIF Model — TensorFlow → PyTorch Port

This branch involves systematic porting of the
[V1 GLIF Model](https://github.com/JavierGalvan9/V1_GLIF_model) (Allen Institute
V1 cortical column, Generalized Leaky Integrate-and-Fire neurons) from TensorFlow
to PyTorch.

## Project Objectives

| # | Objective |
|---|-----------|
| 1 | Audit the existing TF implementation |
| 2 | Identify TF→PyTorch porting regions & flag known issues |
| 3 | Write unit tests for each ported region (test-first) |
| 4 | Implement the PyTorch port |
| 5 | Numerical correctness comparison (TF vs PT outputs) |
| 6 | GPU / multi-GPU / memory performance benchmarks |


## Porting Status

See [docs/porting_status.md](docs/porting_status.md) for a live checklist.

## Contributing

1. Open an issue for each porting region (use the `porting` label).
2. Write failing tests first (`tests/unit/`).
3. Implement, make tests green, open a PR.
