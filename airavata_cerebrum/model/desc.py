import pathlib
import typing
import os

from ..util.io import load, dump

# Lookup Keys in Configuration dictionary
DB_CONFIG_KEY = "config"
DB_DATA_SRC_KEY = "source_data"
DB_CONNECT_KEY = "db_connect"
DB_POSTOP_KEY = "post_ops"
#
DB2MODEL_MAP_KEY = "data2model_map"
TEMPLATES_KEY = "templates"
LABEL_KEY = "label"
NAME_KEY = "name"
WORKFLOW_KEY = "workflow"
LOCATIONS_KEY = "locations"
CONNECTIONS_KEY = "connections"
TYPE_KEY = "type"
#
DESC_CFG_KEYS = [
    DB2MODEL_MAP_KEY,
    DB_DATA_SRC_KEY
]

#
# File paths
DESCRIPTION_DIR = "description"


#
#
class ModelDescConfig:
    def __init__(
        self,
        name: str,
        base_dir: str | pathlib.Path,
        config_files: typing.Dict[str, str],
        config_dir: str | pathlib.Path = pathlib.Path("."),
        create_dir: bool = False
    ):
        self.name = name
        self.base_dir = base_dir
        self.config_dir = config_dir
        self.config: typing.Dict[str, typing.Any] = {}
        if DB_CONFIG_KEY in config_files:
            self.load_config(config_files[DB_CONFIG_KEY])
        else:
            self.load_config_from(config_files, DESC_CFG_KEYS)
        self.model_dir = pathlib.PurePath(self.base_dir,
                                          self.name)
        if create_dir and not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)

    def location(self, file_name):
        if self.config_dir:
            return pathlib.PurePath(self.config_dir, file_name)
        return file_name

    def load_config(self, config_file):
        cdict = load(self.location(config_file))
        if cdict:
            self.config: typing.Dict[str, typing.Any] = cdict

    def load_config_from(self, config_files, db_cfg_keys):
        for cfg_key in db_cfg_keys:
            json_obj = None
            if cfg_key in config_files:
                json_obj = load(self.location(config_files[cfg_key]))
            if json_obj:
                self.config[cfg_key] = json_obj[cfg_key]

    def out_prefix(self, cfg_key: str) -> str:
        return cfg_key + "_output"

    def get_config(self, cfg_key: str) -> typing.Dict[str, typing.Any]:
        return self.config[cfg_key]


class ModelConfigTemplate(ModelDescConfig):

    def __init__(
        self,
        name: str,
        base_dir: str | pathlib.Path,
        config_files: typing.Dict[str, str],
        config_dir: str | pathlib.Path = pathlib.Path("."),
        create_dir: bool = False,
    ):
        super().__init__(name, base_dir, config_files, config_dir, create_dir)
        if TEMPLATES_KEY in config_files:
            cdict = load(self.location(config_files[TEMPLATES_KEY]))
            if cdict:
                self.config[TEMPLATES_KEY] = cdict[TEMPLATES_KEY]

    def get_template_for(self, cfg_key: str) -> typing.Dict[str, typing.Any]:
        template_config = self.config[TEMPLATES_KEY]
        return template_config[cfg_key]

    def get_template(self) -> typing.Dict[str, typing.Any]:
        return self.config[TEMPLATES_KEY]
