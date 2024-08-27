import abc
import typing
import tqdm
import itertools
import jsonpath
import tqdm.contrib.logging as tqdm_log
from .abm_celltypes import CTDbGlifApiQuery, CTDbCellApiQuery, CTDbCellCacheQuery
from .abm_celltypes import CTDbCellAttrMapper, CTDbCellAttrFilter
from .abc_mouse import ABCDbMERFISH_CCFQuery
from .abm_celltypes import ABMCT_QUERY_REGISTER, ABMCT_XFORM_REGISTER
from .abc_mouse import ABC_QUERY_REGISTER, ABC_XFORM_REGISTER
from ..log.logging import LOGGER


#
# Abstract classes
#
class DbQuery(abc.ABC):
    @abc.abstractmethod
    def run(
        self,
        in_stream: typing.Union[typing.Iterable, None],
        **params: typing.Dict[str, typing.Any],
    ) -> typing.Iterable[typing.Dict[str, typing.Any]]:
        return None


class DbRecordXFormer(abc.ABC):
    @abc.abstractmethod
    def xform(
        self, in_iter: typing.Iterable, **params: typing.Dict[str, typing.Any]
    ) -> typing.Iterable:
        return None


#
# Basic Transformers
#
class IdentityXformer:
    def xform(self, in_val, **params):
        return in_val


class TQDMWrapper:
    def xform(self, in_lst: typing.List, **params):
        return tqdm.tqdm(in_lst)


class DataSlicer:
    def xform(self, in_iter: typing.Iterable, **params):
        default_args = {"stop": 10, "list": True}
        rarg = {**default_args, **params} if params is not None else default_args
        ditr = itertools.islice(in_iter, rarg["stop"])
        return list(ditr) if bool(rarg["list"]) else ditr


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
# ----- Registring the Sub-classes ------
#
DbQuery.register(CTDbCellCacheQuery)
DbQuery.register(CTDbCellApiQuery)
DbQuery.register(CTDbGlifApiQuery)
DbQuery.register(ABCDbMERFISH_CCFQuery)
#
DbRecordXFormer.register(IdentityXformer)
DbRecordXFormer.register(TQDMWrapper)
DbRecordXFormer.register(DataSlicer)
DbRecordXFormer.register(JPointerFilter)
DbRecordXFormer.register(IterJPatchFilter)
DbRecordXFormer.register(IterJPointerFilter)
DbRecordXFormer.register(CTDbCellAttrMapper)
DbRecordXFormer.register(CTDbCellAttrFilter)

#
# ----- Mapper, Filter and Query Registers ------
#
BASE_XFORM_REGISTER = {
    "IdentityXformer": IdentityXformer,
    __name__ + ".IdentityXformer": IdentityXformer,
    "TQDMWrapper": TQDMWrapper,
    __name__ + ".TQDMWrapper": TQDMWrapper,
    "DataSlicer": DataSlicer,
    __name__ + ".DataSlicer": DataSlicer,
    "JPointerFilter": JPointerFilter,
    __name__ + ".JPointerFilter": JPointerFilter,
    "IterJPatchFilter": IterJPatchFilter,
    __name__ + ".IterJPatchFilter": IterJPatchFilter,
    "IterJPointerFilter": IterJPointerFilter,
    __name__ + ".IterJPointerFilter": IterJPointerFilter,
}
BASE_QUERY_REGISTER = {}
#
QUERY_REGISTER = {**BASE_QUERY_REGISTER, **ABMCT_QUERY_REGISTER, **ABC_QUERY_REGISTER}
XFORM_REGISTER = {**BASE_XFORM_REGISTER, **ABMCT_XFORM_REGISTER, **ABC_XFORM_REGISTER}


def get_query_object(query_key, **init_params) -> typing.Union[DbQuery, None]:
    if query_key not in QUERY_REGISTER:
        return None
    return QUERY_REGISTER[query_key](**init_params)


def get_xform_object(xform_key, **init_params) -> typing.Union[DbRecordXFormer, None]:
    if xform_key not in XFORM_REGISTER:
        return None
    return XFORM_REGISTER[xform_key](**init_params)  # type:ignore


def run_dc_workflow(workflow_steps, wf_stream=None):
    for stx in workflow_steps:
        sname = stx["name"]
        iparams = stx["init_params"]
        eparams = stx["exec_params"]
        if stx["type"] == "query":
            LOGGER.info("Running Query : " + sname)
            qobj: typing.Union[DbQuery, None] = get_query_object(sname, **iparams)
            if qobj:
                wf_stream = qobj.run(wf_stream, **eparams)
                LOGGER.info("Completed Query : " + sname)
            else:
                LOGGER.error("Failed to find Query : " + sname)
        elif stx["type"] == "xform":
            LOGGER.info("Running XFormer : " + stx["name"])
            fobj: typing.Union[DbRecordXFormer, None] = get_xform_object(
                sname, **iparams
            )
            if fobj and wf_stream:
                wf_stream = fobj.xform(wf_stream, **eparams)
                LOGGER.info("Completed XForm : " + sname)
            else:
                LOGGER.error("Failed to find XFormer : " + sname)
    return wf_stream


def run_db_conn_workflows(db_conn_desc):
    db_conn_output = {}
    #
    for db_conn in db_conn_desc:
        db_name = db_conn["db_name"]
        db_wflow = db_conn["workflow"]
        LOGGER.info("Running workflow for db: " + db_name)
        with tqdm_log.logging_redirect_tqdm():
            model_itr = run_dc_workflow(db_wflow)
            if model_itr:
                db_conn_output[db_name] = list(model_itr)
        LOGGER.info("Completed workflow for db: " + db_name)
    #
    return db_conn_output


def run_db_conn_xformers(db_conn_data, xformers_config):
    neuron_dc_map = {}
    for db_name, wf_desc in xformers_config.items():
        LOGGER.info("Processing xformers for db " + db_name)
        wf_input = db_conn_data[db_name]
        neuron_dc = list(run_dc_workflow(wf_desc["workflow"], wf_input))  # type: ignore
        LOGGER.debug(
            ";".join(
                (
                    "WF Desc : " + str(wf_desc),
                    "WF IN:" + str(len(wf_input)),
                    "Neuron DC:" + str(len(wf_input)),
                )
            )
        )
        neuron_dc_map[db_name] = neuron_dc
        LOGGER.info("Completed processing xformers for db " + db_name)
    return neuron_dc_map


def dbconn2locations(db_conn_output, network_desc):
    network_locations = {}
    for location, location_desc in network_desc["locations"].items():
        neuron_desc_map = {}
        for neuron, neuron_desc in location_desc.items():
            LOGGER.info("Processing db connection for neuron " + neuron)
            db_conn_xformers = neuron_desc["db_connections"]
            neuron_dc_map = run_db_conn_xformers(db_conn_output, db_conn_xformers)
            neuron_dc_map["property_map"] = neuron_desc["property_map"]
            neuron_desc_map[neuron] = neuron_dc_map
            LOGGER.info("Completed db connection for neuron " + neuron)
        network_locations[location] = neuron_desc_map
    return network_locations
