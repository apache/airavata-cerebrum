import json
import pickle
import yaml
import typing as t
from pathlib import Path
# ----- json files load/save ----------
#

# Type to indicate the dict data loaded from the serialized files
SerialDict : t.TypeAlias = dict[str, t.Any]


def load_json(file_name: str | Path) -> SerialDict:
    with open(file_name) as in_fptr:
        return json.load(in_fptr)


def dump_json(
    json_obj: SerialDict,
    file_name: str | Path,
    indent: int
):
    with open(file_name, "w") as out_fptr:
        json.dump(json_obj, out_fptr, indent=indent)


# ----- yaml files load/save ----------
#
def load_yaml(file_name: str | Path) -> SerialDict:
    with open(file_name) as in_fptr:
        return yaml.safe_load(in_fptr)


def dump_yaml(
    json_obj: SerialDict,
    file_name: str | Path,
    indent: int
):
    with open(file_name, "w") as out_fptr:
        yaml.dump(json_obj, out_fptr, indent=indent)


#
def load(file_name: str | Path) -> SerialDict | None:
    fp_suffix = Path(file_name).suffix
    match fp_suffix:
        case ".yaml" | ".yml":
            return load_yaml(file_name)
        case ".json":
            return load_json(file_name)
        case _:
            return {}


def dump(
    json_obj: SerialDict,
    file_name: str | Path,
    indent: int
):
    fpath = Path(file_name)
    match fpath.suffix:
        case ".yaml" | ".yml":
            return dump_yaml(json_obj, file_name, indent=indent)
        case ".json":
            return dump_json(json_obj, file_name, indent=indent)
        case _:
            return None


# Pickle
def dump_pickle(fname: str, pyobject: object):
    with open(fname, 'wb') as handle:
        pickle.dump(
            pyobject,
            handle,
            protocol=pickle.HIGHEST_PROTOCOL
        )
