import json
import yaml
import pathlib
import typing
# ----- json files load/save ----------
#
def load_json(file_name: str | pathlib.PurePath) -> typing.Dict:
    with open(file_name) as in_fptr:
        return json.load(in_fptr)


def dump_json(json_obj: typing.Dict, file_name: str | pathlib.PurePath, indent: int):
    with open(file_name, "w") as out_fptr:
        json.dump(json_obj, out_fptr, indent=indent)

# ----- yaml files load/save ----------
#
def load_yaml(file_name: str | pathlib.PurePath) -> typing.Dict:
    with open(file_name) as in_fptr:
        return yaml.safe_load(in_fptr)


def dump_yaml(json_obj: typing.Dict, file_name: str | pathlib.PurePath, indent: int):
    with open(file_name, "w") as out_fptr:
        yaml.dump(json_obj, out_fptr, indent=indent)


# 
def load(file_name: str | pathlib.PurePath) -> typing.Dict | None:
    fpath = pathlib.PurePath(file_name)
    match fpath.suffix:
        case "yaml":
            return load_yaml(file_name)
        case "json":
            return load_json(file_name)
        case _:
            return None


def dump(json_obj: typing.Dict, file_name: str | pathlib.PurePath, indent: int):
    fpath = pathlib.PurePath(file_name)
    match fpath.suffix:
        case "yaml":
            return dump_yaml(json_obj, file_name, indent=indent)
        case "json":
            return dump_json(json_obj, file_name, indent=indent)
        case _:
            return None
