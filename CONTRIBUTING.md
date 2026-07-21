# Contibuting to Cerebrum

Issues and PRs are welcome — especially from neuroscience researchers on real models.
Bug reports and enhancement requests go in 
the [issue tracker](https://github.com/apache/airavata-cerebrum/issues).
This document overviews the software design, source layout, and developement setup.


## Software Design

The design of `Cerebrum` software consists of two layers. The foundation
layer consists of the component modules for data acquisition, data mapping,
SONATA editing and user customization, and the
workflow layer includes the modules to define the `Cerebrum` model recipe,
and running the `Cerebrum` workflow are built on top the foundation layer.

The modules for the foundation layer are in the `base`, `dataset`, `operations`,
`sontata` modules.
The recipe, workflow, skeletal representation classes are in
`workflow`, `recipe`, `model` modules.
The widgets to render the structure in jupyter and marimo notebooks are in
the `view`module.


### Source Tree 

```sh
airavata_cerebrum/
├── __init__.py             # Type definitions
├── base.py                 # Base classes for data base queries, data transformers and writers.  
├── const.py                # Constant definitions used in other modules.
├── recipe.py               # pydantic data structure defintion for recipes
├── register.py             # Global registers of data providers, transformers and data writers.
├── workflow.py             # workflow runners for queries, mappers and transformers.
├── dataset                 # Module for Data Sources/Transforms 
│   ├── __init__.py         # Register for query/transform/writer classes.
│   ├── abc_mouse.py        # Classes to query/filter data from Brain Atlas
│   ├── abm_celltypes.py    # Classes to query/filter data from Cell types database.
│   ├── ai_synphys.py       # Classes to query/filter data from AI syn. phys database.
│   ├── me_features.py
│   └── mouse_brain.py      # Constants for Mouse Brain Data
├── model
│   ├── __init__.py
│   └── structure.py        # pydantic data classes for skeletal representation
├── operations              # Data mainulation/transform operations
│   ├── __init__.py
│   ├── abc_mouse.py        # Classes to transform/write data from Brain Atlas.
│   ├── abm_celltypes.py    # Classes to transform/write data from Cell types data.
│   ├── ai_synphys.py       # Classes to transform/write data from Syn. Phys Data.
│   ├── dict_filter.py      # Classes to transform/write data in dict form
│   ├── json_filter.py      # Classes to transform/write data in json format.
│   ├── me_features.py
│   ├── netops.py
│   └── xform.py            # Abstract transformer clsses
├── sonata                  # Module for SONATA manipulation.
│   └── edge.py             # SONATA editor context manager and functions.
├── util                    # module with utility functions.
│   ├── __init__.py         # Basic utility functions
│   ├── io.py               # I/O for json/yaml
│   └── profile.py          # Profiling functions for memory usage/timings
└── view                    # Module for generating jupyter/marimo views
    ├── __init__.py         # Base classes for views/network.
    ├── motree.py           # Classes/Widgets viewing Recipes/Network in marimo.
    └── tree.py             # Classes/Widgets viewing Recipes/Network in jupyter.
```


## Setting up Development Environment

### Clone the source github repo
`airavata-cerebrum` includes three submodules:
[abc_atlas_access](https://github.com/srirampc/abc_atlas_access),
[aisynphys](https://github.com/srirampc/aisynphys) and
[codetiming](https://github.com/srirampc/codetiming).
Clone the repository along with all submodules as below.
```sh
git clone --recurse-submodules https://github.com/apache/airavata-cerebrum.git
```

In the wheel file, all the dependencies are included with in
the `airavata_cerebrum/ext` namespace.
To get these modules to work in developement environment, create the following
links to the paths in the _ext_ directory:
```sh
cd airavata-cerebrum/airavata_cerebrum
ln -s ../../ext/codetiming/codetiming/
ln -s ../../ext/abc_atlas_access/src/abc_atlas_access/
ln -s ../../ext/aisynphys/aisynphys/
ln -s ../../ext/abc_atlas_access/src/manifest_builder/
```

### Installing Environment For Development

Development environment for Airavata Cerebrum is created as a python3.10+ 
virtual environment in `conda` using the `environment.yml` file.
```sh
conda config --add channels conda-forge
conda env create -n cbmdev -f environment.yml
conda activate cbmdev
```

`environment.yml` includes the version of each of the package to make conda's 
dependency resolution algorithm to run faster. 

### Buliding dist/wheels

We use [poetry](https://python-poetry.org/) a build tool which can be buit 
as follows.
Intall the follwing dependencies for building the dist/wheels:
```sh
pip install build
pip install twine==6.0.1
```

Build and upload to pypi:
```sh
rm -rf dist; python3 -m build
python3 -m twine upload --repository pypi dist/* --verbose
```


## Potential Environment Issues

### Miniforge `conda` Issue when installed with `spack`

If installing conda with miniforge, in some cases the following error appears:
`ModuleNotFoundError: No module named 'conda'`

This happens when the conda script (`$CONDA_EXE`)  has in its first line 
`#!/usr/bin/env python`, which picks up the python from the `cerebrum` environment
which is currently being installed instead of the base environment. To fix this,
replace the `/usr/bin/env python` with the python installed in the base 
environment (generally corresponds of the environment variable `$CONDA_PYTHON_EXE`).
