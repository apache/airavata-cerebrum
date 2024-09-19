import typing
import numpy as np
from bmtk.builder import NetworkBuilder
from . import structure


def generate_random_pos(N: int, params: typing.Dict) -> np.ndarray:
    r_scale = 1
    if "dims" in params and "scale" in params["dims"]:
        r_scale = params["dims"]["scale"]
    x = np.random.random([N]) * r_scale
    y = np.random.random([N]) * r_scale
    z = np.random.random([N]) * r_scale
    positions = np.column_stack((x, y, z))
    return positions


def add_network_nodes(net_model: structure.Network, out_file: str) -> NetworkBuilder:
    net = NetworkBuilder(net_model.name)
    for location, loc_region in net_model.locations.items():
        for pop_name, pop_neurons in loc_region.neurons.items():
            N = pop_neurons.N
            params = {"location": loc_region.dims,
                      "population": pop_neurons.dims}
            positions = generate_random_pos(N, params)
            ei = pop_neurons.ei
            node_props = {
                "N": N,
                "model_type": "point_process",
                "ei": ei,
                "location": location,
                "pop_name": pop_name,
                "population": net_model.name,
                "x": positions[:, 0],
                "y": positions[:, 1],
                "z": positions[:, 2],
                "tuning_angle": np.linspace(0.0, 360.0, N, endpoint=False),
            }
            net.add_nodes(**node_props)
    net.save(out_file)
    return net


def build_model(model_struct: structure.Network) -> None:
    pass
