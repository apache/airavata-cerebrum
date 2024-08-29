import logging
import json
import os
import pathlib
from airavata_cerebrum.atlas.data.base import (
    run_db_conn_workflows,
    run_db_conn_xformers,
    dbconn2locations,
)
import airavata_cerebrum.atlas.operations.netops as netops
import airavata_cerebrum.atlas.model.structure as structure
import airavata_cerebrum.atlas.model.mousev1 as mousev1

logging.basicConfig(level=logging.INFO)


def load_json(file_name):
    with open(file_name) as in_fptr:
        return json.load(in_fptr)


def save_json(json_obj, file_name, indent):
    with open(file_name, "w") as out_fptr:
        json.dump(json_obj, out_fptr, indent=indent)


class ModelDescription:
    description_files = {
        "db_connections" : "db_connect.json",
        "db_select_xform" : "db_select_xform.json",
        "db_location_map" : "db_location_map.json",
        "db_connections_output": "db_connect_output.json",
        "db_select_xform_output" : "db_select_xform_output.json",
        "network_desc_output" : "network_desc_output.json"
    }

    def location(self, key):
        file_name = self.description_files[key]
        return pathlib.PurePath(self.model_desc_dir, file_name)

    def __init__(self, model_base, model_name,
                 desc2region_mapper, desc2neuron_mapper,
                 user_update_config=None,
                 save_output=True) -> None:
        self.model_name = model_name
        self.desc2region_mapper = desc2region_mapper
        self.desc2neuron_mapper = desc2neuron_mapper
        self.model_base = model_base
        self.user_update_config = user_update_config
        self.save_output = save_output
        self.model_dir = pathlib.PurePath(model_base, model_name)
        self.model_desc_dir = pathlib.PurePath(self.model_dir, "description")
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        if not os.path.exists(self.model_desc_dir):
            os.makedirs(self.model_dir)
        self.net_model = structure.Network(name=self.model_name)

    def download_db_data(self):
        db_connect_config = load_json(self.location("db_connections"))
        db_connect_output = run_db_conn_workflows(db_connect_config["db_connections"])
        if self.save_output:
            save_json(db_connect_output, self.location("db_connections_output"),
                      indent=4)
        return db_connect_output

    def xform_db_data(self):
        db_connect_data = load_json(self.location("db_connections_output"))
        db_xform_config = load_json(self.location("db_select_xform"))
        db_xformed_data = run_db_conn_xformers(db_connect_data, db_xform_config)
        if self.save_output:
            save_json(db_xformed_data, self.location("db_select_xform_output"),
                      indent=4)
        return db_xformed_data

    def map_db_data_locations(self):
        db_location_map = load_json(self.location("db_location_map"))
        db_xformed_data = load_json(self.location("db_select_xform_output"))
        network_desc_output = dbconn2locations(db_xformed_data, db_location_map)
        if self.save_output:
            save_json(network_desc_output, self.location("network_desc_output"),
                      indent=4)
        return network_desc_output

    def atlasdata2netstruct(self):
        network_desc_output = load_json(self.location("network_desc_output"))
        self.net_model = netops.atlasdata2network(network_desc_output,
                                                  self.model_name,
                                                  self.desc2region_mapper,
                                                  self.desc2neuron_mapper)
        return self.net_model

    def update_user_input(self):
        import airavata_cerebrum.atlas.model.structure as structure
        #
        user_update = structure.Network.model_validate(load_json(self.user_update_config))
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
    model_base = "./"
    model_name = "abm_ct"
    user_update_config = "abm_ct/description/user_location_config.json"
    return ModelDescription(model_base, model_name,
                            mousev1.V1ModelDesc2Region,
                            mousev1.V1ModelDesc2Neuron,
                            user_update_config, False)


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
