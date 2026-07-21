import marimo

__generated_with = "0.23.8"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Exploration of Model Source Data

    In construction of V1L4, data downloaded from the Brain atlases are stored in
    the `data/v1l4` directory as json files and as a duckdb database.

    We examine the downloaded data by loading as data frames and exploring using
    the marimo dataframe viewer.
    """)
    return


@app.cell
def _():
    import ast
    import itertools
    import marimo as mo
    import airavata_cerebrum.util.io as cuio
    import airavata_cerebrum.dataset.abc_mouse as abcm
    import airavata_cerebrum.dataset.abm_celltypes as abmct
    import airavata_cerebrum.dataset.ai_synphys as aisyn
    import airavata_cerebrum.workflow as abmwf
    import airavata_cerebrum.register as abmreg
    import duckdb
    import polars as pl
    import typing as t

    src_data_file = "./data/v1l4/db_connect_output.json"
    test_db = "./data/v1l4/db_connect_output.db"
    src_data = cuio.load_json(src_data_file)
    test_conn = duckdb.connect(test_db)
    #db_conn = duckdb.connect("./v1l4/recipe/db_connect_output.db")
    return abcm, abmct, aisyn, mo, src_data


@app.cell
def _(mo):
    mo.md(r"""
    ## Allen Cell Types Database

    The downloaded information about the celltypes from
    the [cell types database](https://celltypes.brain-map.org).

    After selecting the database key from the JSON object,
    we can build a data frame with
    (a) only the `glif` information.
    (b) the neuron model information
    """)
    return


@app.cell
def _(abmct, src_data):
    # From the src_data JSON object, selct the data of interest by its key
    tlist = src_data['airavata_cerebrum.dataset.abm_celltypes']

    # Select the glif data information
    abmct.DFBuilder.build(tlist, df_source="glif")
    return (tlist,)


@app.cell
def _(abmct, tlist):
    # Select the neuron model information
    abmct.DFBuilder.build(tlist, df_source="nm")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Allen Synaptic Physiology Database

    The downloaded information about the synapse connection from
    the [synaptic physiology database](https://brain-map.org/our-research/connectivity/synaptic-physiology).

    After selecting the database key from the JSON object,
    we can build a data frame with the `connection probability` information.
    """)
    return


@app.cell
def _(aisyn, src_data):
    slist = src_data["airavata_cerebrum.dataset.ai_synphys"]
    aisyn.DFBuilder.build(slist)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##  Mouse Whole Brain Atlas

    The downloaded information about the neuron composition from
    the [mouse brain atlas](https://alleninstitute.github.io/abc_atlas_access).

    After selecting the database key from the JSON object,
    we can build a data frame with the `neuron cells proportion` information.
    """)
    return


@app.cell
def _(abcm, src_data):
    alist = src_data["airavata_cerebrum.dataset.abc_mouse"]
    abcm.DFBuilder.build(alist)
    return


if __name__ == "__main__":
    app.run()
