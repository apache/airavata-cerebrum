import logging
import pathlib
import typing
import pydantic
import matplotlib
import mousev1.model as mousev1
from airavata_cerebrum.util.desc_config import ModelDescConfig
from airavata_cerebrum.model.desc import ModelDescription

logging.basicConfig(level=logging.INFO)


class CfgSettings(pydantic.BaseModel):
    name: str = "v1l4"
    base_dir: pathlib.Path = pathlib.Path("./")
    config_files: typing.Dict[str, typing.List[str | pathlib.Path]] = {"config": ["config.json"]}
    config_dir: pathlib.Path = pathlib.Path("./v1l4/description/")
    custom_mod: pathlib.Path = pathlib.Path("./v1l4/description/custom_mod.json")
    save_flag: bool = False


def m_desc(cfg_set: CfgSettings):
    md_config = ModelDescConfig(
        name=cfg_set.name,
        base_dir=cfg_set.base_dir,
        config_files=cfg_set.config_files,
        config_dir=cfg_set.config_dir,
        create_model_dir=True,
    )
    return ModelDescription(
        config=md_config,
        region_mapper=mousev1.V1RegionMapper,
        neuron_mapper=mousev1.V1NeuronMapper,
        connection_mapper=mousev1.V1ConnectionMapper,
        network_builder=mousev1.V1BMTKNetworkBuilder,
        custom_mod=cfg_set.custom_mod,
        save_flag=cfg_set.save_flag,
    )

def struct_bmtk():
    md_dex = m_desc(CfgSettings())
    md_dex.build_net_struct()
    md_dex.apply_custom_mod()
    md_dex.build_bmtk()

def build_bmtk():
    md_dex = m_desc(CfgSettings())
    md_dex.download_db_data()
    md_dex.db_post_ops()
    md_dex.map_source_data()
    md_dex.build_net_struct()
    md_dex.apply_custom_mod()
    md_dex.build_bmtk()


if __name__ == "__main__":
     struct_bmtk()

# model_dex = abm_ct_model()
# network_desc_output = model_dex.map_db_data_locations()
# net_model = model_dex.atlasdata2netstruct()
