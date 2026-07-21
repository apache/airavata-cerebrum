import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **NOTE: By default, the cells are NOT run automatically. Click the play button below to populate the cells**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # V1 Model using Apache Cerebrum
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(f"""
    This notebook walks through the Cerebrum workflow to construct
    a simple *V1* model. The notebook 
    - overviews the data sources configuration,
    - explore the downloaded data,
    - build the model from code,
    - run the simulation, and finally 
    - visualize the simulation outputs.

    ## Structure of the Cerebrum Workflow

    {mo.image("img/Workflow.png", width=500)}


    The workflow steps to construct a model in Cerebrum are as follows (as shown in the figure above): 

    1. Query and download the requisite data from public databases.
       In case of V1, we acquire data from the following databases:
         - Allen Model Database,
         - Allen Brain Atlas
         - Synaptic Physiology datasets. 
    2. Map the acquired data to the relevant regions of the model to be built. 
    3. Fill-in any missing details via an optional user-defined **custom mod** definitions. 
    4. Realize the final network of neurons in the SONATA format.


    ## Model Recipe

    Model Recipe (files in sub-folder `recipes/v1`) defines key components for constructing a Network with Cerebrum. 

    - **Data Providers:** Links to source database and query parameters
    - **Filter and Transformers:** Data processing workflow such as filtering via selection criteria on the queried data.
    - **Data2Model Mappers:** Mapper methods that map data to model components.
    - **User Modifications:** Descriptions of user additions/removals to the purely data-driven model

    The following figure shows the overall structure of a Model recipe definition.

    {mo.image("img/Recipe.png", width=500)}

    ## Install dependencies

    The Notebook is expected to be run in a `conda` environment with `cerebrum` and other dependcies installed.
    See the [README.md](README.md) file for the instructions to create the environment.
    """)
    return


@app.cell
def _():
    import marimo as mo
    #
    from airavata_cerebrum.recipe import RecipeSetup, ModelRecipe
    from airavata_cerebrum.model.structure import Network
    #from airavata_cerebrum.view.tree import DataSourceRecipeView, Data2ModelRecipeView, NetworkStructureView

    from airavata_cerebrum.view import BaseTree
    from airavata_cerebrum.view.motree import DataSourceRecipeView, Data2ModelRecipeView, NetworkStructureView
    #
    from src import model as v1model
    from src import operations as v1ops
    from src import params as v1params
    #
    import nest
    from nest.lib.hl_api_sonata import SonataNetwork
    from nest.lib.hl_api_nodes import Create as NestCreate
    from nest.lib.hl_api_connections import Connect as NestConnect
    from nest.lib.hl_api_types import NodeCollection

    return (
        BaseTree,
        Data2ModelRecipeView,
        DataSourceRecipeView,
        ModelRecipe,
        Network,
        NetworkStructureView,
        mo,
        v1params,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # V1 Recipe Description
    ## V1 Model Recipe

    The Cerebrum V1 model recipe includes the following three sections. For V1, the model recipe is defined by a collection of human-readable json files in the  directory `recipes/v1`.

    1. **source_data**
        - Describes how the source databases are connected.
        - Defines the operations applied to the downloaded data such as filters etc.
        - For V1, the `recipes/v1/recipe_data.json` file contains the **source_data** section.
    2. **data2model_map**
        - Describes mapping between source data and different regions of the model.
        - For V1, we have five recipe files, one corresponding each layers of the V1 model that contains the **data2model_map** section, corresponding to each layer.
            - `recipes/v1/recipe_dm_l1.json`
            - `recipes/v1/recipe_dm_l23.json`
            - `recipes/v1/recipe_dm_l4.json`
            - `recipes/v1/recipe_dm_l5.json`
            - `recipes/v1/recipe_dm_l6.json`
    3. **custom mod**
        - Describes the user modifications applied after a model skeleton build from the data and mapping ((1) and (2) above).
        - For V1, we have eight different custom mod files, one corresponding to each level of the V1 model -- containing the user **cust mod**s for each layer and the BKG and LGN layers.
            - `recipes/v1/custom_mod_l1.json`
            - `recipes/v1/custom_mod_l23.json`
            - `recipes/v1/custom_mod_l4.json`
            - `recipes/v1/custom_mod_l5.json`
            - `recipes/v1/custom_mod_l6.json`
            - `recipes/v1/custom_mod_ext.json`, `recipes/v1/custom_mod_ext_bkg.json` and `recipes/v1/custom_mod_ext_lgn.json`

    ***NOTE: The following code loads all the above recipe files an initializes a python `ModelSetup` object that performs basic input validation, and captures all the parameters. Custom modifications are loaded separately as a `cerebrum.structure.Network` object.***
    """)
    return


@app.cell
def _(Network, v1params):
    #
    # The following code initializes the parameters of the model
    params = v1params.RecipeParams()
    params.ncells = 30000
    #
    # After setting the model parameters, we create a ModelSetup object
    # that builds a framework with some simple valiations
    md_recipe_setup = params.recipe_setup()

    #
    # Custom mods are built as a separate object, which will be 
    # combined later after a skeleton is built.
    custom_mod_struct = Network.from_file_list(params.custom_mod) 

    # View tree widthss
    tree_view_widths = [0.4, 0.6]
    return custom_mod_struct, md_recipe_setup, params, tree_view_widths


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exploring the Source Data Section

    Cerebrum includes modules that can download data from multiple
    data provider modules. It includes
    - Methods for defining the querying from the database and
      filter the data based on specific criteria.
    - Utilities to visualize the data provider configurations in
      easy-to-understand explorer view inside Jupyter notebook
      with the relevant parameters displayed in the side panel.

    Cerebrum Construction of Mouse V1 is enabled by data with
    three different data providers:
    - Allen Cell Types database,
    - Allen Brain Cell Atlas,
    - AI Synaptic Physiology Database, and
    - Gouwens et. al. (2019) neuron classification based on
      electrophysiolocial data.

    ***NOTE: Running code below within the jupyter notebook will display
    the structure of the recipe's source_data section***
    """)
    return


@app.cell
def _(md_recipe_setup):
    md_recipe_setup.get_section('source_data')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualize Source Data

    Cerebrum also provides a Jupyter Notebook Widgets that
    aids the visualization of the source data configration.
    The `DataSourceRecipeView` renders the data source
    information and query parameters in a user friendly output
    as compared to the strict names in json file.

    **NOTE: Running the code below with show an interactive explorer-like tree structure**
    """)
    return


@app.cell
def _(DataSourceRecipeView, md_recipe_setup, mo):
    sd_explorer = DataSourceRecipeView(md_recipe_setup).build()
    sd_tree, sd_panels = sd_explorer.view_components()
    sd_motree = mo.ui.anywidget(sd_tree)
    return sd_motree, sd_panels


@app.cell
def _(BaseTree, mo, sd_motree, sd_panels, tree_view_widths):
    sd_selected = BaseTree.panel_selector(sd_motree, sd_panels)
    mo.hstack(
        [
            sd_motree,
            sd_selected.layout if sd_selected else None
        ],
        widths=tree_view_widths
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data2Model Mapping

    Definitions for data2model_map includes two subsections:

    `data2model_map` section of the recipe includes two subsections:

    1. *Locations:*
        - Locations are hiearchially defined and each sub-location
          declares the links to the acquired data.
        - For __V1__, (i) acquired cell types information from Cell types
          database maps to the neuron models, and
          (ii) the summary information from MERFISH single-cell atlas
          map to the distribution of neuron types.
        - For __V1__, we map eight different neuron types to the specific
          models and the region fractions.
    2. *Connections:*
        - Connections are defined as a set of pairs to neurons,
          with pair defining the data links.
        - AI synaptic physiology data is mapped to the connection
          probabilities between the pairs of neuron classes.
        - For __V1__, we map each of the different neuron pairs to the
          AI Syn. Phys. Data outputs


    ***NOTE: Running code below within the notebook will display the tree structure of the Recipe's data2model section***
    """)
    return


@app.cell
def _(md_recipe_setup):
    md_recipe_setup.get_section('data2model_map')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(f"""
    ### Visualize Data2Model Mapping

    Similar to Source Data section, Cerebrum also provides a Jupyter Notebook Widget
    to visualize the data2model section of the recipe.
    The `Data2ModelRecipeView` renders with a user friendly output compared to
    the strict names in json file. 

    {mo.image('img/Data2Model.png', width=800)}

    ***NOTE: Running the Recipe View code below will display the Tree widget 
    (as shown in the above snapshot), when run inside the notebook***
    """)
    return


@app.cell
def _(Data2ModelRecipeView, md_recipe_setup, mo):
    dm_explorer = Data2ModelRecipeView(md_recipe_setup).build()
    dm_tree, dm_panels = dm_explorer.view_components()
    dm_motree = mo.ui.anywidget(dm_tree)
    return dm_motree, dm_panels


@app.cell
def _(BaseTree, dm_motree, dm_panels, mo, tree_view_widths):
    dm_selected = BaseTree.panel_selector(dm_motree, dm_panels)
    mo.hstack(
        [
            dm_motree,
            dm_selected.layout if dm_selected else None
        ],
        widths=tree_view_widths
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Custom Modifications

    Through the custom modification json files,users can
    provide additional details required for network
    construction. They can include information that are either
    (a) not available in the linked databases or
    (b) not applicable for the model being built and over-ride it.


    For the Mouse V1, custom modifications include:

    1. Dimensions of each region in the model.
    2. Connection Parameters not available within the AI Syn. Phys. database.
    3. Details of the networks that are external to V1 : LGN and the background networks.

    ***NOTE: Running code below within the  notebook will display
    the tree structure of the Recipe's custom_mod***
    """)
    return


@app.cell
def _():
    # Uncomment
    #
    # custom_mod_struct.model_dump()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Mapper classess for  Network construction
    To realize model recipe to SONATA Network, three python classes that translate from the model skeleton to neurons and connections.

    1. *Region Mapper* : Defined in `mousev1.model.V1RegionMapper`, maps the location data gathered from data sources/user mods to a region in the network.
    2. *Neuron Mapper* : Defined in `mousev1.model.V1NeuronMapps`, maps the neuron information within in a given location data to a neuron class within the region.
    3. *Connection Mapper*: Defined in `mousev1.model.V1ConnectionMapper`, maps the connection data to realize the connection details in the network of neurons.

    In addition a *Network Builder* class (`mousev1.model.V1BMTKNetworkBuilder`) is also defined that translates the model description to SONATA network.
    """)
    return


@app.cell
def _(ModelRecipe, custom_mod_struct, md_recipe_setup, params):
    from src.model import (
        V1BMTKNetworkBuilder,
        V1ConnectionMapper,
        V1NeuronMapper,
        V1RegionMapper
    )

    model_recipe = ModelRecipe(
        recipe_setup=md_recipe_setup,
        region_mapper=V1RegionMapper,
        neuron_mapper=V1NeuronMapper,
        connection_mapper=V1ConnectionMapper,
        network_builder=V1BMTKNetworkBuilder,
        mod_structure=custom_mod_struct,
        save_flag=params.save_flag,
    )
    return (model_recipe,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # V1 Network Construction from Recipe

    ## Data Acquistition

    Data acquisition consists of the following two steps:
    1. Data download and
    2. Data transformer operations such as filtering and combining
       that are run after downloaded data.

    ### Run Workflow to Download Data

    After the model description is defined and updated with
    custom user modifications, the download workflow proceeds as follows:
    1. Query and download the data from all the databases of interest.
    2. Apply the filters and transormations.
    3. Save downloaded data to a local database.

    ### Run Post-download Operations

    After data is dowloaded, the data obtained from
    different databases need to processed separately:

    1.  In case of the Allen Cell Type database, the download step can
        be restricted only to obtain the metadata related to cell types.
        After the meta data is downloaded, we need to acquire the models
        of interest (3 LIF Models). We use the GLIF API from allensdk to
        download these 3LIF model with a explained variance threshold.
        Further filter is applied based on the classification by
       *Gouwens et. al. (2019)*.
    3.  For data from Allen Brain Cell Atlas,
        we filter the data specific to only the VISp region.
    5.  For AI Syn Phys. data, we select only the neuron pairs of our interest.


    **The following code is commented as the necessary data is already
    acquired; Uncomment if needed to download again**
    """)
    return


@app.cell
def _():
    # UNCOMMENT THE FOLLOWING TO GET detailed logging
    #import logging
    #logging.basicConfig(level=logging.INFO)
    #import warnings

    #with warnings.catch_warnings():
    #    warnings.simplefilter("ignore", category=RuntimeWarning)
    #    db_source_data = model_recipe.acquire_source_data()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Explore downloaded data

    Output data are stored in json format in the directory
    `data/v1/db_connect_output.json`, which can be examined
    with json library. Here are examples of Region and Neuron
    fractions of the Allen Brain Atlas, and connectivity matrix
    downloaded from AI Syn. Phys. dataset.

    Output data is also stored as duckdb database
    `data/v1/db_connect_output.db`,
    which can be used for more detailed queries.
    """)
    return


@app.cell
def _():
    import duckdb
    db_conn = duckdb.connect("./data/v1/db_connect_output.db")
    return (db_conn,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Regional Neuron Distributions from Brain Atlases
    """)
    return


@app.cell
def _(abm_mouse, db_conn, mo):
    abm_mouse_df = mo.sql(
        f"""
        -- Summary data from the Brain Cell Atlas
        SELECT * FROM abm_mouse LIMIT 100
        """,
        engine=db_conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Cell Types Data from Allen Cell Types Database
    """)
    return


@app.cell
def _(abm_celltypes_ct, db_conn, mo):
    # Explore cell type data
    import quak
    cols = ["cell_reporter_status", "line_name",
            "structure__layer",
           "donor__sex", "donor__age"]
    abm_ct_df = mo.sql(
        f"""
        SELECT {",".join(cols)} FROM abm_celltypes_ct
        """,
        engine=db_conn
    )
    quak.Widget(abm_ct_df)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Connectivity probabilities from AI Syn. Phys.
    """)
    return


@app.cell
def _(ai_synphys, db_conn, mo):
    _df = mo.sql(
        f"""
        -- Summary data from the Synaptic Physiology Database
        SELECT * FROM "ai_synphys" LIMIT 100
        """,
        engine=db_conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Source data to Model mapping

    In this step, the data downloaded is mapped to the locations and
    the connection pairs as mentioned in "Data2Model Map" section above.

    **NOTE: Uncomment the logging configuration to get detailed logging**
    """)
    return


@app.cell
def _(model_recipe):
    #import logging
    #logging.basicConfig(level=logging.INFO)
    #
    msrc = model_recipe.map_source_data()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Apply Custom Modification
    As mentioned in the "Custom Modifications" section above,
    user updates for the model are loaded from the `custom mod` files.

    For V1, the user modification include dimension, additional
    connection properties, and properties of external networks.
    """)
    return


@app.cell
def _(model_recipe, params):
    mstruct = model_recipe.build_net_struct()
    mstruct = model_recipe.apply_mod(params.ncells)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Network Representation after Recipe + Custom Mods

    The intermediate representation after recipe edits/custom mods is given below.
    """)
    return


@app.cell
def _(NetworkStructureView, mo, model_recipe):
    final_net_view = NetworkStructureView(model_recipe.network_struct).build("Final-V1")

    fnet_tree,fnet_panels = final_net_view.view_components()
    fnet_motree = mo.ui.anywidget(fnet_tree)
    #final_net_view.tree
    return fnet_motree, fnet_panels


@app.cell(hide_code=True)
def _(BaseTree, fnet_motree, fnet_panels, mo, tree_view_widths):
    #
    fnet_selected = BaseTree.panel_selector(fnet_motree, fnet_panels)
    mo.hstack(
        [
            fnet_motree,
            fnet_selected.layout if fnet_selected else None
        ],
        widths=tree_view_widths
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Build Network with BMTK

    ### Skeleton Network → Graph of neurons

    The output of *mapping source data* + *applying custom modifications*
    is a skeleton representation of the model.
    In this step this skeletion is used to initialize the nodes and
    edges of a multi-graph of neurons using BMTK.

    ***NOTE:: Building first without saving is useful to first verify any errors***

    ### Save SONATA

    Save SONATA with BMTK

    ***NOTE:: Skipping Save SONTA as it takes a siginificant amount of time.
    For a model of 30K cells, it takes about an hour.
    (Previously built files are made available in "./builds/v1030" folder)***
    """)
    return


@app.cell
def _():
    #
    # Convert skeleton to SONATA build
    #
    # bmtk_net_builder = V1BMTKNetworkBuilder(model_recipe.network_struct)
    # bmtk_net = bmtk_net_builder.build()
    #
    # Save SONATA
    #
    # bmtk_net_builder.save(str(md_recipe_setup.network_dir))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Simulation and Analysis
    ## Prepare neuron model files for NEST

    The format of the glif-model description json files downloaded from the
    cell types database is not compatible with NEST simulator.
    In this step we convert to the appopriate format that is expected from NEST.
    """)
    return


@app.cell
def _():
    # Converting to 
    import src.operations as ops
    import matplotlib.pyplot as plt
    import os

    output_path = "./components/cell_models/"
    input_path = "./components/point_neuron_models/"

    if not os.path.exists(output_path):
        os.mkdir(output_path)
        ops.convert_ctdb_models_to_nest(output_dir=output_path, input_dir=input_path)
    return os, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Simulate the SONATA Network in NEST

    ### SONATA Network Config

    This NEST config file is manually created, and refers to the network files generated by Cerebrum.
    We explore the config file below.
    """)
    return


@app.cell
def _():
    import json
    with open("./builds/v1030/config.json") as ifx:
        cfg_dict = json.load(ifx)
    cfg_dict
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Run Simulation
    """)
    return


@app.cell
def _(os):
    import pandas as pd
    import seaborn as sns
    #
    from src import simulate_cli 
    from src.sonata_df import spikes_df, nodes_df, node_types_df, lgn_df
    #
    import shutil
    sim_output_path = "./builds/v1030/output/"

    if os.path.exists(sim_output_path):
        shutil.rmtree(sim_output_path)

    simulate_cli.main("./builds/v1030/config.json", 16)
    return lgn_df, node_types_df, nodes_df, pd, sns, spikes_df


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Analysis of Simulation outputs
    """)
    return


@app.cell
def _(lgn_df):
    lgndf = lgn_df("./lgn/full3_GScorrected_PScorrected_3.0sec_SF0.04_TF2.0_ori270.0_c100.0_gs0.5_spikes.trial_0.h5")
    lgndf
    return (lgndf,)


@app.cell
def _(lgndf, sns):
    sns.relplot(data=lgndf, x="time", y="gid")
    return


@app.cell
def _(node_types_df, nodes_df, pd, spikes_df):
    sp_df = spikes_df("./builds/v1030/output/spikes.h5")
    nd_df = nodes_df("./builds/v1030/network/v1_nodes.h5")
    ntypes_df = node_types_df("./builds/v1030/network/v1_node_types.csv")

    node_spikes_df = pd.merge(pd.merge(sp_df, nd_df), ntypes_df)
    node_spikes_df
    return (node_spikes_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Spiking Neurons across Layers
    """)
    return


@app.cell
def _(node_spikes_df, sns):
    sns.relplot(data=node_spikes_df, x="timestamp", y="y", col="ei", hue="cell_type", style="layer")
    return


@app.cell
def _(plt):
    from src import plotting_utils as mpu

    pointnet_config = 'builds/v1030/full_path_config.json'
    net = 'full'
    sortby='tuning_angle'
    radius = 400.0
    plt.figure(figsize=(10, 6))


    ax = mpu.plot_raster(pointnet_config, sortby=sortby, **mpu.settings[net])
    ax.set_xlim([0, 2500])
    plt.tight_layout()
    ax
    return mpu, pointnet_config, radius, sortby


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Mean firing rate plots
    """)
    return


@app.cell
def _(mpu, pointnet_config, radius, sns, sortby):
    spk_df, hue_order, color_dict, layer_divisions = mpu.make_figure_elements(pointnet_config, radius, sortby)
    # calculate firing rates
    rates = spk_df[spk_df['timestamps']>500.0].groupby(['Sorted ID'])['timestamps'].count()/2.5
    rates = rates.reset_index(name = 'Mean Rate')
    rates_df = spk_df[['population', 'Sorted ID', 'Cell Type', 'Tuning Angle', 'layer']].drop_duplicates('Sorted ID')
    rates_df = rates_df.merge(rates, how='left', left_on='Sorted ID', right_on = 'Sorted ID')
    sns.boxplot(rates_df, x='layer', y='Mean Rate', hue='Cell Type', order=['VISp2/3', 'VISp4', 'VISp5'])
    return (rates_df,)


@app.cell
def _(rates_df, sns):
    angles_list = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0, 360.0]
    rates_df['Tuning Angle'] = rates_df['Tuning Angle'].round()
    trates_df = rates_df[rates_df['Tuning Angle'].isin(angles_list)]
    sns.lineplot(trates_df[trates_df['Cell Type']=='Exc'], x='Tuning Angle', y='Mean Rate', err_style='bars')
    return (trates_df,)


@app.cell
def _(sns, trates_df):
    sns.lineplot(trates_df[trates_df['Cell Type']!='Exc'], x='Tuning Angle', y='Mean Rate', hue = 'layer', err_style='bars')
    return


if __name__ == "__main__":
    app.run()
