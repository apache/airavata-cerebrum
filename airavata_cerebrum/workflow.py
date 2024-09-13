import typing
import tqdm.contrib.logging as tqdm_log

from . import register, base
from .util.log.logging import LOGGER
from .model import desc as cbmdesc


def run_workflow(
    workflow_steps: typing.List[typing.Dict], wf_stream: typing.Iterable | None = None
) -> typing.Iterable | None:
    for wf_stx in workflow_steps:
        sname = wf_stx[cbmdesc.NAME_KEY]
        slabel = wf_stx[cbmdesc.LABEL_KEY] if cbmdesc.LABEL_KEY in wf_stx else sname
        iparams: typing.Dict[str, typing.Any] = wf_stx["init_params"]
        eparams: typing.Dict[str, typing.Any] = wf_stx["exec_params"]
        match wf_stx[cbmdesc.TYPE_KEY]:
            case "query":
                LOGGER.info("Start Query : [%s]",  slabel)
                qobj: base.DbQuery | None = register.QUERY_REGISTER.object(
                    sname, **iparams
                )
                if qobj:
                    wf_stream = qobj.run(wf_stream, **eparams)
                    LOGGER.info("Complete Query : [%s]", slabel)
                else:
                    LOGGER.error("Failed to find Query : [%s]",  sname)
            case "xform":
                LOGGER.info("Running XFormer : [%s]",  slabel)
                fobj: typing.Union[base.OpXFormer, None] = (
                    register.XFORM_REGISTER.object(sname, **iparams)
                )
                if fobj and wf_stream:
                    wf_stream = fobj.xform(wf_stream, **eparams)
                    LOGGER.info("Complete XForm : [%s]", slabel)
                else:
                    LOGGER.error("Failed to find XFormer : [%s]", sname)
    return wf_stream


def run_db_connect_workflows(
    source_data_cfg: typing.Dict[str, typing.Any]
) -> typing.Dict[str, typing.Any]:
    db_connect_output = {}
    #
    for db_name, db_cfg in source_data_cfg.items():
        db_label = db_name
        if cbmdesc.LABEL_KEY in db_cfg:
            db_label = db_cfg[cbmdesc.LABEL_KEY]
        LOGGER.info("Start db_connect workflow for db: [%s]",  db_label)
        with tqdm_log.logging_redirect_tqdm():
            model_itr = run_workflow(
                db_cfg[cbmdesc.DB_CONNECT_KEY][cbmdesc.WORKFLOW_KEY]
            )
            if model_itr:
                db_connect_output[db_name] = list(model_itr)
        LOGGER.info("Complete db_connect workflow for db: [%s]", db_label)
    #
    return db_connect_output


def run_ops_workflows(
    db_conn_data: typing.Dict[str, typing.Any],
    ops_config_desc: typing.Dict[str, typing.Any],
    ops_key: str | None = None
) -> typing.Dict[str, typing.Any]:
    op_output_data = {}
    for src_db, op_config in ops_config_desc.items():
        LOGGER.info("Start op workflow for db [%s]", src_db)
        wf_input = db_conn_data[src_db]
        op_desc = op_config[ops_key] if ops_key else op_config
        op_output = list(
            run_workflow(op_desc[cbmdesc.WORKFLOW_KEY], wf_input) # type: ignore
        )
        LOGGER.debug(
            "WF Desc: [%s]; WF IN: [%s]; Op output: [%s]",
            str(op_desc),
            str(len(wf_input)),
            str(len(op_output))
        )
        op_output_data[src_db] = op_output
        LOGGER.info("Complete op workflow for db [%s]", src_db)
    return op_output_data


def map_srcdata_locations(
    source_data: typing.Dict[str, typing.Any],
    data2loc_map: typing.Dict[str, typing.Any],
) -> typing.Dict[str, typing.Any]:
    net_locations = {}
    for location, location_desc in data2loc_map.items():
        neuron_desc_map = {}
        for neuron, neuron_dcfg in location_desc.items():
            LOGGER.info("Processing db connection for neuron [%s]", neuron)
            ops_dict = neuron_dcfg[cbmdesc.DB_DATA_SRC_KEY]
            neuron_dc_map = run_ops_workflows(source_data, ops_dict)
            for dkey in neuron_dcfg.keys():
                if dkey != cbmdesc.DB_DATA_SRC_KEY:
                    neuron_dc_map[dkey] = neuron_dcfg[dkey]
            neuron_desc_map[neuron] = neuron_dc_map
            LOGGER.info("Completed db connection for neuron [%s]", neuron)
        net_locations[location] = neuron_desc_map
    return net_locations
