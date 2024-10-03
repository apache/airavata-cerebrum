import logging
import pathlib
import typing
import pydantic
import matplotlib
import mousev1.model as v1model
import mousev1.operations as v1ops
from airavata_cerebrum.util.desc_config import ModelDescConfig
from airavata_cerebrum.model.desc import ModelDescription

logging.basicConfig(level=logging.INFO)


class CfgSettings(pydantic.BaseModel):
    name: str = "v1l4"
    base_dir: pathlib.Path = pathlib.Path("./")
    config_files: typing.Dict[str, typing.List[str | pathlib.Path]] = {"config": ["config.json"]}
    config_dir: pathlib.Path = pathlib.Path("./v1l4/description/")
    custom_mod: pathlib.Path = pathlib.Path("./v1l4/description/custom_mod.json")
    ctdb_models_dir: pathlib.Path = pathlib.Path("./v1l4/components/point_neuron_models/")
    nest_models_dir: pathlib.Path = pathlib.Path("./v1l4/components/cell_models/")
    save_flag: bool = False


def model_desc(cfg_set: CfgSettings):
    md_config = ModelDescConfig(
        name=cfg_set.name,
        base_dir=cfg_set.base_dir,
        config_files=cfg_set.config_files,
        config_dir=cfg_set.config_dir,
        create_model_dir=True,
    )
    return ModelDescription(
        config=md_config,
        region_mapper=v1model.V1RegionMapper,
        neuron_mapper=v1model.V1NeuronMapper,
        connection_mapper=v1model.V1ConnectionMapper,
        network_builder=v1model.V1BMTKNetworkBuilder,
        custom_mod=cfg_set.custom_mod,
        save_flag=cfg_set.save_flag,
    )

def struct_bmtk(cfg_set: CfgSettings):
    md_dex = model_desc(cfg_set)
    md_dex.build_net_struct()
    md_dex.apply_custom_mod()
    md_dex.build_bmtk()

def build_bmtk(cfg_set: CfgSettings):
    md_dex = model_desc(cfg_set)
    md_dex.download_db_data()
    md_dex.db_post_ops()
    md_dex.map_source_data()
    md_dex.build_net_struct()
    md_dex.apply_custom_mod()
    md_dex.build_bmtk()

def convert_models_to_nest(cfg_set: CfgSettings):
    v1ops.convert_ctdb_models_to_nest(cfg_set.ctdb_models_dir,
                                      cfg_set.nest_models_dir)

if __name__ == "__main__":
    cfg_set = CfgSettings()
    convert_models_to_nest(cfg_set)
    # build_bmtk(cfg_set)
    struct_bmtk(cfg_set)
