import abc
import typing
import traitlets


#
# Abstract Base classes
#
class EmptyTraits(traitlets.HasTraits):
    pass


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
        return EmptyTraits


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
        return EmptyTraits
