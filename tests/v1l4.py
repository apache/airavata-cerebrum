import logging
import json
import typing
import os
import pathlib
from airavata_cerebrum.atlas.data.base import (
    run_db_conn_workflows,
    run_db_conn_xformers,
    dbconn2locations,
    load_json,
    save_json,
    ModelDescConfig
)
import airavata_cerebrum.atlas.operations.netops as netops
import airavata_cerebrum.atlas.model.structure as structure
import airavata_cerebrum.atlas.model.mousev1 as mousev1

logging.basicConfig(level=logging.INFO)


class ModelDescription:
    def output_location(self, key: str):
        file_name = self.model_config.output_json(key)
        return pathlib.PurePath(self.model_desc_dir, file_name)

    def __init__(
        self,
        model_config: ModelDescConfig,
        model_base: str,
        model_name: str,
        desc2region_mapper: typing.Callable,
        desc2neuron_mapper: typing.Callable,
        model_patch: str | pathlib.Path | None = None,
        save_output: bool = True,
    ) -> None:
        self.model_config = model_config
        self.model_name = model_name
        self.desc2region_mapper = desc2region_mapper
        self.desc2neuron_mapper = desc2neuron_mapper
        self.model_base = model_base
        self.model_patch = model_patch
        self.save_output = save_output
        self.model_dir = pathlib.PurePath(model_base, model_name)
        self.model_desc_dir = pathlib.PurePath(self.model_dir, "description")
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        if not os.path.exists(self.model_desc_dir):
            os.makedirs(self.model_dir)
        self.net_model = structure.Network(name=self.model_name)

    def download_db_data(self):
        db_connect_config = self.model_config.get_config(ModelDescConfig.DB_CONNECT_KEY)
        db_connect_output = run_db_conn_workflows(db_connect_config)
        if self.save_output:
            save_json(db_connect_output,
                      self.output_location(ModelDescConfig.DB_CONNECT_KEY), indent=4)
        return db_connect_output

    def xform_db_data(self):
        db_connect_key = ModelDescConfig.DB_CONNECT_KEY
        db_xform_key = ModelDescConfig.DB_XFORM_KEY
        db_connect_data = load_json(self.output_location(db_connect_key))
        db_xform_config = self.model_config.get_config(db_xform_key)
        db_xformed_data = run_db_conn_xformers(db_connect_data, db_xform_config)
        if self.save_output:
            save_json(db_xformed_data, self.output_location(db_xform_key), indent=4)
        return db_xformed_data

    def map_db_data_locations(self):
        db_loc_map_key = ModelDescConfig.DB_LOCATION_MAP_KEY
        db_xform_key = ModelDescConfig.DB_XFORM_KEY
        db_location_map = self.model_config.get_config(db_loc_map_key)
        db_xformed_data = load_json(self.output_location(db_xform_key))
        network_desc_output = dbconn2locations(db_xformed_data, db_location_map)
        if self.save_output:
            save_json(
                network_desc_output, self.output_location(db_loc_map_key), indent=4
            )
        return network_desc_output

    def atlasdata2netstruct(self):
        network_desc_output = load_json(
            self.output_location(ModelDescConfig.DB_XFORM_KEY)
        )
        self.net_model = netops.atlasdata2network(
            network_desc_output,
            self.model_name,
            self.desc2region_mapper,
            self.desc2neuron_mapper,
        )
        return self.net_model

    def update_user_input(self):
        import airavata_cerebrum.atlas.model.structure as structure

        if self.model_patch:
            #
            user_update = structure.Network.model_validate(
                load_json(self.model_patch)
            )
            # Update user preference
            self.net_model = netops.update_user_input(self.net_model, user_update)
            # pprint.pp(net_model.model_dump())
            # print("----------------------")
        #
        # NCells
        self.net_model = netops.fractions2ncells(self.net_model, 30000)
        # pprint.pp(net_model.model_dump())
        # print("----------------------")
        return self.net_model

    def build_bmtk(self):
        import airavata_cerebrum.atlas.model.builder as builder

        #
        #
        # Construct model
        bmtk_net = builder.add_nodes_cylinder(self.net_model)
        bmtk_net.save(str(self.model_dir))


def abm_ct_model():
    model_cfg = ModelDescConfig({"config": "config.json"})
    model_base_dir = "./"
    model_name = "v1l4"
    model_patch = "v1l4/description/model_patch.json"
    return ModelDescription(
        model_cfg,
        model_base_dir,
        model_name,
        mousev1.V1ModelDesc2Region,
        mousev1.V1ModelDesc2Neuron,
        model_patch,
        False,
    )


def main():
    model_dex = abm_ct_model()
    model_dex.download_db_data()
    model_dex.xform_db_data()
    model_dex.map_db_data_locations()
    model_dex.atlasdata2netstruct()
    model_dex.update_user_input()
    model_dex.build_bmtk()


# if __name__ == "__main__":
#     main()

model_dex = abm_ct_model()
network_desc_output = model_dex.map_db_data_locations()
net_model = model_dex.atlasdata2netstruct()
