import logging
import json
import tqdm.contrib.logging as tqdm_log
from airavata_cerebrum.atlas.data.base import run_dc_workflow

CT_WORKFLOW_JSON = "./tests/ct_workflow.json"

logging.basicConfig(level=logging.INFO)
workflow_desc = {}
model_itr = None
with open(CT_WORKFLOW_JSON) as ofx:
    workflow_desc = json.load(ofx)
with tqdm_log.logging_redirect_tqdm():
    model_itr = run_dc_workflow(workflow_desc["connection"]["workflow"])
    if model_itr:
        lxl = list(model_itr)
