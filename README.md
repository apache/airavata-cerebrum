# Apache Airavata Cerebrum, an Integrated Neuroscience Computational Framework

## Contents

- [Introduction](#introduction)
- [Key Features](#key-features)
- [Installation](#install-airavata-cerebrum)
- [Examples](#example-usage)
- [Contributing](#contributing)

## Introduction

Airavata Cerebrum is an  open-source framework that provides 
tools to simplify building whole brain models via integration
of data collected from cellular-level brain atlases.
Cerebrum modules allow for accelerated 'data to model' workflows that are 
flexible to update, and straight-forward to reproduce.

## Key Features

- **Integration of Brain Atlases**: Transparently connect to publicly available
  cellular-level brain atlases via a single, accessible platform.
- **Model Consruction Workflows**: Workflows to collect/filter/combine data from
  different databases and construct whole brain scale models.
- **Model Editor**: Utilties for simple edits  
- **Open-Source Framework**: Developing a user-friendly, open-source environment
  for neuroscience research.
- **Streamlined Environment**: A lightweight, efficient framework that is 
  interactively accessible via jupyter/marimo notebooks.

## Install Airavata Cerebrum

*__NOTE:: Some of the example notebooks provided at the
[github source repo](https://github.com/apache/airavata-cerebrum/tree/main/examples) 
might require additional dependencies. Please consult the documentation in the 
[examples/README.md](https://github.com/apache/airavata-cerebrum/tree/main/examples/README.md)
for the respective examples or the jupyter notebooks.__*

Airavata Cerebrum requires python v3.10 environment.
It is currently tested only in the Linux operating system.
To install from the source, we recommend creating a `conda` environment using
[miniforge](https://github.com/conda-forge/miniforge) as below:

```sh
conda config --add channels conda-forge
conda create -n cerebrum python=3.10 nodejs
conda activate cerebrum
```

To install Airavata Cerebrum from source into the environment created above,
install from pypi using pip.

```sh
pip install airavata-cerebrum
```

## Example Usage

The `examples` directory in our 
[github repo](https://github.com/apache/airavata-cerebrum/tree/main/examples) 
contains a set of notebooks and scripts that demonstrate the capabilities of 
Cerebrum. Both the notebooks and standalone batch scripts instruct the use of 
Cerebrum in building/simulating large-scale neuroscience models.
Please refer to 
[examples/README.md](https://github.com/apache/airavata-cerebrum/tree/main/examples/README.md)
for additional installation requirements to run the notebooks. 

## Contributing

Issues and PRs are welcome — especially from neuroscience researchers on real models.
See [CONTRIBUTING.md](CONTRIBUTING.md) for software design, source layout, and
dev setup.
Bug reports and enhancement requests go in 
the [issue tracker](https://github.com/apache/airavata-cerebrum/issues).


## License

[Apache 2.0](LICENSE)
