import typing as t
import functools
#


def class_qual_name(src_class: type):
    return ".".join([src_class.__module__, src_class.__name__])


def exclude_keys(
    r_dct: dict[str, t.Any],
    key_set: set[str]
) -> dict[str, t.Any]:
    return {kx: vx for kx, vx in r_dct.items() if kx not in key_set}


def prefix_keys(
    r_dct: dict[str, t.Any],
    pfx: str,
    sep: str = '_'
) -> dict[str, t.Any]:
    return {f"{pfx}{sep}{kx}": vx for kx, vx in r_dct.items()}


def merge_dict_inplace(
    dest_dct: dict[str, t.Any],
    from_dct: dict[str, t.Any],
) -> None:
    for k, _v in from_dct.items():
        if (
            (k in dest_dct) and
            isinstance(from_dct[k], dict) and
            isinstance(dest_dct[k], dict)
        ):
            merge_dict_inplace(dest_dct[k], from_dct[k])
        else:
            dest_dct[k] = from_dct[k]


def flip_args(bin_func: t.Callable[[t.Any, t.Any], t.Any]):
    def flip_fn(arg_a: t.Any, arg_b: t.Any) -> t.Any:
        return bin_func(arg_b, arg_a)
    return flip_fn


def flip_function(func: t.Callable[[t.Any, ], t.Any]):
    @functools.wraps
    def flip_fn(*args: t.Any):
        return func(*args[::-1])
    return flip_fn
