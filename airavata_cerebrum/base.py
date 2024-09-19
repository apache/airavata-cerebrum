import abc
import typing
import traitlets


#
# Abstract Base classes
#
TraitType = typing.TypeVar(
    'TraitType',
    bound=traitlets.HasTraits
)


# Abstract interface for Database Queries
class DbQuery(abc.ABC):
    @abc.abstractmethod
    def __init__(
        self,
        **params: typing.Any
    ):
        return None

    @abc.abstractmethod
    def run(
        self,
        in_iter: typing.Iterable | None,
        **params: typing.Any,
    ) -> typing.Iterable | None:
        return None

    @classmethod
    @abc.abstractmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return TraitType


# Abstract interface for XFormer operations
class OpXFormer(abc.ABC):
    @abc.abstractmethod
    def xform(
        self,
        in_iter: typing.Iterable | None,
        **params: typing.Any,
    ) -> typing.Iterable | None:
        return None

    @classmethod
    @abc.abstractmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return TraitType
