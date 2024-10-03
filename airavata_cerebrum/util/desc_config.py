import pathlib
import typing
import os
import logging
import pydantic
import collections

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
    NETWORK_STRUCT = "network_structure"
    NETWORK = "network"
    #
    DESCRIPTION_CFG = [DB2MODEL_MAP, SRC_DATA]


class ModelDescConfigBase(pydantic.BaseModel):
    config_files: typing.Dict[str, typing.List[str | pathlib.Path]]
    config_dir: str | pathlib.Path = pathlib.Path(".")
    config: typing.Dict[str, typing.Any] = {}

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
    name: str
    base_dir: str | pathlib.Path
    create_model_dir: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if CfgKeys.CONFIG in self.config_files:
            self.load_config()
        else:
            try:
                self.load_config_list()
            except KeyError:
                _log().error(
                    "Failed to find one of two keys: [%s]", str(CfgKeys.DESCRIPTION_CFG)
                )
        # Create Config
        if self.create_model_dir and not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)

    @property
    def model_dir(self) -> pathlib.Path:
        return pathlib.Path(self.base_dir, self.name)

    @property
    def network_dir(self) -> pathlib.Path:
        return pathlib.Path(self.base_dir, self.name, CfgKeys.NETWORK)

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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if CfgKeys.TEMPLATES in self.config_files:
            for cfg_file in self.config_files[CfgKeys.TEMPLATES]:
                cfg_dict = cbmio.load(self.location(cfg_file))
                if cfg_dict:
                    self.update_config(cfg_dict, CfgKeys.TEMPLATES)

    def get_template_for(self, reg_key: str) -> typing.Dict[str, typing.Any]:
        return self.config[CfgKeys.TEMPLATES][reg_key]

    def get_templates(self) -> typing.Dict[str, typing.Any]:
        return self.config[CfgKeys.TEMPLATES]


class ModelDescCfgTuple(typing.NamedTuple):
    config: ModelDescConfig
    templates: ModelDescConfigTemplate


def init_model_desc_config(
    name,
    base_dir,
    config_files,
    config_dir,
) -> ModelDescCfgTuple:
    return ModelDescCfgTuple(
        config=ModelDescConfig(
            name=name,
            base_dir=base_dir,
            config_files=config_files,
            config_dir=config_dir,
        ),
        templates=ModelDescConfigTemplate(
            config_files=config_files,
            config_dir=config_dir,
        ),
    )
