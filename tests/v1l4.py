import matplotlib
import logging
import typing
import os
import pathlib
from airavata_cerebrum.workflow import (
    run_db_connect_workflows,
    run_ops_workflows,
    map_srcdata_locations,
)
import airavata_cerebrum.util.io as cbmio
import airavata_cerebrum.model.desc as cbmdesc
import airavata_cerebrum.operations.netops as netops
import airavata_cerebrum.model.structure as structure
import airavata_cerebrum.model.mousev1 as mousev1

logging.basicConfig(level=logging.INFO)


class ModelDescription:
    def __init__(
        self,
        config: cbmdesc.ModelDescConfig,
        region_mapper: typing.Callable,
        neuron_mapper: typing.Callable,
        custom_mod: str | pathlib.Path | None = None,
        save_flag: bool = True,
        out_format: str = "json"
    ) -> None:
        self.config = config
        self.region_mapper = region_mapper
        self.neuron_mapper = neuron_mapper
        self.custom_mod = custom_mod
        self.save_flag = save_flag
        self.out_format = out_format
        self.desc_dir = pathlib.PurePath(self.config.model_dir,
                                         cbmdesc.DESCRIPTION_DIR)
        if not os.path.exists(self.desc_dir):
            os.makedirs(self.desc_dir)
        self.model_struct = structure.Network(name=self.config.name)

    def output_location(self, key: str):
        file_name = self.config.out_prefix(key)
        out_path = pathlib.PurePath(self.desc_dir, file_name)
        return out_path.with_suffix("." + self.out_format)

    def download_db_data(self):
        db_src_config = self.config.get_config(cbmdesc.DB_DATA_SRC_KEY)
        db_connect_output = run_db_connect_workflows(db_src_config)
        if self.save_flag:
            cbmio.dump(db_connect_output,
                       self.output_location(cbmdesc.DB_CONNECT_KEY),
                       indent=4)
        return db_connect_output

    def db_post_ops(self):
        db_connect_key = cbmdesc.DB_CONNECT_KEY
        db_datasrc_key = cbmdesc.DB_DATA_SRC_KEY
        db_connect_data = cbmio.load(self.output_location(db_connect_key))
        db_src_config = self.config.get_config(cbmdesc.DB_DATA_SRC_KEY)
        db_post_op_data = None
        if db_connect_data:
            db_post_op_data = run_ops_workflows(db_connect_data,
                                                db_src_config,
                                                cbmdesc.DB_POSTOP_KEY)
        if self.save_flag and db_post_op_data:
            cbmio.dump(db_post_op_data,
                       self.output_location(db_datasrc_key),
                       indent=4)
        return db_post_op_data

    def map_srcdata2locations(self):
        db_loc_map_key = cbmdesc.DB2MODEL_MAP_KEY
        db2model_map = self.config.get_config(cbmdesc.DB2MODEL_MAP_KEY)
        db_location_map = db2model_map[cbmdesc.LOCATIONS_KEY]
        db_source_data = cbmio.load(self.output_location(cbmdesc.DB_DATA_SRC_KEY))
        db2location_output = None
        if db_source_data:
            db2location_output = map_srcdata_locations(db_source_data,
                                                       db_location_map)
        if self.save_flag and db2location_output:
            cbmio.dump(
                db2location_output, self.output_location(db_loc_map_key), indent=4
            )
        return db2location_output

    def map_locdata2netstruct(self):
        network_desc_output = cbmio.load(
            self.output_location(cbmdesc.DB2MODEL_MAP_KEY)
        )
        self.model_struct = netops.src_data2network(
            network_desc_output,
            self.config.name,
            self.region_mapper,
            self.neuron_mapper,
        )
        return self.model_struct

    def apply_custom_mod(self):
        import airavata_cerebrum.model.structure as structure

        if self.custom_mod:
            #
            mod_struct = structure.Network.model_validate(
                cbmio.load(self.custom_mod)
            )
            # Update user preference
            self.model_struct = netops.apply_custom_mod(self.model_struct, mod_struct)
            # pprint.pp(net_model.model_dump())
            # print("----------------------")
        #
        # NCells
        self.model_struct = netops.fractions2ncells(self.model_struct, 30000)
        # pprint.pp(net_model.model_dump())
        # print("----------------------")
        return self.model_struct

    def build_bmtk(self):
        import airavata_cerebrum.model.builder as builder

        #
        #
        # Construct model
        bmtk_net = builder.add_nodes_cylinder(self.model_struct)
        bmtk_net.save(str(self.config.model_dir))


def v1_model_desc_config(name="v1l4", base_dir="./",
                         config_files={"config": "config.json"},
                         config_dir="./v1l4/description/"):
    return cbmdesc.ModelDescConfig(
        name,
        base_dir,
        config_files,
        config_dir,
        True
    )


def v1l4_model_desc(save_output=False):
    model_custom_mod = "./v1l4/description/custom_mod.json"
    return ModelDescription(
        v1_model_desc_config(),
        mousev1.V1RegionMapper,
        mousev1.V1NeuronMapper,
        model_custom_mod,
        True,
    )


def main():
    model_dex = v1l4_model_desc()
    model_dex.download_db_data()
    model_dex.db_post_ops()
    model_dex.map_srcdata2locations()
    model_dex.map_locdata2netstruct()
    model_dex.apply_custom_mod()
    model_dex.build_bmtk()


# if __name__ == "__main__":
#     main()

# model_dex = abm_ct_model()
# network_desc_output = model_dex.map_db_data_locations()
# net_model = model_dex.atlasdata2netstruct()
