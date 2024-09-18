import logging
import airavata_cerebrum.model.mousev1 as mousev1
from airavata_cerebrum.util.desc_config import ModelDescConfig
from airavata_cerebrum.model.desc import ModelDescription

logging.basicConfig(level=logging.INFO)


def v1_model_desc_config(
    name="v1l4",
    base_dir="./",
    config_files={"config": "config.json"},
    config_dir="./v1l4/description/",
):
    return ModelDescConfig(name, base_dir, config_files, config_dir, True)


def v1l4_model_desc(
    name="v1l4",
    base_dir="./",
    config_files={"config": "config.json"},
    config_dir="./v1l4/description/",
    save_output=False,
):
    model_custom_mod = "./v1l4/description/custom_mod.json"
    return ModelDescription(
        v1_model_desc_config(name, base_dir, config_files, config_dir),
        mousev1.V1RegionMapper,
        mousev1.V1NeuronMapper,
        mousev1.V1ConnectionMapper,
        mousev1.V1BMTKNetworkBuilder,
        model_custom_mod,
        save_output,
    )


def main():
    model_dex = v1l4_model_desc()
    model_dex.download_db_data()
    model_dex.db_post_ops()
    model_dex.map_source_data()
    model_dex.build_net_struct()
    model_dex.apply_custom_mod()
    model_dex.build_bmtk()


# if __name__ == "__main__":
#     main()

# model_dex = abm_ct_model()
# network_desc_output = model_dex.map_db_data_locations()
# net_model = model_dex.atlasdata2netstruct()
