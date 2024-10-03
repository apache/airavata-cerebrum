import typing
import traitlets
#
from .. import base
from .json_filter import JPointerFilter


class AISynPhysPairFilter(base.OpXFormer):
    class FilterTraits(traitlets.HasTraits):
        pre = traitlets.Unicode()
        post = traitlets.Unicode()

    def __init__(self, **params):
        self.jptr_filter = JPointerFilter(**params)
        self.path_fmt = "/0/{}"

    def xform(
        self,
        in_iter: typing.Iterable | None,
        **params: typing.Any,
    ) -> typing.Iterable | None:
        npre = params["pre"] if "pre" in params else None
        npost = params["post"] if "post" in params else None
        rpath = self.path_fmt.format(repr((npre, npost)))
        return self.jptr_filter.xform(in_iter, paths=[rpath], keys=["probability"])

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.FilterTraits


#
# ------- Query and Xform Registers -----
#
def query_register() -> typing.List[type[base.DbQuery]]:
    return []


def xform_register() -> typing.List[type[base.OpXFormer]]:
    return [
        AISynPhysPairFilter,
    ]
