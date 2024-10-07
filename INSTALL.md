
## Quick Install with pip

Airavata Cerebrum requires python3.10+ environment. 
It is currently tested only in Linux operating system.
We recommend create a virtual environment using conda as below:
```
conda create -n cerebrum python=3.10 nest-simulator
conda activate cerebrum
```

Following command will download Airavata Cerebrum into your environment. 
```
pip3 install git+https://github.com/apache/airavata-cerebrum.git
```

## Environment For Development

The development environment Airavata Cerebrum requires python3.10+ environment. 
NEST and BMTK depends upon MPI. Since conda's MPI causes conflicts, we recommend 
that MPI is installed from the OS. In case of Ubuntu, this can be accomplished by
```
sudo apt install openmpi-bin  libopenmpi-dev
```

Now we can create a virtual environment in conda
```
conda create env -n cerebrum -f environment.yml
conda activate cerebrum
```

`environment.yml` includes the version of each of the package to make conda's 
dependency resolution algorithm to run faster. In case, this causes issues
during conda install, try using `env_full.yml`, which doesn't include 
the versions 

## Potential Issues

### MPI Depenency Issues ::

- NEST and BMTK depends upon MPI -- specifically the python mpi4py package.
- Latest versionof mpi4py package is only available in the PyPI and hence need to be
  installed 
- In some cases, the mpi package from conda is installed, which causes trouble in
  when installing mpi4py because mpi4py has a C/C++ components that will be 
  compiled by mpicc
- To avoid this, install the mpi libraries on the system first before installing the
  libraries
