import itertools
import typing
import tqdm
import traitlets
#
from ..base import OpXFormer


#
# Basic Transformers
#
class IdentityXformer(OpXFormer):
    class IdTraits(traitlets.HasTraits):
        pass

    def xform(
        self,
        in_iter: typing.Iterable | None,
        **params,
    ) -> typing.Iterable | None:
        return in_iter

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.IdTraits


class TQDMWrapper(OpXFormer):
    class TqTraits(traitlets.HasTraits):
        pass

    def xform(
        self,
        in_iter: typing.Iterable | None,
        **params,
    ) -> typing.Iterable | None:
        return tqdm.tqdm(in_iter)

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.TqTraits


class DataSlicer:
    class SliceTraits(traitlets.HasTraits):
        stop = traitlets.Int()
        list = traitlets.Bool()

    def xform(
        self,
        in_iter: typing.Iterable | None,
        **params,
    ) -> typing.Iterable | None:
        default_args = {"stop": 10, "list": True}
        rarg = default_args | params if params else default_args
        if in_iter:
            ditr = itertools.islice(in_iter, rarg["stop"])
            return list(ditr) if bool(rarg["list"]) else ditr


#
#
def query_register():
    return []


def xform_register():
    return [
        IdentityXformer,
        TQDMWrapper,
        DataSlicer
    ]
