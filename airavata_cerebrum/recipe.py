import logging
import typing as t
import os
#
import pydantic
#
from pathlib import Path
from . import workflow
from .util import io as cbmio, merge_dict_inplace
from .model import structure
from .const import RecipeKeys


def _log():
    return logging.getLogger(__name__)


#
# Class for structure of Recipes
class RecipeSetup(pydantic.BaseModel):
    recipe_dir: str | Path = Path(".")
    recipe_output_dir: str | Path | None = None
    recipe_sections: dict[str, t.Any] = {}
    recipe_templates: dict[str, t.Any] = {}
    recipe_files: dict[str, list[str | Path]]
    #
    create_model_dir: bool = False
    name: str
    base_dir: str | Path

    @property
    def model_dir(self) -> Path:
        return Path(self.base_dir, self.name)

    @property
    def output_dir(self) -> Path:
        return Path(
            self.recipe_output_dir if self.recipe_output_dir else self.recipe_dir
        )

    @property
    def network_dir(self) -> Path:
        return Path(self.base_dir, self.name, RecipeKeys.NETWORK)

    def __init__(self, **kwargs: t.Any):
        super().__init__(**kwargs)
        self.load_recipe()
        # Recipe View Templates
        self.load_templates()
        # Create model directory
        if self.create_model_dir and not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)

    def load_recipe(self):
        # Load if recipe available, load sections otherwise
        if RecipeKeys.RECIPE in self.recipe_files:
            self.load_sections()
        else:
            try:
                self.load_section_list()
            except KeyError:
                _log().error(
                    "Failed to find one of two Recipe Keys: [%s]",
                    str(RecipeKeys.RECIPE_SECTIONS)
                )

    def load_templates(self):
        if RecipeKeys.TEMPLATES in self.recipe_files:
            # _log().warning("Loading View Templates")
            for t_file in self.recipe_files[RecipeKeys.TEMPLATES]:
                t_dict = cbmio.load(self.recipe_file_path(t_file))
                if t_dict:
                    merge_dict_inplace(
                        self.recipe_templates,
                        t_dict
                    )

    def recipe_file_path(self, file_name: str | Path) -> str | Path:
        if self.recipe_dir:
            return Path(self.recipe_dir, file_name)
        return file_name

    def recipe_output_prefix(self, cfg_key: str) -> str:
        return cfg_key + "_output"

    def get_section(self, cfg_key: str) -> dict[str, t.Any]:
        return self.recipe_sections[cfg_key]

    def load_sections(self) -> None:
        for rcp_file in self.recipe_files[RecipeKeys.RECIPE]:
            rcp_dict = cbmio.load(self.recipe_file_path(rcp_file))
            if rcp_dict and self.recipe_sections:
                merge_dict_inplace(
                    self.recipe_sections,
                    rcp_dict
                )
            elif rcp_dict:
                self.recipe_sections = rcp_dict

    def load_section_list(
        self,
    ) -> None:
        for rcp_key in RecipeKeys.RECIPE_SECTIONS:
            for rcp_file in self.recipe_files[rcp_key]:
                rcp_dict = cbmio.load(self.recipe_file_path(rcp_file))
                if rcp_dict and self.recipe_sections:
                    merge_dict_inplace(
                        self.recipe_sections,
                        {rcp_key: rcp_dict}
                    )
                elif rcp_dict:
                    self.recipe_sections[rcp_key] = rcp_dict

    def valid(self) -> bool:
        return all(
            (
                cfg_key in self.recipe_sections
                for cfg_key in RecipeKeys.RECIPE_SECTIONS
            )
        )

    def get_template_for(self, reg_key: str) -> dict[str, t.Any]:
        return self.recipe_templates[reg_key]

    def get_templates(self) -> dict[str, t.Any]:
        return self.recipe_templates


class ModelRecipe(pydantic.BaseModel):
    recipe_setup: RecipeSetup
    region_mapper: type[structure.RegionMapper]
    neuron_mapper: type[structure.NeuronMapper]
    connection_mapper: type[structure.ConnectionMapper]
    network_builder: type[structure.ModelBuilder]
    mod_structure: structure.Network | None = None
    save_flag: bool = True
    write_duck: bool = True
    out_format: t.Literal["json", "yaml", "yml"] = "json"
    network_struct: structure.Network = structure.Network(name="empty")

    def output_location(self, recipe_key: str) -> Path:
        file_name = self.recipe_setup.recipe_output_prefix(recipe_key)
        out_path = Path(
            self.recipe_setup.output_dir, file_name
        )
        if not os.path.exists(out_path.parent):
            os.makedirs(out_path.parent)
        return out_path.with_suffix("." + self.out_format)

    def save_db_out(
        self,
        db_connect_output: dict[str, t.Any] | None ,
        db_out_loc: str | Path,
        write_duck: bool,
    ) -> None:
        if db_connect_output is None:
            return
        if self.save_flag:
            cbmio.dump(
                db_connect_output,
                db_out_loc,
                indent=4,
            )
        if write_duck:
            duck_out_loc = str(db_out_loc).replace(self.out_format, 'db')
            workflow.write_to_duck_db(
                db_connect_output,
                duck_out_loc,
            )

    def download_db_data(self) -> dict[str, t.Any]:
        db_src_config = self.recipe_setup.get_section(RecipeKeys.SRC_DATA)
        _log().info("Start Query and Download Data")
        db_connect_output = workflow.run_db_connect_workflows(db_src_config)
        #
        db_out_loc = self.output_location(RecipeKeys.DB_CONNECT)
        self.save_db_out(db_connect_output, db_out_loc, self.write_duck)
        _log().info("Completed Query and Download Data")
        return db_connect_output

    def run_db_post_ops(self):
        db_connect_data = cbmio.load(
            self.output_location(RecipeKeys.DB_CONNECT)
        )
        db_src_config = self.recipe_setup.get_section(RecipeKeys.SRC_DATA)
        db_post_op_data = None
        _log().info("Start DB Post ops")
        if db_connect_data:
            db_post_op_data = workflow.run_ops_workflows(
                db_connect_data,
                db_src_config,
                RecipeKeys.POST_OPS
            )
            #
            db_out_loc = self.output_location(RecipeKeys.SRC_DATA)
            self.save_db_out(db_post_op_data, db_out_loc, self.write_duck)
        _log().info("Completed Post ops")
        return db_post_op_data

    def acquire_source_data(self):
        db_connection_output = self.download_db_data()
        db_post_op_data = self.run_db_post_ops()
        return db_connection_output, db_post_op_data

    def map_source_data(self):
        db2model_map = self.recipe_setup.get_section(RecipeKeys.DB2MODEL_MAP)
        db_lox_map = db2model_map[RecipeKeys.LOCATIONS]
        db_conn_map = db2model_map[RecipeKeys.CONNECTIONS]
        db_source_data = cbmio.load(self.output_location(RecipeKeys.SRC_DATA))
        srcdata_map_output = None
        if db_source_data:
            db2location_output = workflow.map_srcdata_locations(
                db_source_data, db_lox_map
            )
            db2connect_output = workflow.map_srcdata_connections(
                db_source_data, db_conn_map
            )
            srcdata_map_output = {
                "locations": db2location_output,
                "connections": db2connect_output,
            }
        if self.save_flag and srcdata_map_output:
            cbmio.dump(
                srcdata_map_output,
                self.output_location(RecipeKeys.DB2MODEL_MAP),
                indent=4,
            )
        return srcdata_map_output

    def build_net_struct(self):
        network_desc_output = cbmio.load(
            self.output_location(RecipeKeys.DB2MODEL_MAP)
        )
        if not network_desc_output:
            network_desc_output = self.map_source_data()
        if network_desc_output:
            self.network_struct = structure.srcdata2network(
                network_desc_output,
                self.recipe_setup.name,
                self.region_mapper,
                self.neuron_mapper,
                self.connection_mapper,
            )
            return self.network_struct

    def source_data2model_struct(self):
        self.map_source_data()
        return self.build_net_struct()

    def apply_mod(self, ncells: int=30000):
        if self.mod_structure:
            # Update user preference
            self.network_struct = self.network_struct.apply_mod(self.mod_structure)
        # Estimate NCells from the fractions
        self.network_struct.populate_ncells(ncells)
        if self.save_flag and self.network_struct:
            cbmio.dump(
                self.network_struct.model_dump(),
                self.output_location(RecipeKeys.NETWORK_STRUCT),
                indent=4,
            )
        return self.network_struct

    def build_network(self, save_flag: bool=True, **kwargs: t.Any):
        # Construct model
        net_builder = self.network_builder(self.network_struct, **kwargs)
        net_builder.build()
        if save_flag:
            net_builder.save(self.recipe_setup.network_dir)
        return net_builder


class ModelUpdateRecipe(pydantic.BaseModel):
    recipe_setup: RecipeSetup
    prior_net: structure.PriorNetwork
    connection_mapper: type[structure.ConnectionMapper]
    network_updater: type[structure.ModelEditor]
    mod_structure: structure.Network

    def apply_mod(self, ncells: int=30000):
        # TODO:: work in the future
        return None

    def update_network(self, save_flag: bool=True, **kwargs: t.Any):
        # TODO::
        updater = self.network_updater(self.prior_net, self.mod_structure)
        updater.edit()
        if save_flag:
            updater.save(self.recipe_setup.network_dir)
        return updater


def init_recipe_setup(
    name: str,
    base_dir: str | Path,
    recipe_files: dict[str, list[str | Path]],
    recipe_dir: str | Path,
) -> RecipeSetup:
    return RecipeSetup(
        name=name,
        base_dir=base_dir,
        recipe_files=recipe_files,
        recipe_dir=recipe_dir,
    )


def netstruct_from_file(struct_file: Path) -> structure.Network | None:
    network_struct = cbmio.load(struct_file)
    if network_struct:
        return structure.dict2netstruct(network_struct)
    return None
