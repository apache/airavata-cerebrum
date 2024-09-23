import pathlib
import typing
import os
import logging

from . import io as cbmio


def _log():
    return logging.getLogger(__name__)


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
    INIT_PARAMS = "init_params"
    EXEC_PARAMS = "exec_params"
    TEMPLATES = "templates"
    NODE_KEY = "node_key"
    #
    DESCRIPTION_CFG = [DB2MODEL_MAP, SRC_DATA]


class ModelDescConfigBase:
    def __init__(
        self,
        config_files: typing.Dict[str, typing.List[str | pathlib.Path]],
        config_dir: str | pathlib.Path = pathlib.Path("."),
    ) -> None:
        self.config_files = config_files
        self.config_dir = config_dir
        self.config: typing.Dict[str, typing.Any] = {}

    def location(self, file_name: str | pathlib.Path) -> str | pathlib.Path:
        if self.config_dir:
            return pathlib.Path(self.config_dir, file_name)
        return file_name

    def out_prefix(self, cfg_key: str) -> str:
        return cfg_key + "_output"

    def get_config(self, cfg_key: str) -> typing.Dict[str, typing.Any]:
        return self.config[cfg_key]

    def update_config(
        self,
        cdict: typing.Dict[str, typing.Any],
        cfg_key: str | None = None,
    ) -> None:
        if cfg_key:
            if cfg_key in self.config:
                self.config[cfg_key] |= cdict
            else:
                self.config[cfg_key] = cdict
        else:
            self.config |= cdict


#
# Configuration for Model Description
class ModelDescConfig(ModelDescConfigBase):
    def __init__(
        self,
        name: str,
        base_dir: str | pathlib.Path,
        config_files: typing.Dict[str, typing.List[str | pathlib.Path]],
        config_dir: str | pathlib.Path = pathlib.Path("."),
        create_model_dir: bool = False,
    ):
        super().__init__(config_files, config_dir)
        self.name = name
        self.base_dir = base_dir
        self.model_dir = pathlib.Path(self.base_dir, self.name)
        if CfgKeys.CONFIG in config_files:
            self.load_config()
        else:
            try:
                self.load_config_list()
            except KeyError:
                _log().error(
                    "Failed to find one of two keys: [%s]", str(CfgKeys.DESCRIPTION_CFG)
                )
        # Create Config
        if create_model_dir and not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)

    def load_config(self) -> None:
        for cfg_file in self.config_files[CfgKeys.CONFIG]:
            cdict = cbmio.load(self.location(cfg_file))
            if cdict:
                self.update_config(cdict)

    def load_config_list(
        self,
    ) -> None:
        for cfg_key in CfgKeys.DESCRIPTION_CFG:
            for cfg_file in self.config_files[cfg_key]:
                cdict = cbmio.load(self.location(cfg_file))
                if cdict:
                    self.update_config(cdict, cfg_key)

    def valid(self) -> bool:
        return all(cfg_key in self.config for cfg_key in CfgKeys.DESCRIPTION_CFG)


#
# Template Configuration
class ModelDescConfigTemplate(ModelDescConfigBase):

    def __init__(
        self,
        config_files: typing.Dict[str, typing.List[str | pathlib.Path]],
        config_dir: str | pathlib.Path = pathlib.Path("."),
    ) -> None:
        super().__init__(config_files, config_dir)
        if CfgKeys.TEMPLATES in config_files:
            for cfg_file in config_files[CfgKeys.TEMPLATES]:
                cdict = cbmio.load(self.location(cfg_file))
                if cdict:
                    self.update_config(cdict, CfgKeys.TEMPLATES)

    def get_template_for(self, reg_key: str) -> typing.Dict[str, typing.Any]:
        return self.config[CfgKeys.TEMPLATES][reg_key]

    def get_templates(self) -> typing.Dict[str, typing.Any]:
        return self.config[CfgKeys.TEMPLATES]
