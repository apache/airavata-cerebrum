import itertools
import typing as t
from collections.abc import Iterable

from .base import (
    CerebrumBaseModel,
    OpXFormer, DbQuery, QryDBWriter,
    BaseParamsCBT, DbQueryCBT, OpXFormerCBT
)
from .dataset import query_register as db_query_register
from .dataset import xform_register as db_xform_register
from .dataset import dbwriter_register
from .operations import query_register as ops_query_register
from .operations import xform_register as ops_xform_register
from .util import class_qual_name


#
# -------- Register Query and Xform classes
#
RCType = t.TypeVar("RCType")


class TypeRegister(t.Generic[RCType]):
    register_map: dict[str, type[RCType]]
    base_class: type[RCType]

    def __init__(
        self,
        register_lst: Iterable[type[RCType]],
        base_class: type[RCType],
        key_source: t.Literal['class', 'module'] = 'class'
    ) -> None:
        self.base_class = base_class
        self.register_map = {
            self.qual_name(clsx, key_source): clsx
            for clsx in register_lst
            if issubclass(clsx, base_class)
        }

    def qual_name(
        self,
        clsx: type,
        key_source: t.Literal['class', 'module'],
    ) -> str:
        match key_source:
            case 'class':
                return class_qual_name(clsx)
            case 'module':
                return clsx.__module__

    def register(
        self,
        clsx : type[RCType],
        key_source: t.Literal['class', 'module'] = 'class'
    ) -> bool:
        if issubclass(clsx, self.base_class):
            self.register_map[self.qual_name(clsx, key_source)] = clsx
            return True
        return False

    def get_type(self, query_key: str) -> type[RCType] | None:
        if query_key not in self.register_map:
            return None
        return self.register_map[query_key]


QUERY_REGISTER: TypeRegister[DbQueryCBT] = TypeRegister(
    itertools.chain(
        db_query_register(),
        ops_query_register(),
    ),
    DbQuery,
)

XFORM_REGISTER: TypeRegister[OpXFormerCBT] = TypeRegister(
    itertools.chain(
        db_xform_register(),
        ops_xform_register(),
    ),
    OpXFormer,
)

QRY_DBWIRTER_REGISTER: TypeRegister[QryDBWriter] = TypeRegister(
    dbwriter_register(),
    QryDBWriter,
    key_source='module'
)


def find_query_type(
    register_key: str,
):
    return QUERY_REGISTER.get_type(register_key)


def find_xformer_type(
    register_key: str,
):
    return XFORM_REGISTER.get_type(register_key)


def find_type(
    register_key: str,
) -> type[OpXFormerCBT] | type[DbQueryCBT] | None:
    reg_type = find_query_type(register_key)
    if reg_type:
        return reg_type
    return find_xformer_type(register_key)


def get_query_params(
    register_key: str,
    params: dict[str, t.Any]
) -> BaseParamsCBT | None:
    reg_type = find_query_type(register_key)
    if reg_type:
        return reg_type.params_instance(params)
    return None


def get_xformer_params(
    register_key: str,
    params: dict[str, t.Any]
) -> BaseParamsCBT | None:
    reg_type = find_xformer_type(register_key)
    if reg_type:
        return reg_type.params_instance(params)
    return None


def get_query_instance(
    register_key: str,
    init_params: CerebrumBaseModel,
    **params: t.Any,
) -> DbQueryCBT | None:
    qry_type : type[DbQueryCBT] | None = find_query_type(register_key)
    return (
        qry_type(init_params, **params)
        if qry_type else None
    )


def get_xformer_instance(
    register_key: str,
    init_params: CerebrumBaseModel,
    **params: t.Any,
) -> OpXFormerCBT | None:
    xformer_type : type[OpXFormerCBT] | None = find_xformer_type(register_key)
    return (
        xformer_type(init_params, **params)
        if xformer_type else None
    )


def get_db_writer_instance(
    register_key: str,
    **params: t.Any,
) -> QryDBWriter | None:
    qdb_writer = QRY_DBWIRTER_REGISTER.get_type(register_key)
    return qdb_writer(**params) if qdb_writer else None
