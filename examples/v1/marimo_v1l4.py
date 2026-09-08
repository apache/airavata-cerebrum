import marimo

__generated_with = "0.23.8"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _(mo):
    mo.md(rf"""
    # V1 L4 Model using Apache Cerebrum

    This notebook walks through the  Cerebrum workflow to construct
    a simple *V1* model that restricted to only the layer *L4*.
    The notebook 
    - overviews the data sources configuration,
    - explore the downloaded data,
    - build the model from code,
    - run the simulation, and finally 
    - visualize the simulation outputs.  

    ### Cerebrum Workflow Structure

    Cerebrum follows the following workflow when building a computational brain model
    from data acquired from large databases 

    {mo.image("img/Workflow.png", width=500)}

    The workflow steps to construct a model in Cerebrum are as follows (as shown in the figure above): 

    1. Query and download the requisite data from public databases.
       In case of V1 L4, we acquire data from the following databases:
         - Allen Model Database,
         - Allen Brain Atlas
         - Synaptic Physiology datasets. 
    3. Map the acquired data to the relevant regions of the model to be built. 
    4. Fill-in any missing details via an optional user-defined **custom mod** definitions. 
    5. Realize the final network of neurons in the SONATA format.


    ### Model Recipe

    Model Recipe (files in sub-folder `recipes/v1`) defines key components for constructing a Network of neurons with Cerebrum. 

    - **Data Providers:** Links to source database and query parameters
    - **Filter and Transformers:** Data processing workflow such as filtering via selection criteria on the queried data.
    - **Data2Model Mappers:** Mapper methods that map data to model components.
    - **User Modifications:** Descriptions of user additions/removals to the purely data-driven model

    The following figure shows the overall structure of a Model recipe definition.

    {mo.image("img/Recipe.png", width=500)}

    ## Create a conda Environment

    The Notebook is expected to be run in a `conda` environment with `cerebrum` and other dependcies installed.
    See the [README.md](README.md) file for the instructions to create the environment.
    """)
    return


@app.cell
def _():
    import marimo as mo
    ##

    from airavata_cerebrum.recipe import RecipeSetup, ModelRecipe
    from airavata_cerebrum.model.structure import Network
    from airavata_cerebrum.view.motree import BaseTree, DataSourceRecipeView, Data2ModelRecipeView, NetworkStructureView
    #
    from src import model as v1model
    from src import operations as v1ops
    from src import lfour_params as v1params
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
        SonataNetwork,
        mo,
        nest,
        v1params,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # V1 L4 Model Recipe

    The Cerebrum V1 L4 model recipe includes the following three sections.
    For V1, the model recipe is defined by a collection of human-readable
    json files under the recipe directory `recipes/v1`.

    1. **source_data**
        - Describes how the source databases are connected
        - Defines what operations applied to the data such as filters etc
        - For V1 L4, the `recipes/v1l4/source_data.json` file contains
          the **source_data** section.
    2. **data2model_map**
        - Describes mapping between source data and different
          regions/segments of the model.
        - For V1 L4, `recipes/v1l4/recipe.json` contains the
          **data2model_map** section.
    3. **custom mod**
        - Describes the user modifications applied after a model skeleton
          build from the data and mapping ((1) and (2) above).
        - For V1 L4, we have eight different custom mod files,
          `recipes/v1l4/custom_mod.json` contains the user
           **cust mod**s for L4 layer and the BKG and LGN layers.


    ***NOTE: The following code loads all the above recipe files an initializes
    a python `ModelSetup` object that performs basic input validation,
    and captures all the parameters. Custom modifications are loaded separately
    as `custom_mod_struct`, a `cerebrum.structure.Network` object.***
    """)
    return


@app.cell
def _(Network, v1params):
    #
    # The following code initializes the parameters of the model
    params = v1params.RecipeParams()
    params.ncells = 4000
    #
    # After setting the model parameters, we create a ModelSetup object
    # that builds a framework with some simple valiations
    md_recipe_setup = params.recipe_setup()

    #
    # Custom mods are built as a separate object, which will be 
    # combined later after a skeleton is built.
    custom_mod_struct = Network.from_file_list(params.custom_mod) 

    #
    tree_view_widths = [0.4, 0.6]
    return custom_mod_struct, md_recipe_setup, params, tree_view_widths


@app.cell
def _():
    import IPython.display
    import json
    with open("./recipes/v1l4/recipe.json") as ifx:
        config_dict = json.load(ifx)
    IPython.display.JSON(config_dict)
    return


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

    ***NOTE: Running code below within the notebook will display the tree structure of the recipe's source_data section***
    """)
    return


@app.cell
def _(md_recipe_setup):
    md_recipe_setup.get_section('source_data')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(rf"""
    ### Visualize Source Data

    Cerebrum also provides a Jupyter Notebook Widgets that
    aids the visualization of the source data configration.
    The `DataSourceRecipeView` renders the data source 
    information and query parameters in a user friendly output
    as compared to the strict names in json file. 

    {mo.image("./img/L4SourceData.png", width=600)}


    **NOTE: Running the code below with show an interactive
    explorer-like tree structure as shown in the image above**
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

    `data2model_map` section of the recipe includes two subsections:

    1. *Locations:*
        - Locations are hiearchially defined and each sub-location
          declares the links to the acquired data.
        - For V1 L4, (i) acquired cell types information from Cell types
          database maps to the neuron models, and
          (ii) the summary information from MERFISH single-cell atlas
          map to the distribution of neuron types.
        - For V1 L4, we map eight different neuron types to the specific
          models and the region fractions.
    2. *Connections:*
        - Connections are defined as a set of pairs to neurons,
          with pair defining the data links.
        - AI synaptic physiology data is mapped to the connection
          probabilities between the pairs of neuron classes.
        - For V1 L4, we map each of the different neuron pairs to the
          AI Syn. Phys. Data outputs


    ***NOTE: Running code below within the notebook will display
    the json hierachial-structure of the recipe's data2model section***
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

    {
    mo.image("img/L4SrcLocations.png", width=200)
    }
    {
    mo.image("img/L4SrcConnections.png", width=200)
    }


    ***NOTE: Running the Recipe View code below will display
    the Tree widget (as shown in the above snapshot),
    when run inside the  notebook***
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
    mo.md(f"""
    ## Custom Modifications


    Through the custom modification json files,users can
    provide additional details required for network
    construction. They can include information that are either
    (a) not available in the linked databases or
    (b) not applicable for the model being built and over-ride it.

    For the Mouse V1 L4, custom modifications include:

    1. Dimensions of each region in the model.
    2. Connection Parameters not available within the AI Syn. Phys. database.
    3. Details of the networks that are external to V1 : LGN and the background networks. 


    {mo.image("img/L4CustomMod.png", width=600)}


    ***NOTE: Running code below within the jupyter notebook will display the tree structure of the data2model section from the json files***
    """)
    return


@app.cell
def _():
    # Uncomment 
    #ustom_mod_struct.model_dump()
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
    return V1BMTKNetworkBuilder, model_recipe


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # V1 L4 Network Construction from Recipe

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

    We accomplish the above two steps by running `recipe.acquire_source_data()` function as below.
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

    Output data are stored in the description directory in
    json format in `data/v1l4/db_connect_output.json`, which
    can be examine with json library. Here are examples of
    Region and Neuron fractions of the Allen Brain Atlas, and
    connectivity matrix downloaded from AI Syn. Phys. dataset.

    Output data is also stored as **duckdb** database
    `data/v1l4/db_connect_output.db`, which can be used for
    more detailed queries.


    ### Loading the database as a connection object

    Duckdb database can be connected as a data connection in the notebook. After running the connection below, expand the `Explore variables and data sources` button on the sidebar to see a tree view of the database.
    """)
    return


@app.cell
def _():
    import duckdb
    db_conn = duckdb.connect("./data/v1l4/db_connect_output.db")
    return (db_conn,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Regional Neuron Distributions from Brain Atlases
    """)
    return


@app.cell(hide_code=True)
def _(abm_mouse, db_conn, mo):
    _df = mo.sql(
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
    ### Connectivity probability from AI Syn. Phys.
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

    **NOTE:: Uncomment the logging configuration to get detailed logging**
    """)
    return


@app.cell
def _(model_recipe):
    #import logging
    #logging.basicConfig(level=logging.INFO)
    #
    #
    msrc = model_recipe.map_source_data()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Apply User Modification

    As mentioned in the "Custom Modifications" section above,
    user updates for the model are loaded from
    `./recipes/v1l4/custom_mod.json`.

    For V1 L4, the user modification include the dimensions,
    connection properties, and details about the external netowrks.
    """)
    return


@app.cell
def _(model_recipe, params):
    mnet = model_recipe.build_net_struct()
    mnet = model_recipe.apply_mod(params.ncells)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Network Skeleton Representation after Recipe + Custom Mods

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


@app.cell
def _(BaseTree, fnet_motree, fnet_panels, mo, tree_view_widths):
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

    In this step this configuation is used to initialize the nodes and edges based on the data downloaded and custom modifications applied.

    ***NOTE:: The code below skips saving the file as saving consumes significant amount of time. Building first is useful to first verify any errors***
    """)
    return


@app.cell
def _(V1BMTKNetworkBuilder, model_recipe):
    bmtk_net_builder = V1BMTKNetworkBuilder(model_recipe.network_struct)
    bmtk_net = bmtk_net_builder.build()
    return (bmtk_net_builder,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Save SONATA

    Save SONATA with BMTK

    ***NOTE:: Skipping Save SONTA as it takes a siginificant amount of time. (Previously built files are made available in "./builds/v1l4" folder)***
    """)
    return


@app.cell
def _(bmtk_net_builder, mdr_setup):
    save_bmtk = False
    if save_bmtk:
        bmtk_net_builder.net.save(str(mdr_setup.network_dir))
        bmtk_net_builder.bkg_net.save(str(mdr_setup.network_dir))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Simulation Run
    ## Running the SONATA Network in NEST

    1. Convert downloaded models to NEST confirmed models
    2. Load SONATA network in NEST
    3. Run Simulation
    """)
    return


@app.cell
def _(SonataNetwork):
    config_file = "./builds/v1l4//config_nest.json"
    # Instantiate SonataNetwork
    sonata_net = SonataNetwork(config_file)

    # Create and connect nodes
    node_collections = sonata_net.BuildNetwork()
    print("Node Collections", node_collections.keys())
    return node_collections, sonata_net


@app.cell
def _(nest, node_collections, sonata_net):
    # Connect spike recorder to a population
    spike_rec = nest.Create("spike_recorder")
    nest.Connect(node_collections["v1l4"], spike_rec)

    # Attach Multimeter
    multi_meter = nest.Create(
        "multimeter",
        params={
            # "interval": 0.05,
            "record_from": ["V_m", "I", "I_syn", "threshold", "threshold_spike", "threshold_voltage", "ASCurrents_sum"],
        },
    )
    nest.Connect(multi_meter, node_collections["v1l4"])

    # Simulate the network
    sonata_net.Simulate()
    return multi_meter, spike_rec


@app.cell
def _(multi_meter):
    import matplotlib.pyplot as plt
    #
    dmm = multi_meter.get()
    Vms = dmm["events"]["V_m"]
    ts = dmm["events"]["times"]
    #
    plt.figure(1)
    plt.plot(ts, Vms)
    return (plt,)


@app.cell
def _(plt, spike_rec):
    spike_data = spike_rec.events
    spike_senders = spike_data["senders"]
    ts2 = spike_data["times"]
    plt.figure(2)
    plt.plot(ts2, spike_senders, ".")
    plt.show()
    return


if __name__ == "__main__":
    app.run()
