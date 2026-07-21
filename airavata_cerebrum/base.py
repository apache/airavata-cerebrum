import typing as t
#
from abc import ABC, ABCMeta, abstractmethod
from collections.abc import Iterable, Sequence
from typing_extensions import Self, override
from pydantic import BaseModel, Field


#
# pydantic-based BaseModel for Cerebrum
class CerebrumBaseModel(BaseModel):
    name : t.Annotated[str, Field(title="Name")] = ""

    def exclude(self) -> set[str]:
        return set(["name"])

    def is_valid_field(self, field: str) -> bool:
        return field in type(self).model_fields

    def get(self, field: str, val_not_found: t.Any = None) -> t.Any:
        try:
            return getattr(self, field)
        except AttributeError:
            return val_not_found


# Initilization and Execution Parameters
InitParamsT = t.TypeVar(
    'InitParamsT',
    bound='CerebrumBaseModel',
    covariant=True,
)

ExecParamsT = t.TypeVar(
    'ExecParamsT',
    bound='CerebrumBaseModel',
    covariant=True,
)


# pydantic-based BaseModel for Query and Transform paramters
class BaseParams(CerebrumBaseModel, t.Generic[InitParamsT, ExecParamsT]):
    init_params: t.Annotated[InitParamsT, Field(title="Init. Params")]
    exec_params: t.Annotated[ExecParamsT, Field(title="Exec. Params")]

    @override
    def is_valid_field(self, field: str) -> bool:
        return (
            (field in type(self.init_params).model_fields) or
            (field in type(self.exec_params).model_fields) or
            (field in type(self).model_fields)
        )

    @override
    def get(self, field: str, val_not_found: t.Any = None) -> t.Any:
        ivalue = self.init_params.get(field)
        if ivalue is not None:
            return ivalue
        evalue = self.exec_params.get(field)
        if evalue is not None:
            return evalue
        return super().get(field, val_not_found)


# Base Parameters with CerebrumBaseModel as init and exec parameters
BaseParamsCBT : t.TypeAlias = BaseParams[CerebrumBaseModel, CerebrumBaseModel]


# pydantic-based model for no paramters
class NoneParams(CerebrumBaseModel):
    pass


# Abstract Base class for parameter interface
class ParamsInterface(ABC, t.Generic[InitParamsT, ExecParamsT]):
    @classmethod
    @abstractmethod
    def params_type(
        cls
    ) -> type[BaseParamsCBT]:
        return BaseParamsCBT

    @classmethod
    @abstractmethod
    def params_instance(
        cls,
        param_dict: dict[str, t.Any],
    ) -> BaseParamsCBT:
        return BaseParamsCBT.model_validate(param_dict)


XformElt : t.TypeAlias = dict[str, t.Any]
XformItr : t.TypeAlias = Iterable[XformElt]
XformSeq : t.TypeAlias = Sequence[XformElt]
QryElt   : t.TypeAlias = dict[str, t.Any]
QryItr   : t.TypeAlias = Iterable[QryElt]


# Abstract interface for Database Queries
class DbQuery(ParamsInterface[InitParamsT, ExecParamsT], ABC):
    @abstractmethod
    def __init__(
        self,
        init_params: InitParamsT,
        **params: t.Any
    ):
        pass

    @abstractmethod
    def run(
        self,
        exec_params: ExecParamsT,
        first_iter: QryItr | None,
        *rest_iter: QryItr | None,
        **params: t.Any,
    ) -> QryItr | None:
        return None


# Abstract interface for XFormer operations
class OpXFormer(ParamsInterface[InitParamsT, ExecParamsT], ABC):
    @abstractmethod
    def __init__(
        self,
        init_params: InitParamsT,
        **params: t.Any
    ):
        pass

    @abstractmethod
    def xform(
        self,
        exec_params: ExecParamsT,
        first_iter: XformItr | None,
        *rest_iter: QryItr | None,
        **params: t.Any,
    ) -> XformItr | None:
        return None


# Query Types with CerebrumBaseModel as init and exec parameters
DbQueryCBT   : t.TypeAlias = DbQuery[CerebrumBaseModel, CerebrumBaseModel]
OpXFormerCBT : t.TypeAlias = OpXFormer[CerebrumBaseModel, CerebrumBaseModel]


# Abstract interface for DBWrite operations
class QryDBWriter(ABC):
    @abstractmethod
    def write(
        self,
        in_iter: QryItr | None,
        **_params: t.Any,
    ) -> None:
        pass


BaseStructType = t.TypeVar('BaseStructType')


# Abstract Base class for network structure components
class BaseStruct(CerebrumBaseModel, metaclass=ABCMeta):
    @abstractmethod
    @override
    def exclude(self) -> set[str]:
        return set([])

    @abstractmethod
    def apply_mod(self, mod_struct: t.Any) -> Self:
        return self
