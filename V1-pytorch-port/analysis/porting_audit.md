# Porting Audit — V1 GLIF Model

Source: https://github.com/JavierGalvan9/V1_GLIF_model/tree/master

## 1. Repository Overview

The model simulates a biologically-realistic V1 cortical column using
Generalized Leaky Integrate-and-Fire (GLIF) neurons:
> Teeter et al. (2018). *Generalized leaky integrate-and-fire models classify
> multiple neuron types.* Nature Communications.

Key TensorFlow constructs used:
- `tf.keras.layers.AbstractRNNCell` subclasses (GLIF neuron dynamics)
- `tf.keras.layers.RNN` for time-stepping
- `tf.Variable` for stateful / learnable parameters
- `tf.sparse.SparseTensor` for connectivity matrices
- `@tf.function` for graph compilation
- Custom surrogate gradient ops for spike discontinuity
- `tf.distribute.MirroredStrategy` for multi-GPU

## 2. Porting Regions

### Region A — GLIF Cell (`glif_cell.py`)
**TF:** `AbstractRNNCell`, `tf.Variable`, state-tuple management
**PT:** custom `nn.Module` + manual state dict
**Issues:**
- `call(inputs, states)` → `forward(x, h)` signature change
- State tensors: tuple-of-tensors (TF) vs tensor/NamedTuple (PT)
- Shape broadcast conventions differ subtly

### Region B — Synaptic Dynamics (`synapses.py`)
**TF:** `tf.linalg.matvec`, `tf.nn.relu`
**PT:** `torch.mv` / `F.linear`, `F.relu`
**Issues:**
- Transposition convention in matvec — must verify
- Sparse connectivity: `tf.SparseTensor` → `torch.sparse_coo_tensor`

### Region C — Connectivity / Weight Matrices (`network.py`)
**TF:** `tf.SparseTensor`, sparse-dense matmul
**PT:** `torch.sparse_coo_tensor`, `torch.sparse.mm`
**Issues:**
- PyTorch sparse gradient support is less mature; start with dense,
  optimize to sparse later
- Index tensor dtype requirements differ

### Region D — Stimulus / Data Pipeline (`stimulus.py`)
**TF:** `tf.data.Dataset`, `tf.io`
**PT:** `torch.utils.data.Dataset` + `DataLoader`
**Issues:** Low risk — mostly numpy ops underneath

### Region E — Training Loop & Surrogate Gradient
**TF:** `GradientTape`, `custom_gradient`, `MirroredStrategy`
**PT:** `autograd.Function` (custom backward), `DDP`
**Issues:**
- Surrogate gradient is the highest-risk piece — different hook API
- `MirroredStrategy` vs `DistributedDataParallel` (very different paradigms)
- `@tf.function` graph tracing vs `torch.compile`

### Region F — Metrics / Logging
**TF:** `tf.keras.metrics`, `tf.summary`
**PT:** `torchmetrics` or manual accumulators, `SummaryWriter`
**Issues:** Low risk

## 3. Known Porting Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Surrogate gradient | HIGH | Implement `autograd.Function`; cross-check gradients numerically |
| Sparse connectivity gradients | HIGH | Dense fallback first |
| RNN state management | MEDIUM | Explicit state dicts; thorough unit tests |
| Float parity TF vs PT | MEDIUM | Accept < 1e-5 relative diff; flag larger |
| Multi-GPU (DDP vs MirroredStrategy) | MEDIUM | Single-GPU correctness first |
| Data pipeline | LOW | Numpy-backed; straightforward |

## 4. Recommended Porting Order

1. Data pipeline (Region D)
2. GLIF cell forward pass / no gradients (Region A)
3. Synaptic dynamics (Region B)
4. Connectivity — dense (Region C)
5. Surrogate gradient (Region E, partial)
6. Full training loop (Region E)
7. Multi-GPU support (Region E)
8. Sparse optimization pass (Region C revisit)
