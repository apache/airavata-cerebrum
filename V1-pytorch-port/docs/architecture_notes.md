# Architecture Notes

## GLIF Neuron Dynamics

The GLIF model integrates:
  voltage (V), threshold (θ), after-spike current (I_ASC)

Update equations per timestep dt:
  V[t+1]  = V[t] + dt/C * (-g_L*(V[t] - E_L) + I_syn + I_ASC + I_ext)
  θ[t+1]  = θ[t] + dt * (θ_inf - θ[t]) / τ_θ   [threshold adaptation]
  I_ASC   = I_ASC * exp(-dt/τ_ASC) + b  [after-spike current]

Spike condition: V[t] >= θ[t]  →  reset V to V_reset

## Surrogate Gradient

The Heaviside spike function is non-differentiable. The TF implementation
uses a piecewise-linear surrogate:

  dH/dV ≈ max(0, 1 - |V - θ|)   [or similar]

In PyTorch this is implemented via `torch.autograd.Function`:
```python
class SpikeFunction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, v, theta):
        ctx.save_for_backward(v - theta)
        return (v >= theta).float()

    @staticmethod
    def backward(ctx, grad_output):
        (diff,) = ctx.saved_tensors
        surrogate = torch.clamp(1.0 - diff.abs(), min=0)
        return grad_output * surrogate, -grad_output * surrogate
```

## Connectivity

Sparse weight matrix W of shape (N_post, N_pre).
TF: `tf.sparse.SparseTensor` + `tf.sparse.sparse_dense_matmul`
PT:  Start with dense `torch.Tensor`, later `torch.sparse_coo_tensor`
