# Examples of `airavata-cerebrum` applications

This folder contains jupyter notebooks, marimo notebooks and 
other standalone scripts demonstating the use of
[airavata-cerebrum](https://github.com/apache/airavata-cerebrum) 
software in building the neuroscience models. 

## Contents

1. [Simple Model](#simple-model)
2. [Sonata Editor](#sonata-edge-editor)
3. [V1 Model](#v1-model)
## Simple Model

[Simple Notebook](simple/Simple.ipynb) shows a workflow to build a 
simple one layer model. Cerebrum is used query the Mouse Brain Atlas
to identify the proportions of excitatory and inhibitory neurons.
No additional dependencies are necessary to run this notebook.


## SONATA Edge Editor

These notebooks listed below show a demo of edititng edges in a SONATA file:
A specific case where all the edges of a given edge `type id` are
replaced with a random subset of edges. 
See [editor/README.md](editor/README.md) for a description of this 
functionality.
No additional dependencies are necessary to run this notebook.

| Source        | Notebook                                   |
| ------------- | ------------------------------------------ |
| jupyter       | [Notebook](editor/SonataEditorDemo.ipynb)  |
| marimo        | [Notebook](editor/marimo_sonata_editor.py) |



## V1 Model

### Install cerebrum + additional dependencies

V1/V1 L4 notebooks listed below depend upon 
[airavata-cerebrum](https://github.com/apache/airavata-cerebrum), 
[NEST](https://www.nest-simulator.org/) ,
[BMTK](https://alleninstitute.github.io/bmtk/) and other dependencies.
BMTK and NEST inturn depend upon [mpi4py](https://mpi4py.readthedocs.io/),
the python interface to MPI. 
All these dependencies can be installed via conda using the given
`environment.yml` (in this directory) as follows.
To create a new `conda` environment with all the required dependencies,
run the following commands.

```sh
conda env create -n arv_cbm -f environment.yml
conda activate arv_cbm
```
To update the existing environment `cerebrum`, run the following commands.
```sh
conda activate cerebrum
conda env update --file environment.yml  --prune
```

#### MPI Depenency Issues during installation

- NEST and BMTK depends upon MPI -- specifically the python mpi4py package.
- Latest version of mpi4py package is only available in the PyPI and hence need to be
  installed via pip command.
- In some cases, the mpi package from conda causes failures during installation
  of mpi4py. This is due to the compilation errors arising from building the 
  C/C++ modules of mpi4py (compiled using mpicc).
- To avoid this, it is recommend to install the MPI libraries on the system first
  before creating the conda environment and installing the python libraries.
  MPI can be installed using via OS package managers (`apt`, `snap`, etc.) (or) 
  external package managers such as `spack`. In case of Ubuntu, this can be
  accomplished by
  ```sh
  sudo apt install openmpi-bin  libopenmpi-dev
  ```

### Notebooks/Scripts

The following notebooks demonstrate the use of airavata-cerebrum to gather 
data from Brain Atlases and other databases,  build the model and 
simulate using NEST simulator. See the [v1/README.md](v1/README.md) 
for a detail discussion on each phase of model construction.

#### jupyter Notebooks

The notebooks can be viewed and run with jupyter under the above 
environment.

| Model                             | Notebook                                         |
| --------------------------------- | ------------------------------------------------ |
| Complete V1 model                 | [V1 IPython Notebook](v1/V1-Notebook.ipynb)      |
| V1 model restricted to only L4    | [V1 L4 IPython Notebook](v1/V1L4-Notebook.ipynb) |

#### marimo Notebooks

[marimo](https://marimo.io/) is a reactive notebook that is reusable as a
module, executable as a script and sharable as an app.
The following marimo notebooks are the counterparts to the jupyter notebooks.
By default, the notebooks are not run automatically. 

| Model                          | Notebook                                     |
| ------------------------------ | -------------------------------------------- |
| Complete V1 model              | [V1 marimo Notebook](v1/marimo_v1.py)        |
| V1 model resricted to only L4  | [V1 L4 marimo Notebook](v1/marimo_v1l4.py)   |
| Data views w.r.t V1            | [V1 db marimo Notebook](v1/marimo_v1l4db.py) |


#### Command-line scripts

Standalone python scripts can be run on command line to build/simulate V1 models.
They can used for cases where they can be only run in non-interactive mode. 


| Model                              | Scripts                                       |
| ---------------------------------- | --------------------------------------------- |
| Build/Simulate Cerebrum V1 model   | [V1 script](v1/src/cli.py)                    |
| Simulate Cerebrum V1 model w. BMTK | [V1 BMTK script](v1/src/simulate_cli.py)      |
| Simulate Cerebrum V1 model w. NEST | [V1 NEST script](v1/src/nest_simulate_cli.py) |


