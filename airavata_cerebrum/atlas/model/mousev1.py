import typing
import jsonpath
from ..log.logging import LOGGER
from . import structure


class V1ModelDesc2Region:
    def __init__(self, region_desc):
        self.region_desc = region_desc
        self.region_meta = self.region_desc["region_meta"]
        self.region_meta_abc = self.region_meta[
            "airavata_cerebrum.atlas.data.abc_mouse"
        ][0]

    def neuron_list(self):
        return self.region_meta["property_map"]["neurons"]

    def inh_fraction(self):
        return float(self.region_meta_abc["inh_fraction"])

    def region_fraction(self):
        return float(self.region_meta_abc["region_fraction"])


class V1ModelDesc2Neuron:
    abc_ptr = jsonpath.JSONPointer("/airavata_cerebrum.atlas.data.abc_mouse/0")
    ct_ptr = jsonpath.JSONPointer("/airavata_cerebrum.atlas.data.abm_celltypes")
    ev_ptr = jsonpath.JSONPointer(
        "/glif/neuronal_models/0/neuronal_model_runs/0/explained_variance_ratio"
    )

    def __init__(self, neuron_desc):
        self.neuron_desc = neuron_desc
        self.ct_data: typing.Iterable | None = None
        self.abc_data: typing.Iterable | None = None
        if self.abc_ptr.exists(neuron_desc):
            self.abc_data = self.abc_ptr.resolve(neuron_desc)  # type:ignore
        else:
            self.abc_data = None
        if self.abc_data is None:
            LOGGER.error("Can not find ABC Pointer in Model Description")
        if self.ct_ptr.exists(neuron_desc):
            self.ct_data = self.ct_ptr.resolve(neuron_desc)  # type: ignore
        else:
            self.ct_data = None
        if self.ct_data is None:
            LOGGER.error("Can not find ABM CT Pointer in Model Description")

    def map(self) -> typing.Union[structure.Neuron, None]:
        ntype = self.neuron_desc["property_map"]["ei"]
        if not self.abc_data:
            return structure.Neuron(ei=ntype)
        nfrac = self.abc_data["fraction"]  # type:  ignore
        if not self.ct_data:
            return structure.Neuron(ei=ntype, fraction=float(nfrac))
        neuron_models = []
        for mdesc in self.ct_data:
            spec_id = mdesc["ct"]["specimen__id"]
            m_type = "point_process"
            m_template = "nrn:IntFire1"
            params_file = str(spec_id) + "_glif_lif_asc_config.json"
            property_map = {"explained_variance_ratio": self.ev_ptr.resolve(mdesc)}
            nmodel = structure.NeuronModel(
                id=spec_id,
                m_type=m_type,
                template=m_template,
                dynamics_params=params_file,
                property_map=property_map,
            )
            neuron_models.append(nmodel)
        return structure.Neuron(
            ei=ntype, fraction=float(nfrac), neuron_models=neuron_models
        )
