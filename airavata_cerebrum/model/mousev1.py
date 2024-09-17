import typing
import jsonpath
import ast

import numpy as np
import scipy
import pandas as pd
import bmtk.builder
import bmtk.builder.node_pool
from ..util.log.logging import LOGGER
from ..operations import netops
from ..dataset import abc_mouse
from . import structure

from ..operations.mousev1 import (
    compute_pair_type_parameters,
    connect_cells,
    syn_weight_by_experimental_distribution
)


class V1RegionMapper(structure.RegionMapper):
    def __init__(self, name: str, region_desc: typing.Dict[str, typing.Dict]):
        self.name = name
        self.region_desc = region_desc
        self.property_map = self.region_desc["property_map"]
        self.src_data = self.property_map[
            "airavata_cerebrum.dataset.abc_mouse"
        ][0]

    def neuron_names(self) -> typing.List[str]:
        return self.property_map["neurons"]

    def inh_fraction(self):
        return float(self.src_data["inh_fraction"])

    def region_fraction(self):
        return float(self.src_data["region_fraction"])

    def map(self, region_neurons: typing.Dict[str, structure.Neuron]) -> structure.Region:
        return structure.Region(
            name=self.name,
            inh_fraction=self.inh_fraction(),
            region_fraction=self.region_fraction(),
            neurons=region_neurons,
        )


structure.RegionMapper.register(V1RegionMapper)


class V1NeuronMapper(structure.NeuronMapper):
    abc_ptr = jsonpath.JSONPointer("/airavata_cerebrum.dataset.abc_mouse/0")
    ct_ptr = jsonpath.JSONPointer("/airavata_cerebrum.dataset.abm_celltypes")
    ev_ptr = jsonpath.JSONPointer(
        "/glif/neuronal_models/0/neuronal_model_runs/0/explained_variance_ratio"
    )

    def __init__(self, name: str, desc: typing.Dict[str, typing.Dict]):
        self.name = name
        self.desc = desc
        self.ct_data: typing.Iterable | None = None
        self.abc_data: typing.Iterable | None = None
        if self.abc_ptr.exists(desc):
            self.abc_data = self.abc_ptr.resolve(desc)  # type:ignore
        else:
            self.abc_data = None
        if self.abc_data is None:
            LOGGER.error("Can not find ABC Pointer in Model Description")
        if self.ct_ptr.exists(desc):
            self.ct_data = self.ct_ptr.resolve(desc)  # type: ignore
        else:
            self.ct_data = None
        if self.ct_data is None:
            LOGGER.error("Can not find ABM CT Pointer in Model Description")

    def map(self) -> structure.Neuron | None:
        ntype = self.desc["property_map"]["ei"]
        if not self.abc_data:
            return structure.Neuron(ei=ntype)
        nfrac = self.abc_data["fraction"]  # type:  ignore
        if not self.ct_data:
            return structure.Neuron(name=self.name, ei=ntype, fraction=float(nfrac))
        neuron_models = {}
        for mdesc in self.ct_data:
            spec_id = mdesc["ct"]["specimen__id"]
            m_type = "point_process"
            m_template = "nrn:IntFire1"
            params_file = str(spec_id) + "_glif_lif_asc_config.json"
            property_map = {"explained_variance_ratio": self.ev_ptr.resolve(mdesc)}
            nmodel = structure.NeuronModel(
                name=str(spec_id),
                m_type=m_type,
                template=m_template,
                dynamics_params=params_file,
                property_map=property_map,
            )
            neuron_models[nmodel.name] = nmodel
        return structure.Neuron(
            name=self.name,
            ei=ntype,
            fraction=float(nfrac),
            neuron_models=neuron_models,
        )


structure.NeuronMapper.register(V1NeuronMapper)


class V1ConnectionMapper(structure.ConnectionMapper):

    def __init__(self, name: str, desc: typing.Dict[str, typing.Dict]):
        self.name = name
        self.pre, self.post = ast.literal_eval(self.name)
        self.desc = desc

    def map(self) -> structure.Connection | None:
        if "airavata_cerebrum.dataset.ai_synphys" in self.desc:
            conn_prob = self.desc["airavata_cerebrum.dataset.ai_synphys"][0]["probability"]
            return structure.Connection(
                name=self.name,
                pre=self.pre,
                post=self.post,
                property_map={"A_literature": [conn_prob]},
            )
        else:
            return structure.Connection(
                name=self.name,
                pre=self.pre,
                post=self.post,
            )


structure.ConnectionMapper.register(V1ConnectionMapper)


class ABCRegionMapper:
    def __init__(self, name: str,
                 region_desc: typing.Dict):
        self.name = name
        self.region_desc = region_desc

    def map(self, neuron_struct: typing.Dict[str, structure.Neuron]) -> structure.Region:
        return structure.Region(
            name=self.name,
            inh_fraction=float(self.region_desc[abc_mouse.INHIBITORY_FRACTION_COLUMN]),
            region_fraction=float(self.region_desc[abc_mouse.FRACTION_WI_REGION_COLUMN]),
            neurons=neuron_struct,
        )


class ABCNeuronMapper:
    def __init__(self, name: str, desc: typing.Dict):
        self.name = name
        self.desc = desc
        self.ei_type = desc["ei"]

    def map(self) -> structure.Neuron | None:
        frac_col = abc_mouse.FRACTION_COLUMN_FMT.format(self.name)
        return structure.Neuron(ei=self.ei_type,
                                fraction=float(self.desc[frac_col]))

# def atlasdata2regionfractions(
#     region_frac_df: pd.DataFrame, model_name: str
# ) -> structure.Network:
#     loc_struct = {}
#     for loc, row in region_frac_df.iterrows():
#         neuron_struct = {}
#         for gx in abc_mouse.GABA_TYPES:
#             frac_col = abc_mouse.FRACTION_COLUMN_FMT.format(gx)
#             neuron_struct[gx] = structure.Neuron(ei="i", fraction=float(row[frac_col]))
#         for gx in abc_mouse.GLUT_TYPES:
#             frac_col = abc_mouse.FRACTION_COLUMN_FMT.format(gx)
#             neuron_struct[gx] = structure.Neuron(ei="e", fraction=float(row[frac_col]))
#         loc_struct[loc] = structure.Region(
#             name=str(loc),
#             inh_fraction=float(row[abc_mouse.INHIBITORY_FRACTION_COLUMN]),
#             region_fraction=float(row[abc_mouse.FRACTION_WI_REGION_COLUMN]),
#             neurons=neuron_struct,
#         )
#     return structure.Network(name=model_name, locations=loc_struct)


class V1BMTKNetworkBuilder:
    def __init__(
        self,
        net_struct: structure.Network,
        **kwargs,
    ):
        self.net_struct: structure.Network = net_struct
        self.fraction: float = 1.0
        self.flat: bool = False
        if "fraction" in kwargs:
            self.fraction = kwargs["fraction"]
        if "flat" in kwargs:
            self.fraction = kwargs["flat"]

        self.min_radius: float = 1.0  # to avoid diverging density near 0
        self.radius: float = self.net_struct.dims["radius"] * np.sqrt(self.fraction)
        self.radial_range: typing.List[float] = [self.min_radius, self.radius]
        self.net: bmtk.builder.NetworkBuilder = bmtk.builder.NetworkBuilder(self.net_struct.name)

    def add_model_nodes(
        self,
        location: str,
        loc_dims: typing.Dict,
        pop_neuron: structure.Neuron,
        neuron_model: structure.NeuronModel
    ):
        pop_name = pop_neuron.name
        pop_size = pop_neuron.N
        # if "N" not in model:
        #     # Assumes a 'proportion' key with a value from 0.0 to 1.0, N will be a proportion of pop_size
        #     model["N"] = model["proportion"] * pop_size
        #     del model["proportion"]
        N = pop_size
        if neuron_model.N == 0:
            if neuron_model.proportion > 0:
                N = int(pop_size * neuron_model.proportion)
            else:
                N = int(float(pop_size) / float(len(pop_neuron.neuron_models)))
        else:
            N = neuron_model.N
        ei = pop_neuron.ei
        if self.fraction != 1.0:
            # Each model will use only a fraction of the of the number of cells for each model
            # NOTE: We are using a ceiling function so there is atleast 1 cell of each type - however for models
            #  with only a few initial cells they can be over-represented.
            N = int(np.ceil(self.fraction * N))

        if self.flat:
            N = 100
        #
        # create a list of randomized cell positions for each cell type
        depth_range = -np.array(loc_dims["depth_range"], dtype=float)
        positions = netops.generate_random_cyl_pos(N, depth_range, self.radial_range)
        #
        # properties used to build the cells for each cell-type
        nsyn_lognorm_shape = pop_neuron.dims["nsyn_lognorm_shape"]
        nsyn_lognorm_scale = pop_neuron.dims["nsyn_lognorm_scale"]
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
        print(pop_name, neuron_model.name, len(target_sizes), nsyn_size_mean)
        node_props = {
            "N": N,
            "node_type_id": int(neuron_model.name),  # model["node_type_id"],
            "model_type": neuron_model.m_type,  # model["model_type"],  #  "model_type": "point_process",
            "model_template": neuron_model.template,  # model["model_template"],
            "dynamics_params": neuron_model.dynamics_params,
            "ei": ei,
            "location": location,
            "pop_name": pop_name,
            # "pop_name": (
            #     "LIF" if model["model_type"] == "point_process" else ""
            # )
            # + pop_name,
            "population": self.net_struct.name,
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
        #             # for RTNeuron store explicity store the x-rotations
        #             #   (even though it should be 0 by default).
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

        self.net.add_nodes(**node_props)

    def add_nodes(
        self,
    ) -> None:
        # if miniature:
        #     node_props = "glif_props/v1_node_models_miniature.json"
        # else:
        #     node_props = "glif_props/v1_node_models.json"
        #
        for location, loc_region in self.net_struct.locations.items():
            for _, pop_neuron in loc_region.neurons.items():
                pop_size = pop_neuron.N
                if pop_size == 0:
                    continue
                # --- Neuron Model ---
                for _, neuron_model in pop_neuron.neuron_models.items():
                    self.add_model_nodes(location, loc_region.dims,
                                         pop_neuron, neuron_model)

    def add_connection_edges(
        self,
        connex_item: structure.Connection,
        connex_md: structure.ConnectionModel,
    ) -> None:
        node_type_id = int(connex_md.target_model_id)
        src_type = connex_item.pre   # row["source_label"]
        trg_type = connex_item.post  # row["target_label"]
        src_trg_params = compute_pair_type_parameters(
            str(src_type),
            str(trg_type),
            connex_item
        )
        # print(src_trg_params)

        prop_query = ["x", "z", "tuning_angle"]
        src_criteria = {"pop_name": repr(src_type)}
        self.net.nodes()  # this line is necessary to activate nodes... (I don't know why.)
        source_nodes = bmtk.builder.node_pool.NodePool(self.net,
                                                       **src_criteria)
        print(src_type, trg_type, len(source_nodes), src_trg_params)
        source_nodes_df = pd.DataFrame(
            [{q: s[q] for q in prop_query} for s in source_nodes]
        )
        md_pmap = connex_md.property_map
        cx_pmap = connex_item.property_map

        # TODO: check if these values should be used
        # weight_fnc, weight_sigma = find_direction_rule(src_type, trg_type)
        if src_trg_params["A_new"] > 0.0:
            # if src_type.startswith("LIF"):
            #     net.add_edges(
            #         source={"pop_name": src_type},
            #         target={"node_type_id": node_type_id},
            #         iterator="all_to_one",
            #         connection_rule=connect_cells,
            #         connection_params={"params": src_trg_params},
            #         dynamics_params=row["params_file"],
            #         syn_weight=row["weight_max"],
            #         delay=row["delay"],
            #         weight_function=weight_fnc,
            #         weight_sigma=weight_sigma,
            #     )
            # else:
            # tentative fix for non-negative inhibitory connections
            if cx_pmap["pre_ei"] == "i":
                pspsign = -1
            else:
                pspsign = 1
            cm = self.net.add_edges(
                source=src_criteria,
                target={"node_type_id": node_type_id},
                iterator="all_to_one",
                connection_rule=connect_cells,  # type: ignore
                connection_params={
                    "params": src_trg_params,
                    "source_nodes": source_nodes_df,
                    "core_radius": self.net_struct.dims["core_radius"],
                },
                dynamics_params=md_pmap["params_file"],
                # syn_weight_max=row["weight_max"],
                delay=connex_md.delay,
                weight_function="weight_function_recurrent",
                # weight_sigma=weight_sigma,
                # distance_range=row["distance_range"],
                # target_sections=row["target_sections"],
                # PSP_correction=row["PSP_scale_factor"],  # original there is one more line to fix ~30 lines below.
                PSP_correction=np.abs(md_pmap["PSP_scale_factor"]) * pspsign,
                PSP_lognorm_shape=md_pmap["lognorm_shape"],
                PSP_lognorm_scale=md_pmap["lognorm_scale"],
                model_template="static_synapse",
            )
            # replaced with custom analytic cdf function
            # if not np.isnan(src_trg_params["gradient"]):
            #     pdf1, cdf1, ppf1 = orientation_dependence_fns(
            #         src_trg_params["intercept"], src_trg_params["gradient"]
            #     )

            #     class orientation_dependence_dist(rv_continuous):
            #         def _pdf(self, x):
            #             return pdf1(x)

            #         def _cdf(self, x):
            #             return cdf1(x)

            #         def _ppf(self, x):
            #             return ppf1(x)

            #     delta_theta_dist = orientation_dependence_dist()
            # else:
            #     delta_theta_dist = np.NaN

            cm.add_properties(
                ["syn_weight", "n_syns_"],
                rule=syn_weight_by_experimental_distribution,
                rule_params={
                    "src_type": src_type,
                    "trg_type": trg_type,
                    "src_ei": cx_pmap["pre_ei"],
                    "trg_ei": cx_pmap["post_ei"],
                    # "PSP_correction": row["PSP_scale_factor"],
                    "PSP_correction": np.abs(md_pmap["PSP_scale_factor"]) * pspsign,
                    "PSP_lognorm_shape": md_pmap["lognorm_shape"],
                    "PSP_lognorm_scale": md_pmap["lognorm_scale"],
                    "connection_params": src_trg_params,
                    # "delta_theta_dist": delta_theta_dist,
                    # "lognorm_shape": row["lognorm_shape"],
                    # "lognorm_scale": row["lognorm_scale"],
                },
                dtypes=[float, np.int64],
            )

    def add_edges(
        self,
    ):
        for _, connex_item in self.net_struct.connections.items():
            for _, connex_md in connex_item.models.items():
                # Build model from connection information
                self.add_connection_edges(connex_item, connex_md)

    def build(
        self,
    ) -> bmtk.builder.NetworkBuilder:
        self.add_nodes()
        self.add_edges()
        return self.net
