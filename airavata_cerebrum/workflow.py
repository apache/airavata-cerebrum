import typing
import tqdm.contrib.logging as tqdm_log

from . import register, base
from .util.log.logging import LOGGER


def run_dc_workflow(
    workflow_steps: typing.List[typing.Dict], wf_stream: typing.Iterable | None = None
) -> typing.Iterable | None:
    for wf_stx in workflow_steps:
        sname = wf_stx["name"]
        iparams: typing.Dict[str, typing.Any] = wf_stx["init_params"]
        eparams: typing.Dict[str, typing.Any] = wf_stx["exec_params"]
        match wf_stx["type"]:
            case "query":
                LOGGER.info("Running Query : " + sname)
                qobj: base.DbQuery | None = register.QUERY_REGISTER.object(
                    sname, **iparams
                )
                if qobj:
                    wf_stream = qobj.run(wf_stream, **eparams)
                    LOGGER.info("Completed Query : " + sname)
                else:
                    LOGGER.error("Failed to find Query : " + sname)
            case "xform":
                LOGGER.info("Running XFormer : " + wf_stx["name"])
                fobj: typing.Union[base.OpXFormer, None] = (
                    register.XFORM_REGISTER.object(sname, **iparams)
                )
                if fobj and wf_stream:
                    wf_stream = fobj.xform(wf_stream, **eparams)
                    LOGGER.info("Completed XForm : " + sname)
                else:
                    LOGGER.error("Failed to find XFormer : " + sname)
    return wf_stream


def run_db_connect_workflows(
    db_conn_desc: typing.Dict[str, typing.Any]
) -> typing.Dict[str, typing.Any]:
    db_conn_output = {}
    #
    for db_name, db_wflow in db_conn_desc.items():
        LOGGER.info("Running workflow for db: " + db_name)
        with tqdm_log.logging_redirect_tqdm():
            model_itr = run_dc_workflow(db_wflow)
            if model_itr:
                db_conn_output[db_name] = list(model_itr)
        LOGGER.info("Completed workflow for db: " + db_name)
    #
    return db_conn_output


def run_op_xformers(
    db_conn_data: typing.Dict[str, typing.Any],
    xformers_config: typing.Dict[str, typing.Any],
) -> typing.Dict[str, typing.Any]:
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


def dbconn2locations(
    db_conn_output: typing.Dict[str, typing.Any],
    network_desc: typing.Dict[str, typing.Any],
) -> typing.Dict[str, typing.Any]:
    network_locations = {}
    for location, location_desc in network_desc["locations"].items():
        neuron_desc_map = {}
        for neuron, neuron_desc in location_desc.items():
            LOGGER.info("Processing db connection for neuron " + neuron)
            db_conn_xformers = neuron_desc["db_connections"]
            neuron_dc_map = run_op_xformers(db_conn_output, db_conn_xformers)
            neuron_dc_map["property_map"] = neuron_desc["property_map"]
            neuron_desc_map[neuron] = neuron_dc_map
            LOGGER.info("Completed db connection for neuron " + neuron)
        network_locations[location] = neuron_desc_map
    return network_locations
