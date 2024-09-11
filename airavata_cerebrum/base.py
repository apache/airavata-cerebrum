import abc
import typing
#
# Abstract Base classes
#
class DbQuery(abc.ABC):
    @abc.abstractmethod
    def run(
        self,
        in_stream: typing.Union[typing.Iterable, None],
        **params: typing.Dict[str, typing.Any],
    ) -> typing.Iterable[typing.Dict[str, typing.Any]]:
        return None

class OpXFormer(abc.ABC):
    @abc.abstractmethod
    def xform(
        self, in_iter: typing.Iterable, **params: typing.Dict[str, typing.Any]
    ) -> typing.Iterable:
        return None

