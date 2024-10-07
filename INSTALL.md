## OS Depenencies

Airavata Cerebrum is currently tested only in Linux operating system.
NEST and BMTK depends upon MPI. Since conda's MPI causes conflicts, we recommend 
that MPI is installed from the OS packages.
In case of Ubuntu, this can be accomplished by
```
sudo apt install openmpi-bin  libopenmpi-dev
```

## Install with pip

Airavata Cerebrum requires python3.10+ environment. 
We recommend create a virtual environment using conda as below:
```
conda create -n cerebrum python=3.10 nest-simulator
conda activate cerebrum
```

Following command will download Airavata Cerebrum into your environment. 
```
pip3 install git+https://github.com/apache/airavata-cerebrum.git
```

## Installing Environment For Code Development

Development environment Airavata Cerebrum requires python3.10+ environment. 
We can create a virtual environment in conda using the `environment.yml` file.
```
conda create env -n cerebrum -f environment.yml
conda activate cerebrum
```

`environment.yml` includes the version of each of the package to make conda's 
dependency resolution algorithm to run faster. In case, this causes issues
during conda install, try using `env_full.yml`, which doesn't include 
the versions 

## Potential Issues

### MPI Depenency Issue

- NEST and BMTK depends upon MPI -- specifically the python mpi4py package.
- Latest versionof mpi4py package is only available in the PyPI and hence need to be
  installed via pip command.
- In some cases, the mpi package from conda causes failures during installation
  of mpi4py. This is due to the compilation errors arising from building the 
  C/C++ modules of mpi4py (compiled using mpicc).
- To avoid this, it is recommend to install the MPI libraries on the system first
  before creating the conda environment and installing the python libraries.
