import logging
import pathlib
import typing
import os

from ..util import io as cbmio
from ..util.desc_config import CfgKeys, ModelDescConfig
from . import structure
from .. import workflow


def _log():
    return logging.getLogger(__name__)


# File paths
class DescPaths:
    DESCRIPTION_DIR = "description"


class ModelDescription:
    def __init__(
        self,
        config: ModelDescConfig,
        region_mapper: typing.Type,
        neuron_mapper: typing.Type,
        connection_mapper: typing.Type,
        network_builder: typing.Type,
        custom_mod: str | pathlib.Path | None = None,
        save_flag: bool = True,
        out_format: typing.Literal["json", "yaml", "yml"] = "json",
    ) -> None:
        self.config = config
        self.region_mapper = region_mapper
        self.neuron_mapper = neuron_mapper
        self.connection_mapper = connection_mapper
        self.network_builder = network_builder
        self.custom_mod = custom_mod
        self.save_flag = save_flag
        self.out_format = out_format
        self.desc_dir = pathlib.Path(self.config.model_dir,
                                     DescPaths.DESCRIPTION_DIR)
        if not os.path.exists(self.desc_dir):
            os.makedirs(self.desc_dir)
        self.model_struct = structure.Network(name=self.config.name)

    def output_location(self, key: str) -> pathlib.Path:
        file_name = self.config.out_prefix(key)
        out_path = pathlib.Path(self.desc_dir, file_name)
        return out_path.with_suffix("." + self.out_format)

    def download_db_data(self) -> typing.Dict[str, typing.Any]:
        db_src_config = self.config.get_config(CfgKeys.SRC_DATA)
        _log().info("Start Query and Download Data")
        db_connect_output = workflow.run_db_connect_workflows(db_src_config)
        if self.save_flag:
            cbmio.dump(
                db_connect_output,
                self.output_location(CfgKeys.DB_CONNECT),
                indent=4,
            )
        _log().info("Completed Query and Download Data")
        return db_connect_output

    def db_post_ops(self):
        db_connect_key = CfgKeys.DB_CONNECT
        db_datasrc_key = CfgKeys.SRC_DATA
        db_connect_data = cbmio.load(self.output_location(db_connect_key))
        db_src_config = self.config.get_config(CfgKeys.SRC_DATA)
        db_post_op_data = None
        if db_connect_data:
            db_post_op_data = workflow.run_ops_workflows(
                db_connect_data, db_src_config, CfgKeys.POST_OPS
            )
        if self.save_flag and db_post_op_data:
            cbmio.dump(db_post_op_data, self.output_location(db_datasrc_key), indent=4)
        return db_post_op_data

    def map_source_data(self):
        db2model_map = self.config.get_config(CfgKeys.DB2MODEL_MAP)
        db_lox_map = db2model_map[CfgKeys.LOCATIONS]
        db_conn_map = db2model_map[CfgKeys.CONNECTIONS]
        db_source_data = cbmio.load(self.output_location(CfgKeys.SRC_DATA))
        srcdata_map_output = None
        if db_source_data:
            db2location_output = workflow.map_srcdata_locations(db_source_data, db_lox_map)
            db2connect_output = workflow.map_srcdata_connections(db_source_data, db_conn_map)
            srcdata_map_output = {
                "locations": db2location_output,
                "connections": db2connect_output,
            }
        if self.save_flag and srcdata_map_output:
            cbmio.dump(
                srcdata_map_output,
                self.output_location(CfgKeys.DB2MODEL_MAP),
                indent=4,
            )
        return srcdata_map_output

    def build_net_struct(self):
        network_desc_output = cbmio.load(self.output_location(CfgKeys.DB2MODEL_MAP))
        if not network_desc_output:
            return None
        self.model_struct = structure.srcdata2network(
            network_desc_output,
            self.config.name,
            self.region_mapper,
            self.neuron_mapper,
            self.connection_mapper,
        )
        return self.model_struct

    def apply_custom_mod(self):
        import airavata_cerebrum.model.structure as structure

        if self.custom_mod:
            mod_struct = structure.Network.model_validate(cbmio.load(self.custom_mod))
            # Update user preference
            self.model_struct = self.model_struct.apply_mod(mod_struct)
        # Estimate NCells from the fractions
        self.model_struct.populate_ncells(30000)
        return self.model_struct

    def build_bmtk(self):
        # Construct model
        net_builder = self.network_builder(self.model_struct)
        bmtk_net = net_builder.build()
        bmtk_net.save(str(self.config.model_dir))
