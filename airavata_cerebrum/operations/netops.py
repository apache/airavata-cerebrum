import numpy as np
import scipy
import scipy.stats
import typing


def generate_random_cyl_pos(
        N: int,
        layer_range: typing.List[float] | np.ndarray,
        radial_range: typing.List[float] | np.ndarray,
) -> np.ndarray:
    radius_outer = radial_range[1]
    radius_inner = radial_range[0]

    phi = 2.0 * np.pi * np.random.random([N])
    r = np.sqrt(
        (radius_outer**2 - radius_inner**2) * np.random.random([N])
        + radius_inner**2
    )
    x = r * np.cos(phi)
    z = r * np.sin(phi)

    layer_start = layer_range[0]
    layer_end = layer_range[1]
    # Generate N random z values.
    y = (layer_end - layer_start) * np.random.random([N]) + layer_start

    positions = np.column_stack((x, y, z))

    return positions


def generate_target_sizes(
        N: int,
        ln_shape: float,
        ln_scale: float
) -> int:
    ln_rv = scipy.stats.lognorm(s=ln_shape, loc=0, scale=ln_scale)
    ln_rvs = ln_rv.rvs(N).round()
    return ln_rvs


def generate_node_positions(model_struct):
    pass
