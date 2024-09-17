import numpy as np
import scipy
import scipy.stats
import typing
from ..model import structure


def srcdata2network(
    network_desc: typing.Dict,
    model_name: str,
    desc2region_mapper: type[structure.RegionMapper],
    desc2neuron_mapper: type[structure.NeuronMapper],
    desc2connection_mapper: type[structure.ConnectionMapper]
) -> structure.Network:
    loc_struct = {}
    for region, region_desc in network_desc["locations"].items():
        drx_mapper = desc2region_mapper(region, region_desc)
        neuron_struct = {}
        for neuron in drx_mapper.neuron_names():
            if neuron not in region_desc:
                continue
            neuron_desc = region_desc[neuron]
            dn_mapper = desc2neuron_mapper(neuron, neuron_desc)
            neuron_struct[neuron] = dn_mapper.map()
        loc_struct[region] = drx_mapper.map(neuron_struct)
    conn_struct = {}
    for cname, connect_desc in network_desc["connections"].items():
        crx_mapper = desc2connection_mapper(cname, connect_desc)
        conn_struct[cname] = crx_mapper.map()
    return structure.Network(
        name=model_name,
        locations=loc_struct,
        connections=conn_struct,
    )


def subset_network(net_stats: structure.Network,
                   region_list: typing.List[str]) -> structure.Network:
    sub_locs = {k: v for k, v in net_stats.locations.items() if k in region_list}
    return structure.Network(name=net_stats.name, dims=net_stats.dims,
                             locations=sub_locs)


def fractions2ncells(net_stats: structure.Network, N: int) -> structure.Network:
    net_stats.ncells = N
    for lx, lrx in net_stats.locations.items():
        ncells_region = int(lrx.region_fraction * N)
        ncells_inh = int(lrx.inh_fraction * ncells_region)
        ncells_exc = ncells_region - ncells_inh
        net_stats.locations[lx].ncells = ncells_region
        net_stats.locations[lx].inh_ncells = ncells_inh
        net_stats.locations[lx].exc_ncells = ncells_exc
        for nx, nurx in lrx.neurons.items():
            eix = nurx.ei
            ncells = ncells_inh if eix == "i" else ncells_exc
            ncells = int(ncells * nurx.fraction)
            if ncells == 0:
                continue
            net_stats.locations[lx].neurons[nx].N = ncells
    return net_stats


def generate_random_cyl_pos(N, layer_range, radial_range):
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


def generate_target_sizes(N, ln_shape, ln_scale):
    ln_rv = scipy.stats.lognorm(s=ln_shape, loc=0, scale=ln_scale)
    ln_rvs = ln_rv.rvs(N).round()
    return ln_rvs


def generate_node_positions(model_struct):
    pass


def map_node_paramas(model_struct, node_map):
    pass


def filter_node_params(model_struct, filter_predicate):
    pass


def map_edge_paramas(model_struct, node_map):
    pass


def filter_edge_params(model_struct, filter_predicate):
    pass


def union_network(model_struct1, model_struct2):
    pass


def join_network(model_struct1, model_struct2):
    pass
