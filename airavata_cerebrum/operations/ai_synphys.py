from ipywidgets.widgets.widget import _staticproperty
from .json_filter import JPointerFilter
import traitlets

class AISynPhysPairFilterTraits(traitlets.HasTraits):
    pre = traitlets.Unicode()
    post = traitlets.Unicode()

class AISynPhysPairFilter:
    def __init__(self, **init_params):
        self.jptr_filter = JPointerFilter(**init_params)
        self.path_fmt = "/0/{}"

    def xform(self, ct_iter, **params):
        npre = params["pre"] if "pre" in params else None
        npost = params["post"] if "post" in params else None
        rpath = self.path_fmt.format(repr((npre, npost)))
        return self.jptr_filter.xform(ct_iter, paths=[rpath], keys=["probability"])

    @_staticproperty
    def trait_class():
        return AISynPhysPairFilterTraits


def query_register():
    return []


def xform_register():
    return [
        AISynPhysPairFilter,
    ]
