import abc
import typing


#
# Abstract Base classes
#
TraitType = typing.TypeVar('TraitType')


class DbQuery(abc.ABC):
    @abc.abstractmethod
    def run(
        self,
        in_iter: typing.Iterable | None,
        **params: typing.Any,
    ) -> typing.Iterable | None:
        return None

    @classmethod
    @abc.abstractmethod
    def trait_type(cls) -> typing.Type:
        return TraitType


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
    def trait_type(cls) -> typing.Type:
        return TraitType
