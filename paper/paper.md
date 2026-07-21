---
title: "Airavata Cerebrum : Flexible tool for Constructing Computational Neuroscience Models from Large Public Databases and Brain Atlases"
tags:
  - Python
  - neuroscience
  - whole brain model 
  - sonata
authors:
  - name: Sriram P. Chockalingam
    orcid: 0000-0003-1358-7691
    affiliation: 1
affiliations:
  - name: Georgia Insitute of Technology, Atlanta, GA, USA
    index: 1
date: 8 June 2026
bibliography: paper.bib
---

# Summary

`Airavata Cerebrum` is a flexible and extendable tool in python to construct
large-scale data-driven computational models of hierarchically-organized
network of neurons.
Specifically, `Airavata Cerebrum` enables  
1. acquisition of datasets by querying different neuroscience databases and brain atlases, 
2. application of user-customizable transformations on the acquired datasets, and
3. construction of a computational model of a whole brain.  
`Airavata Cerebrum` saves the computational neuroscience models  
using the standard _SONATA_ format. Simulation software such as _NEST_ and
_NEURON_ can run the output models in _SONTA_ format without any modification.   
Further, `Airavata Cerebrum` includes utilities that enables the application of
minor edits to the model, without completely re-building from scratch.


# Statement of need

Public databases such as the whole-brain atlases[@hawrylycz2023guide, @yao2023high]
contain large compendiums of datasets reprsenting different modalities, and
therefore provide extensive and detailed maps of the brain. However,  
using such brain atlases for the construction of computational models remains a
challenge. 

The key challenges in building a data-driven construction of large-scale 
computational neuroscience model are as follows:
- Diversity in the data types acquired from different databases to compile different 
  components of the model.
- Different databases require different access methods. Some databases provide 
  a simple REST-like API access, where as some other databases require downloading
  a set of large files to the local machines.
- Integrating data from all the datasets of interest in a specific combination
  that encodes the neuro-system of the user's interest and their own custom data.
- Visualize the hierarchy of the model structure and its various sub-structures.
- Ability to update, modify, reuse and remix the models in future research. 

To seamlessly and effectively integrate data from different data sources,
there is a need for an easy-to-use tool to tackle the above challenges in the 
different phases of the lifecycle of a large-scale model of neurons:
construction, modification, reuse and revise. 


# State of the field

As far as we know, `Cerebrum` is the only software that provides interfaces 
that allow collecting data from different databases, 
mapping data to model components, and provide an end-to-end tool 
to construct brain-scale network of neurons.
Other software packages such as NetPyNE [@dura2019netpyne], and
PyNN [@davison2009pynn] and BMTK [@dai2020brain] provide tools to describe 
any large network of neurons at an abstract level and run with different
simulators, but these tools doesn't provide `Cerebrum`'s
emphasis on data-driven modeling and the ease of 
describing connections to different databases and collecting from the databases.


# Software Design

The design of `Cerebrum` software consists of two layers. The foundation
layer consists of the component modules for data acquisition, data mapping,
SONATA [@dai2020sonata] editing and user customization, and the
workflow layer includes the modules to define the `Cerebrum` model recipe,
and running the `Cerebrum` workflow are built on top the foundation layer.

## Cerebrum Components
`Cerebrum`'s foundation components are classified in to four categories
1. Data Providers,
2. Data2Model mappers,  and 
3. SONATA editors,
4. Custom Network structures.

### Data Providers
Classes in data providers module download the necessary data from the
atlases and the databases of interest. In `Cerebrum`, the
_Data Provider_ classes provide the following functionalities:
- Query different databases, with the options to restrict the search specific 
to context of the model under construction.
- Filter the obtained search results based on the model requirements including the 
organism/location/layer of interest and expected quality of the available
data specimens.
- Re-organize data so as to enable combining multiple datasets from the same 
or different database.

Currently, `Cerebrum` provides classes to query/filter:
1. transcriptomic data from the whole-brain atlas by `@yao2023high`,
2. connection probabilities from the database by `@campagnola2022local`,
3. neuron models from Allen Cell Types Database.
Users can extended thesee functionalities via custom classes 
to acquire data from their own database of interest.

### Data2Model mappers
Using the acquired data, `Data2Model` mapper classes furnish the details
of the model such as the neuron composition, physiology, neuron types,
synapse connectivity probabilities, and the connectivity models.

### SONTA editors
_SONATA_ network format includes (a) the list of nodes and edges saved as 
HDF5 files and (b) the node types and edge types are stored as CSV files.
`Cerebrum` provides context manager to remove/add/replace edges and 
nodes of a given type.

### Custom Network
Custom Network module defines data modelling classes that enable the user to
update the underlying structure either to fill in any missing details of the
model or to modify the data-driven structure via an optional user-defined
custom modifications. This may include (i) details of the model such as
dimensions and size of the model that are based on the user knowledge;
(ii) aspects of the model that can not be identified using available datasets;
and (iii) model parameters that are derived from the user's own experimental data.


## Cerebrum Workflow
`Cerebrum` expects that the workflow instructions are encoded as 
the _model recipe_, realized as a set of recipe files.

### Cerebrum Model Recipe

Input to the `Cerebrum` workflow is a set of configuration files,
called the _Model Recipe_ files, the defines the steps of model construction
workflow. _Model Recipe_ includes the following four sections.

- **Data Sources :** Details about the source database, query methods,
  and query parameters.
- **Filter and Transformers :** Listing of all the data filters and
  data selection mappers that run on the queried data to transform the data
  that is amenable to be used in the construction of the model.
- **Data Mappers :** Description of Mapper classes and methods that map 
  data to model components.
- **User Modifications :** User Inputs that modify the data-derived model.
- **Network Converters :** Classes and Methods to convert the description of 
  in the _SONATA_ format.

### Workflow Runners
The default workflow runner classes execute in the standard order of 
data acquisition, data mapping, applying user updates and building the 
model graph.

# Research Impact Statement

As as significant demonstration of `Cerebrum`, we build a 
a 30,000-neuron version of `@billeh2020systematic`'s  model of
mouse's the primary visual cortex (V1).
The `Cerebrum` workflow for V1:
- Acquires data from Single-cell Brain Atlas [@yao2023high] and 
  identies the regional and layer-wise  distributions of the different cell types.
- Query the connection probabilities from the synaptic physiology 
  database [@campagnola2022local].
- Acquires Neuron models from cell types database.
- Filter the data to only that of the V1 region,
- Map the cell types data to the neuron types, and probabilities to the edge types,
- Use custom class the borrow the details from `@billeh2020systematic`

The complete notebook is available in the examples folder of the source 
repository.


# AI usage disclosure

AI tools were used in the development of the SONATA editor module of the
cerebrum software. No AI tools were used in the writing
of this manuscript, or the preparation of supporting materials.

# Acknowledgements

TODO:ack

# References
