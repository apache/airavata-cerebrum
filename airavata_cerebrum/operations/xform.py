import itertools
import tqdm
import typing
from ..base import OpXFormer


#
# Basic Transformers
#
class IdentityXformer(OpXFormer):
    def xform(self, in_iter: typing.Iterable | None, **params):
        return in_iter


class TQDMWrapper(OpXFormer):
    def xform(self, in_iter: typing.Iterable | None, **params):
        return tqdm.tqdm(in_iter)


class DataSlicer:
    def xform(self, in_iter: typing.Iterable, **params):
        default_args = {"stop": 10, "list": True}
        rarg = {**default_args, **params} if params is not None else default_args
        ditr = itertools.islice(in_iter, rarg["stop"])
        return list(ditr) if bool(rarg["list"]) else ditr


#
#
OpXFormer.register(IdentityXformer)
OpXFormer.register(TQDMWrapper)
OpXFormer.register(DataSlicer)


def query_register():
    return []


def xform_register():
    return [
        IdentityXformer,
        TQDMWrapper,
        DataSlicer
    ]
