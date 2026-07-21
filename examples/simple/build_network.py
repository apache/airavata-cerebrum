import os

import duckdb
import h5py
import numpy as np
import pandas as pd

from airavata_cerebrum.dataset.abc_mouse import (
    ABCDbMERFISH_CCFQuery,
    ABCDuckDBWriter,
    ExecParams,
    InitParams,
)

# Paths
DOWNLOAD_BASE = "./cache/abc_mouse/"
SEL_REGION = "VISp"
SEL_LAYER = "4"
ABM_DB = "abm_mouse.db"
OUT_DIR = "./"
NODE_POPULATION = "default"
EDGE_POPULATION = f"{NODE_POPULATION}_to_{NODE_POPULATION}"

#
N_NRN = 1000
AVG_DEGREE = 10  # average outgoing edges per neuron
N_EDGES = N_NRN * AVG_DEGREE
ID_RANGE = np.arange(N_NRN, dtype=np.int64)
RNG = np.random.default_rng(42)
# Node positions
RND_POSITIONS = RNG.uniform(0, 1.0, size=(N_NRN, 3)).astype(np.float32)
S_RAW, T_RAW = (
    RNG.integers(0, N_NRN, size=N_EDGES).astype(np.int64),
    RNG.integers(0, N_NRN, size=N_EDGES).astype(np.int64),
)
# Edge SRC/TGT ids
EDGE_SRC_ID, EDGE_TGT_ID = S_RAW[S_RAW != T_RAW], T_RAW[S_RAW != T_RAW]
# Edge Syn Weights
SYN_WEIGHTS = RNG.uniform(0.0, 1.0, size=len(EDGE_SRC_ID)).astype(np.float32)
DELAYS = RNG.uniform(0.5, 5.0, size=len(EDGE_SRC_ID)).astype(np.float32)


def make_dirs():
    if not os.path.exists(DOWNLOAD_BASE):
        os.makedirs(DOWNLOAD_BASE)
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)


def download_abc_mouse(db_file: str = ABM_DB):
    qry: ABCDbMERFISH_CCFQuery = ABCDbMERFISH_CCFQuery(
        init_params=InitParams(download_base=DOWNLOAD_BASE)
    )
    qitr = qry.run(ExecParams(region=[SEL_REGION]), None, None)
    with duckdb.connect(db_file) as conn:
        db_writer = ABCDuckDBWriter(conn)
        db_writer.write(qitr)


def neuron_counts(
    n: int = N_NRN, db_file: str = ABM_DB, layer: str = SEL_LAYER
) -> tuple[int, int]:
    r_sql = 'select "inhibitory fraction" from abm_mouse where layer='
    r_sql += f"'{layer}'"
    with duckdb.connect(db_file) as dconn:
        qrdf = dconn.sql(r_sql).to_df()
        inh_fraction = qrdf.iloc[0, 0]
        inh_neurons = int(n * inh_fraction)
        exc_neurons = n - inh_neurons
        return (exc_neurons, inh_neurons)


def nodes_file(n_exc: int, n_inh: int):
    assert n_inh + n_exc == N_NRN
    # ── Write nodes.h5
    with h5py.File(f"{OUT_DIR}/nodes.h5", "w") as f:
        f.attrs["magic"] = np.uint32(0x0A7A)
        f.attrs["version"] = np.array([0, 1], dtype=np.uint32)
        pop = f.require_group(f"nodes/{NODE_POPULATION}")
        pop.create_dataset("node_id", data=ID_RANGE)
        pop.create_dataset(
            "node_type_id", data=np.array([100] * n_inh + [200] * n_exc, dtype=np.int64)
        )
        pop.create_dataset("node_group_id", data=ID_RANGE)
        pop.create_dataset("node_group_index", data=ID_RANGE)
        grp = pop.require_group("0")
        grp.create_dataset("x", data=RND_POSITIONS[:, 0])
        grp.create_dataset("y", data=RND_POSITIONS[:, 1])
        grp.create_dataset("z", data=RND_POSITIONS[:, 2])


def node_types_file():
    node_type_rows = [
        dict(
            node_type_id=100,
            population=NODE_POPULATION,
            model_type="point_neuron",
            model_template="nrn:IntFire1",
            dynamics_params="inhibitory_params.json",
            cell_class="inhibitory",
            ei="i",
        ),
        dict(
            node_type_id=200,
            population=NODE_POPULATION,
            model_type="point_neuron",
            model_template="nrn:IntFire1",
            dynamics_params="excitatory_params.json",
            cell_class="excitatory",
            ei="e",
        ),
    ]
    pd.DataFrame(node_type_rows).to_csv(
        f"{OUT_DIR}/node_types.csv", sep=" ", index=False
    )


def edges_file(n_exc: int, n_inh: int):
    assert n_inh + n_exc == N_NRN
    src_e = EDGE_SRC_ID < n_exc
    tgt_e = EDGE_TGT_ID < n_exc
    edge_type_ids = np.where(
        src_e & tgt_e,
        10,
        np.where(src_e & ~tgt_e, 11, np.where(~src_e & tgt_e, 20, 21)),
    ).astype(np.int64)
    # Write edges.h5
    with h5py.File(f"{OUT_DIR}/edges.h5", "w") as f:
        f.attrs["magic"] = np.uint32(0x0A7A)
        f.attrs["version"] = np.array([0, 1], dtype=np.uint32)
        pop = f.require_group(f"edges/{EDGE_POPULATION}")
        ds = pop.create_dataset("source_node_id", data=EDGE_SRC_ID)
        ds.attrs["node_population"] = NODE_POPULATION
        ds = pop.create_dataset("target_node_id", data=EDGE_TGT_ID)
        ds.attrs["node_population"] = NODE_POPULATION
        pop.create_dataset("edge_type_id", data=edge_type_ids)
        pop.create_dataset(
            "edge_group_id", data=np.zeros(len(EDGE_SRC_ID), dtype=np.int64)
        )
        pop.create_dataset(
            "edge_group_index", data=np.arange(len(EDGE_SRC_ID), dtype=np.int64)
        )
        grp = pop.require_group("0")
        grp.create_dataset("syn_weight", data=SYN_WEIGHTS)
        grp.create_dataset("delay", data=DELAYS)


def edge_types_file():
    edge_type_rows = [
        dict(
            edge_type_id=10,
            population=EDGE_POPULATION,
            model_template="Exp2Syn",
            dynamics_params="AMPA_ExcToExc.json",
            connection_type="ExcToExc",
        ),
        dict(
            edge_type_id=11,
            population=EDGE_POPULATION,
            model_template="Exp2Syn",
            dynamics_params="AMPA_ExcToInh.json",
            connection_type="ExcToInh",
        ),
        dict(
            edge_type_id=20,
            population=EDGE_POPULATION,
            model_template="Exp2Syn",
            dynamics_params="GABA_InhToExc.json",
            connection_type="InhToExc",
        ),
        dict(
            edge_type_id=21,
            population=EDGE_POPULATION,
            model_template="Exp2Syn",
            dynamics_params="GABA_InhToInh.json",
            connection_type="InhToInh",
        ),
    ]
    # Write edge_types.csv
    pd.DataFrame(edge_type_rows).to_csv(
        f"{OUT_DIR}/edge_types.csv", sep=" ", index=False
    )


def main():
    make_dirs()
    download_abc_mouse()
    n_exc, n_inh = neuron_counts()
    nodes_file(n_exc, n_inh)
    node_types_file()
    edges_file(n_exc, n_inh)
    edge_types_file()


if __name__ == "__main__":
    main()
