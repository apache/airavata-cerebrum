import logging
import typing
import tqdm.contrib.logging as tqdm_log

from . import register, base
from .util.desc_config import CfgKeys

def _log():
    return logging.getLogger(__name__)


def run_workflow(
    workflow_steps: typing.List[typing.Dict],
    wf_iter: typing.Iterable | None = None
) -> typing.Iterable | None:
    for wf_step in workflow_steps:
        sname = wf_step[CfgKeys.NAME]
        slabel = wf_step[CfgKeys.LABEL] if CfgKeys.LABEL in wf_step else sname
        iparams: typing.Dict[str, typing.Any] = wf_step[CfgKeys.INIT_PARAMS]
        eparams: typing.Dict[str, typing.Any] = wf_step[CfgKeys.EXEC_PARAMS]
        match wf_step[CfgKeys.TYPE]:
            case "query":
                _log().info("Start Query : [%s]",  slabel)
                qobj: base.DbQuery | None = register.get_query_object(
                    sname, **iparams
                )
                if qobj:
                    wf_iter = qobj.run(wf_iter, **eparams)
                    _log().info("Complete Query : [%s]", slabel)
                else:
                    _log().error("Failed to find Query : [%s]",  sname)
            case "xform":
                _log().info("Running XFormer : [%s]",  slabel)
                fobj: base.OpXFormer | None = register.get_xform_op_object(
                    sname, **iparams
                )
                if fobj and wf_iter:
                    wf_iter = fobj.xform(wf_iter, **eparams)
                    _log().info("Complete XForm : [%s]", slabel)
                else:
                    _log().error("Failed to find XFormer : [%s]", sname)
    return wf_iter


def run_db_connect_workflows(
    source_data_cfg: typing.Dict[str, typing.Any]
) -> typing.Dict[str, typing.Any]:
    db_connect_output = {}
    #
    for db_name, db_wcfg in source_data_cfg.items():
        db_label = db_name
        if CfgKeys.LABEL in db_wcfg:
            db_label = db_wcfg[CfgKeys.LABEL]
        _log().info("Start db_connect workflow for db: [%s]",  db_label)
        with tqdm_log.logging_redirect_tqdm():
            model_itr = run_workflow(
                db_wcfg[CfgKeys.DB_CONNECT][CfgKeys.WORKFLOW]
            )
            if model_itr:
                db_connect_output[db_name] = list(model_itr)
        _log().info("Complete db_connect workflow for db: [%s]", db_label)
    #
    return db_connect_output


def run_ops_workflows(
    db_conn_data: typing.Dict[str, typing.Any],
    ops_config_desc: typing.Dict[str, typing.Any],
    ops_key: str | None = None
) -> typing.Dict[str, typing.Any]:
    op_output_data = {}
    for src_db, op_config in ops_config_desc.items():
        _log().info("Start op workflow for db [%s]", src_db)
        wf_input = db_conn_data[src_db]
        op_desc = op_config[ops_key] if ops_key else op_config
        op_output = list(
            run_workflow(op_desc[CfgKeys.WORKFLOW], wf_input) # type: ignore
        )
        _log().debug(
            "WF Desc: [%s]; WF IN: [%s]; Op output: [%s]",
            str(op_desc),
            str(len(wf_input)),
            str(len(op_output))
        )
        op_output_data[src_db] = op_output
        _log().info("Complete op workflow for db [%s]", src_db)
    return op_output_data


def map_srcdata_locations(
    source_data: typing.Dict[str, typing.Any],
    data2loc_map: typing.Dict[str, typing.Any],
) -> typing.Dict[str, typing.Any]:
    net_locations = {}
    for location, location_desc in data2loc_map.items():
        neuron_desc_map = {}
        for neuron, neuron_dcfg in location_desc.items():
            _log().info("Processing db connection for neuron [%s]", neuron)
            ops_dict = neuron_dcfg[CfgKeys.SRC_DATA]
            neuron_dc_map = run_ops_workflows(source_data, ops_dict)
            for dkey in neuron_dcfg.keys():
                if dkey != CfgKeys.SRC_DATA:
                    neuron_dc_map[dkey] = neuron_dcfg[dkey]
            neuron_desc_map[neuron] = neuron_dc_map
            _log().info("Completed db connection for neuron [%s]", neuron)
        net_locations[location] = neuron_desc_map
    return net_locations

def map_srcdata_connections(
    source_data: typing.Dict[str, typing.Any],
    data2con_map: typing.Dict[str, typing.Any],
) -> typing.Dict[str, typing.Any]:
    net_connections = {}
    for connx, connx_desc in data2con_map.items():
        conn_desc_map = {}
        _log().info("Processing db data for connex [%s]", connx)
        ops_dict = connx_desc[CfgKeys.SRC_DATA]
        conn_desc_map = run_ops_workflows(source_data, ops_dict)
        for dkey in connx_desc.keys():
            if dkey != CfgKeys.SRC_DATA:
                conn_desc_map[dkey] = connx_desc[dkey]
        _log().info("Completed db data for connex [%s]", connx)
        net_connections[connx] = conn_desc_map
    return net_connections
