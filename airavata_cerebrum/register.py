import typing
import itertools
from . import base
from .dataset import abc_mouse as abc_mouse_db
from .dataset import abm_celltypes as abm_celltypes_db
from .dataset import ai_synphys as ai_synphys_db
from .operations import abc_mouse as abc_mouse_ops
from .operations import abm_celltypes as abm_celltypes_ops
from .operations import ai_synphys as ai_synphys_ops
from .operations import json_filter
from .operations import dict_filter
from .operations import xform
from .util import class_qual_name


#
# -------- Register Query and Xform classes
#
RCType = typing.TypeVar("RCType")


class TypeRegister(typing.Generic[RCType]):
    register_map: typing.Dict[str, typing.Type[RCType]]

    def __init__(
        self, register_lst: typing.Iterable[type[RCType]], base_class: type[RCType]
    ) -> None:
        self.register_map = {
            class_qual_name(clsx): clsx
            for clsx in register_lst
            if issubclass(clsx, base_class)
        }

    def get_object(
        self, query_key: str, **init_params: typing.Any
    ) -> RCType | None:
        if query_key not in self.register_map:
            return None
        return self.register_map[query_key](**init_params)

    def get_type(self, query_key: str) -> typing.Type[RCType] | None:
        if query_key not in self.register_map:
            return None
        return self.register_map[query_key]


QUERY_REGISTER: TypeRegister[base.DbQuery] = TypeRegister(
    itertools.chain(
        abc_mouse_db.query_register(),
        abm_celltypes_db.query_register(),
        ai_synphys_db.query_register(),
        xform.query_register(),
        json_filter.query_register(),
        dict_filter.query_register(),
        abc_mouse_ops.query_register(),
        abm_celltypes_ops.query_register(),
        ai_synphys_ops.query_register(),
    ),
    base.DbQuery,
)

XFORM_REGISTER: TypeRegister[base.OpXFormer] = TypeRegister(
    itertools.chain(
        abc_mouse_db.xform_register(),
        abm_celltypes_db.xform_register(),
        ai_synphys_db.xform_register(),
        xform.xform_register(),
        json_filter.xform_register(),
        dict_filter.xform_register(),
        abc_mouse_ops.xform_register(),
        abm_celltypes_ops.xform_register(),
        ai_synphys_ops.xform_register(),
    ),
    base.OpXFormer,
)


def find_type(
    register_key: str,
) -> type[base.OpXFormer] | type[base.DbQuery] | None:
    reg_type = QUERY_REGISTER.get_type(register_key)
    if reg_type:
        return reg_type
    return XFORM_REGISTER.get_type(register_key)


def get_query_object(
    register_key: str,
    **params: typing.Any,
) -> base.DbQuery | None:
    return QUERY_REGISTER.get_object(
        register_key, **params
    )


def get_xform_op_object(
    register_key: str,
    **params: typing.Any,
) -> base.OpXFormer | None:
    return XFORM_REGISTER.get_object(
        register_key, **params
    )
 
