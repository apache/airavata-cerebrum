import pathlib
import typing
import os

from . import io as cbmio


#
# Lookup Keys in Configuration dictionary
class CfgKeys:
    CONFIG = "config"
    SRC_DATA = "source_data"
    DB_CONNECT = "db_connect"
    POST_OPS = "post_ops"
    DB2MODEL_MAP = "data2model_map"
    LABEL = "label"
    NAME = "name"
    WORKFLOW = "workflow"
    LOCATIONS = "locations"
    CONNECTIONS = "connections"
    TYPE = "type"
    #
    DESCRIPTION_CFG = [
        DB2MODEL_MAP,
        SRC_DATA
    ]
    #
    TEMPLATES = "templates"


#
# Configuration for Model Description
class ModelDescConfig:
    def __init__(
        self,
        name: str,
        base_dir: str | pathlib.Path,
        config_files: typing.Dict[str, str | pathlib.Path],
        config_dir: str | pathlib.Path = pathlib.Path("."),
        create_dir: bool = False
    ):
        self.name = name
        self.base_dir = base_dir
        self.config_dir = config_dir
        self.config: typing.Dict[str, typing.Any] = {}
        if CfgKeys.CONFIG in config_files:
            self.load_config(config_files[CfgKeys.CONFIG])
        else:
            self.load_config_from(config_files, CfgKeys.DESCRIPTION_CFG)
        self.model_dir = pathlib.Path(self.base_dir,
                                      self.name)
        if create_dir and not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)

    def location(
        self,
        file_name: str | pathlib.Path
    ) -> str | pathlib.Path:
        if self.config_dir:
            return pathlib.Path(self.config_dir, file_name)
        return file_name

    def load_config(
        self,
        config_file: str | pathlib.Path
    ) -> None:
        cdict = cbmio.load(self.location(config_file))
        if cdict:
            self.config |= cdict

    def load_config_from(
        self,
        config_files: typing.Dict[str, str | pathlib.Path],
        db_cfg_keys: typing.List[str]
    ) -> None:
        for cfg_key in db_cfg_keys:
            json_obj = None
            if cfg_key in config_files:
                json_obj = cbmio.load(self.location(config_files[cfg_key]))
            if json_obj:
                self.config[cfg_key] = json_obj[cfg_key]

    def out_prefix(self, cfg_key: str) -> str:
        return cfg_key + "_output"

    def get_config(self, cfg_key: str) -> typing.Dict[str, typing.Any]:
        return self.config[cfg_key]


#
# Template Configuration
class ModelDescConfigTemplate(ModelDescConfig):

    def __init__(
        self,
        name: str,
        base_dir: str | pathlib.Path,
        config_files: typing.Dict[str, str | pathlib.Path],
        config_dir: str | pathlib.Path = pathlib.Path("."),
        create_dir: bool = False,
    ):
        super().__init__(name, base_dir, config_files, config_dir, create_dir)
        if CfgKeys.TEMPLATES in config_files:
            cdict = cbmio.load(self.location(config_files[CfgKeys.TEMPLATES]))
            if cdict:
                self.config[CfgKeys.TEMPLATES] = cdict[CfgKeys.TEMPLATES]

    def get_template_for(
        self,
        cfg_key: str
    ) -> typing.Dict[str, typing.Any]:
        template_config = self.config[CfgKeys.TEMPLATES]
        return template_config[cfg_key]

    def get_template(
        self
    ) -> typing.Dict[str, typing.Any]:
        return self.config[CfgKeys.TEMPLATES]
