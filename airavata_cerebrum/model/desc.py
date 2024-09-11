import pathlib
import typing


from ..util.io import load, dump


#
#
class ModelDescConfig:
    DB_CONFIG_KEY = "config"
    DB_CONNECT_KEY = "db_connect"
    DB_XFORM_KEY = "db_xform"
    DB_LOCATION_MAP_KEY = "db_location_map"
    DB_CFG_KEYS = [DB_CONNECT_KEY, DB_XFORM_KEY, DB_LOCATION_MAP_KEY]

    def __init__(self, config_files: typing.Dict[str, str],
                 config_dir: str | pathlib.Path | None = None,
                 ):
        self.config_dir = config_dir
        self.md_config: typing.Dict[str, typing.Any] = {}
        if ModelDescConfig.DB_CONFIG_KEY in config_files:
            self.load_config(config_files[ModelDescConfig.DB_CONFIG_KEY])
        else:
            self.load_config_from(config_files,
                                  ModelDescConfig.DB_CFG_KEYS)

    def location(self, file_name):
        if self.config_dir:
            return pathlib.PurePath(self.config_dir, file_name)
        return file_name

    def load_config(self, config_file):
        cdict = load(self.location(config_file))
        if cdict:
            self.md_config: typing.Dict[str, typing.Any] = cdict 

    def load_config_from(self, config_files, db_cfg_keys):
        for cfg_key in db_cfg_keys:
            json_obj = load(self.location(config_files[cfg_key]))
            if json_obj:
                self.md_config[cfg_key] = json_obj[cfg_key]

    def out_json(self, cfg_key: str) -> str:
        return cfg_key + "_output.json"

    def get_config(self, cfg_key: str) -> typing.Dict[str, typing.Any]:
        return self.md_config[cfg_key]


class ModelConfigTemplate(ModelDescConfig):
    DB_TEMPLATE_KEY = "template"
    DB_CFG_KEYS = [DB_TEMPLATE_KEY]

    def __init__(self, config_files: typing.Dict[str, str],
                 config_dir: str | pathlib.Path | None = None):
        super().__init__(config_files, config_dir)
        if ModelConfigTemplate.DB_TEMPLATE_KEY in config_files:
            self.load_config(config_files[ModelConfigTemplate.DB_TEMPLATE_KEY])

    def get_template_for(self, cfg_key: str) -> typing.Dict[str, typing.Any]:
        template_config = self.md_config[ModelConfigTemplate.DB_TEMPLATE_KEY]
        return template_config[cfg_key]

    def get_template(self) -> typing.Dict[str, typing.Any]:
        return self.md_config[ModelConfigTemplate.DB_TEMPLATE_KEY]
