import logging
from pathlib import Path

import pydantic

from airavata_cerebrum.model.structure import Network
from airavata_cerebrum.recipe import ModelRecipe, RecipeSetup

from .model import (V1BMTKNetworkBuilder, V1ConnectionMapper, V1NeuronMapper,
                    V1RegionMapper)


class RecipeParams(pydantic.BaseModel):
    name: str = "v1l4"
    ncells: int = 4000
    enable_timing: bool = True
    logging_level: int = logging.DEBUG
    root_logging_level: int = logging.DEBUG
    base_dir: Path = Path("./builds/v1l4")
    recipe_dir: Path = Path("./recipes/v1l4")
    recipe_output_dir: Path | None = Path("./data/v14")
    full_recipe: str | Path = "recipe.json"
    custom_mod_main: Path = Path("./recipes/v1l4/custom_mod.json")
    ctdb_models_dir: Path = Path("./components/point_neuron_models/")
    nest_models_dir: Path = Path("./components/cell_models/")
    save_flag: bool = True

    @property
    def output_dir(self) -> Path:
        return Path(
            self.recipe_output_dir if self.recipe_output_dir else self.recipe_dir
        )

    @property
    def recipe_files(self) -> dict[str, list[str | Path]]:
        """The recipe_files property."""
        return {
            "recipe": [self.full_recipe],
            "templates": ["recipe_template.json"]
        }

    @property
    def custom_mod(self) -> list[str | Path]:
        return [self.custom_mod_main]

    def recipe_setup(self):
        return RecipeSetup(
            name=self.name,
            base_dir=self.base_dir,
            recipe_files=self.recipe_files,
            recipe_dir=self.recipe_dir,
            recipe_output_dir=self.output_dir,
            create_model_dir=True,
        )

    def model_recipe(self) -> ModelRecipe:
        md_recipe_setup = self.recipe_setup()
        custom_mod_struct = Network.from_file_list(self.custom_mod)
        return ModelRecipe(
            recipe_setup=md_recipe_setup,
            region_mapper=V1RegionMapper,
            neuron_mapper=V1NeuronMapper,
            connection_mapper=V1ConnectionMapper,
            network_builder=V1BMTKNetworkBuilder,
            mod_structure=custom_mod_struct,
            save_flag=self.save_flag,
        )
