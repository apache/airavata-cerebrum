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
T = typing.TypeVar('T')


class ClassRegister(typing.Generic[T]):
    register_map: typing.Dict[str, typing.Type[T]]

    def __init__(self, register_map: typing.Dict[str, typing.Type]) -> None:
        self.register_map = register_map

    def object(
        self, query_key: str, **init_params: typing.Dict[str, typing.Any]
    ) -> T | None:
        if query_key not in self.register_map:
            return None
        return self.register_map[query_key](**init_params)

    def get_type(self, query_key: str) -> typing.Type[T] | None:
        if query_key not in self.register_map:
            return None
        return self.register_map[query_key]


QUERY_REGISTER : ClassRegister[base.DbQuery] = ClassRegister(
    {
        class_qual_name(clsx): clsx
        for clsx in itertools.chain(
            abc_mouse_db.query_register(),
            abm_celltypes_db.query_register(),
            ai_synphys_db.query_register(),
            xform.query_register(),
            json_filter.query_register(),
            dict_filter.query_register(),
            abc_mouse_ops.query_register(),
            abm_celltypes_ops.query_register(),
            ai_synphys_ops.query_register(),
        )
    }
)
XFORM_REGISTER : ClassRegister[base.OpXFormer] = ClassRegister(
    {
        class_qual_name(clsx): clsx
        for clsx in itertools.chain(
            abc_mouse_db.xform_register(),
            abm_celltypes_db.xform_register(),
            ai_synphys_db.xform_register(),
            xform.xform_register(),
            json_filter.xform_register(),
            dict_filter.xform_register(),
            abc_mouse_ops.xform_register(),
            abm_celltypes_ops.xform_register(),
            ai_synphys_ops.xform_register(),
        )
    }
)

def find_type_in_register(register_key):
    reg_type = QUERY_REGISTER.get_type(register_key)
    if reg_type:
        return reg_type
    return XFORM_REGISTER.get_type(register_key)
