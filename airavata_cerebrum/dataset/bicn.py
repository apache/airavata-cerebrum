import pathlib
import pandas as pd

BICN_BASE = "airavata-cerebrum/brain_atlases/"
#
BICN_DATA_DIR = {
    "cytoarch": BICN_BASE + "cytoarch",
    "adult_human": BICN_BASE + "adult_human",
}
#
BICN_DISECT_META = {
    "cytoarch": {
        "V1": "Dissection:_Primary_visual_cortex(V1).csv",
        "M1": "Dissection:_Primary_motor_cortex_(M1).csv",
    }
}
BICN_DB = list(BICN_DATA_DIR.keys())


def get_disect_meta(data_base, slice):
    """
    Load dissection data
    """
    data_dir = BICN_DATA_DIR[data_base]
    meta_fname = BICN_DISECT_META[data_base][slice]
    meta_file = pathlib.PurePath(data_dir, meta_fname)
    return pd.read_csv(meta_file, index_col=0)
