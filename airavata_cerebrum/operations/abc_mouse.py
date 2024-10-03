import traitlets
import typing
#
from .. import base
from .json_filter import JPointerFilter


class ABCDbMERFISH_CCFLayerRegionFilter(base.OpXFormer):
    class FilterTraits(traitlets.HasTraits):
        region = traitlets.Unicode()
        sub_region = traitlets.Unicode()

    def __init__(self, **params):
        self.jptr_filter = JPointerFilter(**params)
        self.path_fmt = "/0/{}/{}"

    def xform(self, in_iter: typing.Iterable | None, **params) -> typing.Iterable | None:
        region = params["region"]
        sub_region = params["sub_region"]
        rpath = self.path_fmt.format(region, sub_region)
        return self.jptr_filter.xform(
            in_iter,
            paths=[rpath],
            keys=[sub_region],
        )

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.FilterTraits


class ABCDbMERFISH_CCFFractionFilter(base.OpXFormer):
    class FilterTraits(traitlets.HasTraits):
        region = traitlets.Unicode()
        cell_type = traitlets.Unicode()

    def __init__(self, **params):
        self.jptr_filter = JPointerFilter(**params)
        self.ifrac_fmt = "/0/{}/inhibitory fraction"
        self.fwr_fmt = "/0/{}/fraction wi. region"
        self.frac_fmt = "/0/{}/{} fraction"

    def xform(self, in_iter: typing.Iterable | None, **params) -> typing.Iterable | None:
        region = params["region"]
        frac_paths = [
            self.ifrac_fmt.format(region),
            self.fwr_fmt.format(region),
        ]
        frac_keys = ["inh_fraction", "region_fraction"]
        if "cell_type" in params and params["cell_type"]:
            cell_type = params["cell_type"]
            frac_paths.append(self.frac_fmt.format(region, cell_type))
            frac_keys.append("fraction")
        return self.jptr_filter.xform(
            in_iter,
            paths=frac_paths,
            keys=frac_keys,
        )

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
        ABCDbMERFISH_CCFLayerRegionFilter,
        ABCDbMERFISH_CCFFractionFilter,
    ]
