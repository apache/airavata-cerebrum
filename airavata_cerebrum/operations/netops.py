import pandas as pd
import numpy as np
import scipy
import scipy.stats
import typing
from ..dataset import abc_mouse
from ..model import structure


def atlasdata2network(
    atlas_data, model_name: str, desc2region_mapper, desc2neuron_mapper
) -> structure.Network:
    loc_struct = {}
    for region, region_desc in atlas_data.items():
        drx_mapper = desc2region_mapper(region_desc)
        neuron_struct = {}
        for neuron in drx_mapper.neuron_list():
            if neuron not in region_desc:
                continue
            neuron_desc = region_desc[neuron]
            dn_mapper = desc2neuron_mapper(neuron_desc)
            neuron_struct[neuron] = dn_mapper.map()
        loc_struct[region] = structure.Region(
            name=str(region),
            inh_fraction=drx_mapper.inh_fraction(),
            region_fraction=drx_mapper.region_fraction(),
            neurons=neuron_struct,
        )
    return structure.Network(name=model_name, locations=loc_struct)


def atlasdata2regionfractions(
    region_frac_df: pd.DataFrame, model_name: str
) -> structure.Network:
    loc_struct = {}
    for loc, row in region_frac_df.iterrows():
        neuron_struct = {}
        for gx in abc_mouse.GABA_TYPES:
            frac_col = abc_mouse.FRACTION_COLUMN_FMT.format(gx)
            neuron_struct[gx] = structure.Neuron(ei="i", fraction=float(row[frac_col]))
        for gx in abc_mouse.GLUT_TYPES:
            frac_col = abc_mouse.FRACTION_COLUMN_FMT.format(gx)
            neuron_struct[gx] = structure.Neuron(ei="e", fraction=float(row[frac_col]))
        loc_struct[loc] = structure.Region(
            name=str(loc),
            inh_fraction=float(row[abc_mouse.INHIBITORY_FRACTION_COLUMN]),
            region_fraction=float(row[abc_mouse.FRACTION_WI_REGION_COLUMN]),
            neurons=neuron_struct,
        )
    return structure.Network(name=model_name, locations=loc_struct)


def subset_network(net_stats: structure.Network,
                   region_list: typing.List[str]) -> structure.Network:
    sub_locs = {k: v for k, v in net_stats.locations.items() if k in region_list}
    return structure.Network(name=net_stats.name, dims=net_stats.dims,
                             locations=sub_locs)


def update_user_input(
    net_stats: structure.Network, upd_stats: structure.Network
) -> structure.Network:
    # update dims
    for upkx, upvx in upd_stats.dims.items():
        net_stats.dims[upkx] = upvx
    upd_locations = upd_stats.locations
    net_locations = net_stats.locations
    # Locations
    for lx, uprx in upd_locations.items():
        if lx not in net_locations:
            net_stats.locations[lx] = uprx
            continue
        # update fractions
        if uprx.inh_fraction > 0:
            net_stats.locations[lx].inh_fraction = uprx.inh_fraction
        if uprx.region_fraction > 0:
            net_stats.locations[lx].region_fraction = uprx.region_fraction
        # update ncells
        if uprx.ncells > 0:
            net_stats.locations[lx].ncells = uprx.ncells
        if uprx.inh_ncells > 0:
            net_stats.locations[lx].inh_ncells = uprx.inh_ncells
        if uprx.exc_ncells > 0:
            net_stats.locations[lx].exc_ncells = uprx.exc_ncells
        # update dimensions
        for upkx, upvx in uprx.dims.items():
            net_stats.locations[lx].dims[upkx] = upvx
        # update neuron details
        for nx, sx in uprx.neurons.items():
            if nx not in net_stats.locations[lx].neurons:
                net_stats.locations[lx].neurons[nx] = sx
                continue
            if sx.fraction > 0:
                net_stats.locations[lx].neurons[nx].fraction = sx.fraction
            if sx.N > 0:
                net_stats.locations[lx].neurons[nx].N = sx.N
            # update dimensions
            for upkx, upvx in uprx.neurons[nx].dims.items():
                net_stats.locations[lx].neurons[nx].dims[upkx] = upvx
            # update model items
            # model_name : str | None = None
            # model_type: str | None =  None
            # model_template: str | None = None
            # dynamics_params: str | None = None
            for sx_model in sx.neuron_models:
                nmodel = structure.NeuronModel()
                if sx_model.name is not None:
                    nmodel.name = sx_model.name
                if sx_model.m_type is not None:
                    nmodel.m_type = sx_model.m_type
                if sx_model.template is not None:
                    nmodel.template = sx_model.template
                if sx_model.dynamics_params is not None:
                    nmodel.template = sx_model.dynamics_params
                net_stats.locations[lx].neurons[nx].neuron_models.append(nmodel)
    return net_stats


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
