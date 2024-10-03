import json
import pydantic
import traitlets
import typing
import abc


class StructBase(pydantic.BaseModel, abc.ABC):
    name: str = ""

    class StructBaseTrait(traitlets.HasTraits):
        name = traitlets.Unicode()

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.StructBaseTrait

    @abc.abstractmethod
    def exclude(self) -> typing.Set[str]:
        return set([])

    @classmethod
    def trait_ui(cls) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
        return {}


class DataLink(StructBase):
    property_map: typing.Dict = {}

    class DataTrait(StructBase.StructBaseTrait):
        # property_map = traitlets.Dict()
        property_map = traitlets.Unicode()


    def exclude(self) -> typing.Set[str]:
        return set([])

    @classmethod
    def trait_ui(cls) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
        return {
            "name": {"type": "text", "label": "Name", "default": ""},
            "property_map": {"type": "textarea", "label": "Property Map", "default": "{}"},
        }

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.DataTrait


class ComponentModel(StructBase):
    property_map: typing.Dict = {}

    class DataTrait(StructBase.StructBaseTrait):
        property_map = traitlets.Dict()

        def __init__(self, property_map={}, **kwargs):
            super().__init__(
                property_map=json.dumps(property_map, indent=4),
                **kwargs,
            )

    def exclude(self) -> typing.Set[str]:
        return set([])

    @classmethod
    def trait_ui(cls) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
        return {
            "name": {"type": "text", "label": "Name", "default": ""},
            "property_map": {
                "type": "textarea",
                "label": "Property Map",
                "default": "{}",
            },
        }

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.DataTrait


class NeuronModel(StructBase):
    N: int = 0
    id: str = ""
    proportion: float = 0.0
    name: str = ""
    m_type: str = ""
    template: str = ""
    dynamics_params: str = ""
    property_map: typing.Dict = {}
    data_connect: DataLink = DataLink()

    class DataTrait(StructBase.StructBaseTrait):
        N = traitlets.Int()
        id = traitlets.Unicode()
        proportion = traitlets.Float(0.0)
        m_type = traitlets.Unicode()
        template = traitlets.Unicode()
        dynamics_params = traitlets.Unicode()
        # property_map = traitlets.Dict()
        property_map = traitlets.Unicode()

        def __init__(self, property_map={}, **kwargs):
            super().__init__(
                property_map=json.dumps(property_map, indent=4),
                **kwargs,
            )

    def exclude(self) -> typing.Set[str]:
        return set(["data_connect"])

    @classmethod
    def trait_ui(cls) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
        return {
            "N": {"type": "int", "label": "N", "default": 0},
            "id": {"type": "text", "label": "id", "default": ""},
            "proportion": {"type": "float", "label": "Proportion", "default": 0.0},
            "name": {"type": "text", "label": "Name", "default": ""},
            "m_type": {"type": "text", "label": "Model Type", "default": ""},
            "template": {"type": "text", "label": "Template", "default": ""},
            "dynamics_params": {
                "type": "text",
                "label": "Dynamis Parameters",
                "default": "",
            },
            "property_map": {
                "type": "textarea",
                "label": "Property Map",
                "default": "{\n}",
            },
        }

    def apply_mod(self, mod_model: "NeuronModel") -> "NeuronModel":
        if mod_model.name is not None:
            self.name = mod_model.name
        # Model Parameters
        if mod_model.m_type is not None:
            self.m_type = mod_model.m_type
        if mod_model.template is not None:
            self.template = mod_model.template
        if mod_model.dynamics_params is not None:
            self.dynamics_params = mod_model.dynamics_params
        # Model Property Map
        for pkey, pvalue in mod_model.property_map.items():
            if pkey not in self.property_map:
                self.property_map[pkey] = pvalue
            elif pvalue:
                self.property_map[pkey] = pvalue
        return self

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.DataTrait


class Neuron(StructBase):
    N: int = 0
    fraction: float = 0.0
    ei: typing.Literal["e", "i"]  # Either e or i
    dims: typing.Dict[str, typing.Any] = {}
    neuron_models: typing.Dict[str, NeuronModel] = {}

    class DataTrait(StructBase.StructBaseTrait):
        N = traitlets.Int()
        fraction = traitlets.Float(0.0)
        ei = traitlets.Unicode()
        # dims = traitlets.Dict(key_trait=traitlets.Unicode())
        dims = traitlets.Unicode()

        def __init__(self, dims={}, **kwargs):
            super().__init__(
                dims=json.dumps(dims, indent=4),
                **kwargs,
            )

    def exclude(self) -> typing.Set[str]:
        return set(["neuron_models"])

    @classmethod
    def trait_ui(cls) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
        return {
            "name": {"type": "text", "label": "Name", "default": ""},
            "N": {"type": "int", "label": "N", "default": 0},
            "fraction": {"type": "float", "label": "Proportion", "default": 0.0},
            "ei": {"type": "text", "label": "E/I", "default": ""},
            "dims": {"type": "textarea", "label": "Property Map", "default": "{\n}"},
        }

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.DataTrait

    def apply_mod(self, mod_neuron: "Neuron") -> "Neuron":
        # Fraction and counts
        if mod_neuron.fraction > 0:
            self.fraction = mod_neuron.fraction
        if mod_neuron.N > 0:
            self.N = mod_neuron.N
        # Neuron dimensions
        for dim_key, dim_value in mod_neuron.dims.items():
            if dim_key not in self.dims:
                self.dims[dim_key] = dim_value
            elif dim_value:
                self.dims[dim_key] = dim_value
        # Neuron models
        for mx_name, neuron_mx in mod_neuron.neuron_models.items():
            if mx_name not in self.neuron_models:
                self.neuron_models[mx_name] = neuron_mx
            else:
                self.neuron_models[mx_name].apply_mod(neuron_mx)
        return self

    def exclude_set(self) -> typing.Set[str]:
        return set(["neuron_models"])


class Region(StructBase):
    inh_fraction: float = 0.0
    region_fraction: float = 0.0
    ncells: int = 0
    inh_ncells: int = 0
    exc_ncells: int = 0
    dims: typing.Dict[str, typing.Any] = {}
    neurons: typing.Dict[str, Neuron] = {}

    class DataTrait(StructBase.StructBaseTrait):
        inh_fraction = traitlets.Float(0.0)
        region_fraction = traitlets.Float(0.0)
        ncells = traitlets.Int()
        inh_ncells = traitlets.Int()
        exc_ncells = traitlets.Int()
        # dims = traitlets.Dict(key_trait=traitlets.Unicode())
        dims = traitlets.Unicode()

        def __init__(self, dims={}, **kwargs):
            super().__init__(
                dims=json.dumps(dims, indent=4),
                **kwargs,
            )

    def exclude(self) -> typing.Set[str]:
        return set(["neurons"])

    @classmethod
    def trait_ui(cls) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
        return {
            "name": {"type": "text", "label": "Name", "default": ""},
            "ncells": {"type": "int", "label": "No. Cells", "default": 0},
            "inh_ncells": {"type": "int", "label": "No. Inh. Cells", "default": 0},
            "exc_ncells": {"type": "int", "label": "No. Exc. Cells", "default": 0},
            "inh_fraction": {"type": "float", "label": "Inh. Fraction", "default": 0.0},
            "region_fraction": {
                "type": "float",
                "label": "Region Fraction",
                "default": 0.0,
            },
            "dims": {"type": "textarea", "label": "Dimensions", "default": "{\n}"},
        }

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.DataTrait

    def apply_mod(self, mod_region: "Region") -> "Region":
        # update fractions
        if mod_region.inh_fraction > 0:
            self.inh_fraction = mod_region.inh_fraction
        if mod_region.region_fraction > 0:
            self.region_fraction = mod_region.region_fraction
        # update ncells
        if mod_region.ncells > 0:
            self.ncells = mod_region.ncells
        if mod_region.inh_ncells > 0:
            self.inh_ncells = mod_region.inh_ncells
        if mod_region.exc_ncells > 0:
            self.exc_ncells = mod_region.exc_ncells
        # update dims
        for dkey, dvalue in mod_region.dims.items():
            if dvalue:
                self.dims[dkey] = dvalue
        # update neuron details
        for nx_name, nx_obj in mod_region.neurons.items():
            if nx_name not in self.neurons:
                self.neurons[nx_name] = nx_obj
            else:
                self.neurons[nx_name].apply_mod(nx_obj)
        return self

    def find_neuron(self, neuron_name) -> Neuron | None:
        if neuron_name in self.neurons:
            return self.neurons[neuron_name]
        return None


class ConnectionModel(StructBase):
    target_model_id: str = ""
    source_model_id: str = ""
    weight_max: float = 0.0
    delay: float = 0.0
    dynamics_params: str = ""
    property_map: typing.Dict = {}

    class DataTrait(StructBase.StructBaseTrait):
        target_model_id = traitlets.Unicode()
        source_model_id = traitlets.Unicode()
        weight_max = traitlets.Float(0.0)
        delay = traitlets.Float(0.0)
        # property_map = traitlets.Dict(key_trait=traitlets.Unicode())
        property_map = traitlets.Unicode()

        def __init__(self, property_map={}, **kwargs):
            super().__init__(
                dims=json.dumps(property_map, indent=4),
                **kwargs,
            )

    def exclude(self) -> typing.Set[str]:
        return set([])

    @classmethod
    def trait_ui(cls) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
        return {
            "name": {"type": "text", "label": "Name", "default": ""},
            "source_model_id": {"type": "text", "label": "Source Id.", "default": ""},
            "target_model_id": {"type": "text", "label": "Target Id.", "default": ""},
            "weight_max": {"type": "float", "label": "Max. Weight", "default": 0.0},
            "delay": {"type": "float", "label": "Delay", "default": 0.0},
            "property_map": {
                "type": "textarea",
                "label": "Property Map",
                "default": "{\n}",
            },
        }

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.DataTrait

    def apply_mod(self, mod_cmd: "ConnectionModel") -> "ConnectionModel":
        # Apply modification
        if mod_cmd.target_model_id:
            self.target_model_id = mod_cmd.target_model_id
        if mod_cmd.source_model_id:
            self.source_model_id = mod_cmd.source_model_id
        if mod_cmd.delay > 0.0:
            self.delay = mod_cmd.delay
        if mod_cmd.weight_max > 0.0:
            self.weight_max = mod_cmd.weight_max
        # Model Property Map
        for pkey, pvalue in mod_cmd.property_map.items():
            if pkey not in self.property_map:
                self.property_map[pkey] = pvalue
            elif pvalue:
                self.property_map[pkey] = pvalue
        return self


class Connection(StructBase):
    pre: typing.Tuple[str, str]
    post: typing.Tuple[str, str]
    probability: float = 0.0
    connect_models: typing.Dict[str, ConnectionModel] = {}
    property_map: typing.Dict = {}

    class DataTrait(StructBase.StructBaseTrait):
        # pre = traitlets.Tuple(traitlets.Unicode(), traitlets.Unicode())
        # post = traitlets.Tuple(traitlets.Unicode(), traitlets.Unicode())
        # property_map = traitlets.Dict(key_trait=traitlets.Unicode())
        pre = traitlets.Unicode()
        post = traitlets.Unicode()
        probability = traitlets.Float(0.0)
        property_map = traitlets.Unicode()

        def __init__(self, pre=(), post=(), property_map={}, **kwargs):
            super().__init__(
                pre=repr(pre),
                post=repr(post),
                property_map=json.dumps(property_map, indent=4),
                **kwargs,
            )

    def exclude(self) -> typing.Set[str]:
        return set(["connect_models"])

    @classmethod
    def trait_ui(cls) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
        return {
            "name": {"type": "text", "label": "Name", "default": ""},
            "pre": {"type": "textarea", "label": "Pre-Synapse", "default": "()"},
            "post": {"type": "textarea", "label": "Post-Synapse", "default": "()"},
            "probability": {"type": "float", "label": "Inh. Fraction", "default": 0.0},
            "property_map": {
                "type": "textarea",
                "label": "Property Map",
                "default": "{\n}",
            },
        }

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.DataTrait

    def apply_mod(self, mod_con: "Connection") -> "Connection":
        if mod_con.pre[0] and mod_con.pre[1]:
            self.pre = mod_con.pre
        if mod_con.post[0] and mod_con.post[1]:
            self.post = mod_con.post
        if mod_con.probability > 0.0:
            self.probability = mod_con.probability
        # Model Property Map
        for pkey, pvalue in mod_con.property_map.items():
            if pkey not in self.property_map:
                self.property_map[pkey] = pvalue
            elif pvalue:
                self.property_map[pkey] = pvalue
        # Models
        for mx_name, mx_obj in mod_con.connect_models.items():
            if mx_name not in self.connect_models:
                self.connect_models[mx_name] = mx_obj
            else:
                self.connect_models[mx_name].apply_mod(mx_obj)
        return self


class ExtNetwork(StructBase):
    ncells: int = 0
    locations: typing.Dict[str, Region] = {}
    connections: typing.Dict[str, Connection] = {}

    class DataTrait(StructBase.StructBaseTrait):
        ncells = traitlets.Int(0)

    def exclude(self) -> typing.Set[str]:
        return set(["locations", "connections"])

    @classmethod
    def trait_ui(cls) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
        return {
            "name": {"type": "text", "label": "Name", "default": ""},
            "ncells": {"type": "int", "label": "No. Cells", "default": 0},
        }

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.DataTrait

    def apply_mod(self, mod_net: "ExtNetwork") -> "ExtNetwork":
        if mod_net.ncells > 0:
            self.ncells = mod_net.ncells
        # Locations
        for c_name, o_cnx in mod_net.locations.items():
            if c_name not in self.locations:
                self.locations[c_name] = o_cnx
                continue
            self.locations[c_name].apply_mod(o_cnx)
        # Connections
        for c_name, o_cnx in mod_net.connections.items():
            if c_name not in self.connections:
                self.connections[c_name] = o_cnx
                continue
            self.connections[c_name].apply_mod(o_cnx)
        return self


class Network(StructBase):
    ncells: int = 0
    locations: typing.Dict[str, Region] = {}
    connections: typing.Dict[str, Connection] = {}
    dims: typing.Dict[str, typing.Any] = {}
    ext_networks: typing.Dict[str, ExtNetwork] = {}

    class DataTrait(StructBase.StructBaseTrait):
        ncells = traitlets.Int(0)
        # dims = traitlets.Dict(key_trait=traitlets.Unicode())
        dims = traitlets.Unicode()

        def __init__(self, dims={}, **kwargs):
            super().__init__(
                dims=json.dumps(dims, indent=4),
                **kwargs,
            )

    def exclude(self) -> typing.Set[str]:
        return set(["locations", "connections", "ext_networks"])

    @classmethod
    def trait_ui(cls) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
        return {
            "name": {"type": "text", "label": "Name", "default": ""},
            "ncells": {"type": "int", "label": "No. Cells", "default": 0},
            "dims": {"type": "textarea", "label": "Dimensions", "default": "{\n}"},
        }

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.DataTrait

    def apply_mod(self, mod_net: "Network") -> "Network":
        # Update dims
        for dkey, dvalue in mod_net.dims.items():
            if dvalue:
                self.dims[dkey] = dvalue
        # Locations
        for c_name, o_cnx in mod_net.locations.items():
            if c_name not in self.locations:
                self.locations[c_name] = o_cnx
                continue
            self.locations[c_name].apply_mod(o_cnx)
        # Connections
        for c_name, o_cnx in mod_net.connections.items():
            if c_name not in self.connections:
                self.connections[c_name] = o_cnx
                continue
            self.connections[c_name].apply_mod(o_cnx)
        # ExtNetwork
        for e_name, e_net in mod_net.ext_networks.items():
            if e_name not in self.ext_networks:
                self.ext_networks[e_name] = e_net
                continue
            self.ext_networks[e_name].apply_mod(e_net)
        return self

    def populate_ncells(self, N: int) -> "Network":
        """
        Populate cell counts from fractions
        """
        self.ncells = N
        for lx, lrx in self.locations.items():
            ncells_region = int(lrx.region_fraction * N)
            ncells_inh = int(lrx.inh_fraction * ncells_region)
            ncells_exc = ncells_region - ncells_inh
            self.locations[lx].ncells = ncells_region
            self.locations[lx].inh_ncells = ncells_inh
            self.locations[lx].exc_ncells = ncells_exc
            for nx, nurx in lrx.neurons.items():
                eix = nurx.ei
                ncells = ncells_inh if eix == "i" else ncells_exc
                ncells = int(ncells * nurx.fraction)
                if ncells == 0:
                    continue
                self.locations[lx].neurons[nx].N = ncells
        return self

    def find_neuron(self, neuron_name) -> Neuron | None:
        for lx, lrx in self.locations.items():
            neuron_obj = lrx.find_neuron(neuron_name)
            if neuron_obj:
                return neuron_obj
        return None


#
# Mapper Abstract Classes
#
class RegionMapper(abc.ABC):
    @abc.abstractmethod
    def __init__(self, name: str, desc: typing.Dict[str, typing.Dict]):
        return None

    @abc.abstractmethod
    def neuron_names(self) -> typing.List[str]:
        return []

    @abc.abstractmethod
    def map(self, region_neurons: typing.Dict[str, Neuron]) -> Region | None:
        return None


class NeuronMapper(abc.ABC):
    @abc.abstractmethod
    def __init__(self, name: str, desc: typing.Dict[str, typing.Dict]):
        return None

    @abc.abstractmethod
    def map(self) -> Neuron | None:
        return None


class ConnectionMapper(abc.ABC):
    @abc.abstractmethod
    def __init__(self, name: str, desc: typing.Dict[str, typing.Dict]):
        return None

    @abc.abstractmethod
    def map(self) -> Connection | None:
        return None


#
#
def srcdata2network(
    network_desc: typing.Dict,
    model_name: str,
    desc2region_mapper: type[RegionMapper],
    desc2neuron_mapper: type[NeuronMapper],
    desc2connection_mapper: type[ConnectionMapper],
) -> Network:
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
    return Network(
        name=model_name,
        locations=loc_struct,
        connections=conn_struct,
    )


def subset_network(net_stats: Network, region_list: typing.List[str]) -> Network:
    sub_locs = {k: v for k, v in net_stats.locations.items() if k in region_list}
    return Network(name=net_stats.name, dims=net_stats.dims, locations=sub_locs)


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


#
# Example Nework
#
def example_network() -> Network:
    return Network(
        name="v1",
        locations={
            "VISp1": Region(
                name="VISp1",
                inh_fraction=0.4051546391752577,
                region_fraction=0.0696625945317044,
                neurons={
                    "Sst": Neuron(ei="i", fraction=0.0356234096692111),
                    "Lamp5": Neuron(ei="i", fraction=0.7201017811704835),
                    "Sst-Chodl": Neuron(ei="i", fraction=0.0076335877862595),
                    "Pvalb": Neuron(ei="i", fraction=0.0381679389312977),
                    "Vip": Neuron(ei="i", fraction=0.1475826972010178),
                    "GABA-Other": Neuron(ei="i", fraction=0.0508905852417302),
                    "IT": Neuron(ei="e", fraction=0.9896013864818024),
                    "ET": Neuron(ei="e", fraction=0.0),
                    "CT": Neuron(ei="e", fraction=0.0),
                    "NP": Neuron(ei="e", fraction=0.0),
                    "Glut-Other": Neuron(ei="e", fraction=0.0103986135181975),
                },
            ),
            "VISp2/3": Region(
                name="VISp2/3",
                inh_fraction=0.0787551960453881,
                region_fraction=0.3486199987072587,
                neurons={
                    "Sst": Neuron(ei="i", fraction=0.1619115549215406),
                    "Lamp5": Neuron(ei="i", fraction=0.1583452211126961),
                    "Sst-Chodl": Neuron(ei="i", fraction=0.0021398002853067),
                    "Pvalb": Neuron(ei="i", fraction=0.3323823109843081),
                    "Vip": Neuron(ei="i", fraction=0.3166904422253923),
                    "GABA-Other": Neuron(ei="i", fraction=0.028530670470756),
                    "IT": Neuron(ei="e", fraction=1.0),
                    "ET": Neuron(ei="e", fraction=0.0),
                    "CT": Neuron(ei="e", fraction=0.0),
                    "NP": Neuron(ei="e", fraction=0.0),
                    "Glut-Other": Neuron(ei="e", fraction=0.0),
                },
            ),
            "VISp4": Region(
                name="VISp4",
                inh_fraction=0.1119157340355497,
                region_fraction=0.2096987912869239,
                neurons={
                    "Sst": Neuron(ei="i", fraction=0.315126050420168),
                    "Lamp5": Neuron(ei="i", fraction=0.0184873949579831),
                    "Sst-Chodl": Neuron(ei="i", fraction=0.0),
                    "Pvalb": Neuron(ei="i", fraction=0.5327731092436975),
                    "Vip": Neuron(ei="i", fraction=0.1319327731092437),
                    "GABA-Other": Neuron(ei="i", fraction=0.0016806722689075),
                    "IT": Neuron(ei="e", fraction=0.9626178121359736),
                    "ET": Neuron(ei="e", fraction=0.0293338981255956),
                    "CT": Neuron(ei="e", fraction=0.0002117970983797),
                    "NP": Neuron(ei="e", fraction=0.0074128984432913),
                    "Glut-Other": Neuron(ei="e", fraction=0.0004235941967595),
                },
            ),
            "VISp5": Region(
                name="VISp5",
                inh_fraction=0.165427954926876,
                region_fraction=0.1776064895611143,
                neurons={
                    "Sst": Neuron(ei="i", fraction=0.4557971014492754),
                    "Lamp5": Neuron(ei="i", fraction=0.022463768115942),
                    "Sst-Chodl": Neuron(ei="i", fraction=0.0065217391304347),
                    "Pvalb": Neuron(ei="i", fraction=0.4876811594202898),
                    "Vip": Neuron(ei="i", fraction=0.0217391304347826),
                    "GABA-Other": Neuron(ei="i", fraction=0.0057971014492753),
                    "IT": Neuron(ei="e", fraction=0.5212582591209423),
                    "ET": Neuron(ei="e", fraction=0.3230393565067509),
                    "CT": Neuron(ei="e", fraction=0.0439528871014076),
                    "NP": Neuron(ei="e", fraction=0.1041367423154266),
                    "Glut-Other": Neuron(ei="e", fraction=0.0076127549554725),
                },
            ),
            "VISp6a": Region(
                name="VISp6a",
                inh_fraction=0.0627792416084316,
                region_fraction=0.163661043242195,
                neurons={
                    "Sst": Neuron(ei="i", fraction=0.3485401459854014),
                    "Lamp5": Neuron(ei="i", fraction=0.0255474452554744),
                    "Sst-Chodl": Neuron(ei="i", fraction=0.010948905109489),
                    "Pvalb": Neuron(ei="i", fraction=0.5620437956204379),
                    "Vip": Neuron(ei="i", fraction=0.0383211678832116),
                    "GABA-Other": Neuron(ei="i", fraction=0.0145985401459854),
                    "IT": Neuron(ei="e", fraction=0.2159882654932159),
                    "ET": Neuron(ei="e", fraction=0.0006111722283339),
                    "CT": Neuron(ei="e", fraction=0.7593203764820926),
                    "NP": Neuron(ei="e", fraction=0.0053783156093387),
                    "Glut-Other": Neuron(ei="e", fraction=0.0187018701870187),
                },
            ),
            "VISp6b": Region(
                name="VISp6b",
                inh_fraction=0.0529100529100529,
                region_fraction=0.0307510826708034,
                neurons={
                    "Sst": Neuron(ei="i", fraction=0.275),
                    "Lamp5": Neuron(ei="i", fraction=0.0875),
                    "Sst-Chodl": Neuron(ei="i", fraction=0.075),
                    "Pvalb": Neuron(ei="i", fraction=0.475),
                    "Vip": Neuron(ei="i", fraction=0.0375),
                    "GABA-Other": Neuron(ei="i", fraction=0.05),
                    "IT": Neuron(ei="e", fraction=0.0467877094972067),
                    "ET": Neuron(ei="e", fraction=0.0),
                    "CT": Neuron(ei="e", fraction=0.7255586592178771),
                    "NP": Neuron(ei="e", fraction=0.0),
                    "Glut-Other": Neuron(ei="e", fraction=0.2276536312849162),
                },
            ),
        },
    )
