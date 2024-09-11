import numpy as np
import scipy.stats
from bmtk.builder import NetworkBuilder
from ..model import structure
from ..operations import netops


def generate_random_pos(N, params):
    # TODO:
    x = np.array(params["dims"])
    y = np.array(params["dims"])
    z = np.array(params["dims"])
    positions = np.column_stack((x, y, z))

    return positions


def add_network_nodes(net_model: structure.Network, out_file: str):
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


def add_nodes_cylinder(net_model: structure.Network, fraction=1.00, flat=False):
    # if miniature:
    #     node_props = "glif_props/v1_node_models_miniature.json"
    # else:
    #     node_props = "glif_props/v1_node_models.json"
    # v1_models = json.load(open(node_props, "r"))

    min_radius = 1.0  # to avoid diverging density near 0
    radius = net_model.dims["radius"] * np.sqrt(fraction)
    radial_range = [min_radius, radius]

    net = NetworkBuilder(net_model.name)

    for location, loc_region in net_model.locations.items():
        for pop_name, pop_neurons in loc_region.neurons.items():
            pop_size = pop_neurons.N
            if pop_size == 0:
                continue
            depth_range = -np.array(loc_region.dims["depth_range"], dtype=float)
            ei = pop_neurons.ei
            # TODO:
            # print("dims", pop_neurons.dims)
            nsyn_lognorm_shape = 0
            if "nsyn_lognorm_shape" in pop_neurons.dims:
                nsyn_lognorm_shape = pop_neurons.dims["nsyn_lognorm_shape"]
            nsyn_lognorm_scale = 0
            if "nsyn_lognorm_scale" in pop_neurons.dims:
                nsyn_lognorm_scale = pop_neurons.dims["nsyn_lognorm_scale"]

            # for model in pop_neurons["models"]:
            # Assuming there is only one model for all
            # if "N" not in model:
            #     # Assumes a 'proportion' key with a value from 0.0 to 1.0, N will be a proportion of pop_size
            #     model["N"] = model["proportion"] * pop_size
            #     del model["proportion"]
            N = pop_size  # Only model
            if fraction != 1.0:
                # Each model will use only a fraction of the of the number of cells for each model
                # NOTE: We are using a ceiling function so there is atleast 1 cell of each type - however for models
                #  with only a few initial cells they can be over-represented.
                N = int(np.ceil(fraction * N))

            if flat:
                N = 100
            # create a list of randomized cell positions for each cell type
            positions = netops.generate_random_cyl_pos(N, depth_range, radial_range)

            # properties used to build the cells for each cell-type
            target_sizes = []
            if nsyn_lognorm_shape > 0:
                target_sizes = netops.generate_target_sizes(
                    N, nsyn_lognorm_shape, nsyn_lognorm_scale
                )
            nsyn_size_mean = 0
            if nsyn_lognorm_shape > 0:
                nsyn_size_mean = int(
                    scipy.stats.lognorm(
                        s=nsyn_lognorm_shape, loc=0, scale=nsyn_lognorm_scale
                    ).stats(moments="m")
                )
            print(pop_name, target_sizes, nsyn_size_mean)
            node_props = {
                "N": N,
                # "node_type_id": model["node_type_id"],
                # "model_type": model["model_type"],
                # "model_template": model["model_template"],
                # "dynamics_params": model["dynamics_params"],
                "model_type": "point_process",
                "ei": ei,
                "location": location,
                "pop_name": pop_name,
                # "pop_name": (
                #     "LIF" if model["model_type"] == "point_process" else ""
                # )
                # + pop_name,
                "population": net_model.name,
                "x": positions[:, 0],
                "y": positions[:, 1],
                "z": positions[:, 2],
                "tuning_angle": np.linspace(0.0, 360.0, N, endpoint=False),
                "target_sizes": target_sizes,
                # "EPSP_unitary": model["EPSP_unitary"],
                # "IPSP_unitary": model["IPSP_unitary"],
                "nsyn_size_shape": nsyn_lognorm_shape,
                "nsyn_size_scale": nsyn_lognorm_scale,
                "nsyn_size_mean": nsyn_size_mean,
                # "size_connectivity_correction":
            }
            # if model["model_type"] == "biophysical":
            #     # for biophysically detailed cell-types add info about rotations and morphology
            #     node_props.update(
            #         {
            #             # for RTNeuron store explicity store the x-rotations (even though it should be 0 by default).
            #             "rotation_angle_xaxis": np.zeros(N),
            #             "rotation_angle_yaxis": 2 * np.pi * np.random.random(N),
            #             # for RTNeuron we need to store z-rotation in the h5 file.
            #             "rotation_angle_zaxis": np.full(
            #                 N, model["rotation_angle_zaxis"]
            #             ),
            #             "model_processing": model["model_processing"],
            #             "morphology": model["morphology"],
            #         }
            #     )

            net.add_nodes(**node_props)

    return net


def build_model(model_struct):
    pass
