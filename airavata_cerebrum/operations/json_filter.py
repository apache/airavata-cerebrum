import jsonpath

from .. import base
from ..util.log.logging import LOGGER


class JPointerFilter:
    def __init__(self, **init_params):
        self.name = __name__ + ".JPointerFilter"
        self.patch_out = None

    def resolve(self, fpath, dctx):
        jptr = jsonpath.JSONPointer(fpath)
        if jptr.exists(dctx):
            return jptr.resolve(dctx)
        else:
            return None

    def xform(self, dctx, **params):
        """
        Filter the output only if the destination path is present in dctx.

        Parameters
        ----------
        dctx : dict
           dictonary of ddescription
        params: requires the following keyword parameters
          {
            paths : List of JSON Path destination
            keys : Destination keys
          }

        Returns
        -------
        dctx: dict | None
           dict or None
        """
        fp_lst = params["paths"]
        key_lst = params["keys"]
        return [{key: self.resolve(fpath, dctx) for fpath, key in zip(fp_lst, key_lst)}]


class IterJPatchFilter:
    def __init__(self, **init_params):
        self.name = __name__ + ".IterJPatchFilter"
        self.patch_out = None

    def patch(self, ctx, filter_exp, dest_path):
        fx = jsonpath.findall(filter_exp, ctx)
        try:
            if jsonpath.JSONPointer(dest_path).exists(ctx):
                return jsonpath.patch.apply(
                    [{"op": "replace", "path": dest_path, "value": fx}], ctx
                )
            else:
                return None
        except jsonpath.JSONPatchError as jpex:
            LOGGER.error("JPEX : ", jpex)
            return None

    def xform(self, ct_iter, **params):
        """
        Select the output matching the filter expression and place in
        the destination.

        Parameters
        ----------
        ct_iter : Iterator
           iterator of cell type descriptions
        filter_params: requires the following keyword parameters
          {
            filter_exp : JSON path filter expression
            dest_path : JSON Path destination
          }

        Returns
        -------
        ct_iter: iterator
           iterator of cell type descriptions
        """
        filter_exp = params["filter_exp"]
        dest_path = params["dest_path"]
        return iter(self.patch(x, filter_exp, dest_path) for x in ct_iter if x)


class IterJPointerFilter:
    def __init__(self, **init_params):
        self.name = __name__ + ".IterJPointerFilter"
        self.patch_out = None

    def exists(self, ctx, fpath):
        return jsonpath.JSONPointer(fpath).exists(ctx)

    def xform(self, ct_iter, **params):
        """
        Filter the output only if the destination path is present.

        Parameters
        ----------
        ct_iter : Iterator
           iterator of cell type descriptions
        params: requires the following keyword parameters
          {
            path : JSON Path destination
          }

        Returns
        -------
        ct_iter: iterator
           iterator of cell type descriptions
        """
        fpath = params["path"]
        return iter(x for x in ct_iter if x and self.exists(x, fpath))


#
# ----- Mapper, Filter and Query Registers ------
#
base.OpXFormer.register(JPointerFilter)
base.OpXFormer.register(IterJPointerFilter)
base.OpXFormer.register(IterJPatchFilter)


def query_register():
    return []


def xform_register():
    return [
        IterJPointerFilter,
        IterJPatchFilter,
        JPointerFilter,
    ]
