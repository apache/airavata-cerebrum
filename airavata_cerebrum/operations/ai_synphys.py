from .json_filter import JPointerFilter


class AISynPhysPairFilter:
    def __init__(self, **init_params):
        self.jptr_filter = JPointerFilter(**init_params)
        self.path_fmt = "/0/{}"

    def xform(self, ct_iter, **params):
        npre = params["pre"] if "pre" in params else None
        npost = params["post"] if "post" in params else None
        rpath = self.path_fmt.format(repr((npre, npost)))
        return self.jptr_filter.xform(ct_iter, paths=[rpath], keys=["probability"])


def query_register():
    return []


def xform_register():
    return [
        AISynPhysPairFilter,
    ]
