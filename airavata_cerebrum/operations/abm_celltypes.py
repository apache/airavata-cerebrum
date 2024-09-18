import traitlets
import typing
from .. import base
from .json_filter import IterJPatchFilter, IterJPointerFilter
from .dict_filter import IterAttrFilter


class CTModelNameFilter:
    class FilterTraits(traitlets.HasTraits):
        name = traitlets.Unicode()

    def __init__(self, **init_params):
        self.name = __name__ + ".CTModelNameFilter"
        self.filter_fmt = "$.glif.neuronal_models[?('{}' in @.name)]"
        self.dest_path = "/glif/neuronal_models"
        self.jpatch_filter = IterJPatchFilter(**init_params)

    def xform(
        self,
        in_iter: typing.Iterable | None,
        **params: typing.Any,
    ) -> typing.Iterable | None:
        model_name = params["name"]
        filter_exp = self.filter_fmt.format(model_name)
        return self.jpatch_filter.xform(in_iter,
                                        filter_exp=filter_exp,
                                        dest_path=self.dest_path)

    @classmethod
    def trait_type(cls):
        return cls.FilterTraits


class CTExplainedRatioFilter(base.OpXFormer):
    class FilterTraits(traitlets.HasTraits):
        ratio = traitlets.Float()

    def __init__(self, **init_params):
        self.name = __name__ + ".CTExplainedRatioFilter"
        self.filter_fmt = "$.glif.neuronal_models[0].neuronal_model_runs[?(@.explained_variance_ratio > {})]"
        self.dest_path = "/glif/neuronal_models/0/neuronal_model_runs"
        self.final_path = "/glif/neuronal_models/0/neuronal_model_runs/0"
        self.jpatch_filter = IterJPatchFilter(**init_params)
        self.jptr_filter = IterJPointerFilter(**init_params)

    def xform(self, in_iter, **params):
        ratio_value = params["ratio"]
        filter_exp = self.filter_fmt.format(ratio_value)
        patch_out = self.jpatch_filter.xform(in_iter,
                                             filter_exp=filter_exp,
                                             dest_path=self.dest_path)
        return self.jptr_filter.xform(patch_out,
                                      path=self.final_path)

    @classmethod
    def trait_type(cls):
        return cls.FilterTraits


class CTPropertyFilter:
    class FilterTraits(traitlets.HasTraits):
        key = traitlets.Unicode()
        region = traitlets.Unicode()
        layer = traitlets.Unicode()
        line = traitlets.Unicode()
        reporter_status = traitlets.Unicode()

    QUERY_FILTER_MAP = {
        "region": ["structure_parent__acronym", "__eq__"],
        "layer": ["structure__layer", "__eq__"],
        "line": ["line_name", "__contains__"],
        "reporter_status": ["cell_reporter_status", "__eq__"]
    }

    def __init__(self, **init_params):
        self.cell_attr_filter = IterAttrFilter(**init_params)

    def xform(self, ct_iter, **params):
        key = params["key"] if "key" in params else None
        filters = []
        for pkey, valx in params.items():
            if pkey in CTPropertyFilter.QUERY_FILTER_MAP:
                filter_attr = CTPropertyFilter.QUERY_FILTER_MAP[pkey].copy()
                filter_attr.append(str(valx))
                filters.append(filter_attr)
        return self.cell_attr_filter.xform(ct_iter,
                                           key=key,
                                           filters=filters)

    @classmethod
    def trait_type(cls):
        return cls.FilterTraits


#
base.OpXFormer.register(CTModelNameFilter)
base.OpXFormer.register(CTExplainedRatioFilter)
base.OpXFormer.register(CTPropertyFilter)


def query_register():
    return []


def xform_register():
    return [
        CTModelNameFilter,
        CTExplainedRatioFilter,
        CTPropertyFilter,
    ]
