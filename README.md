# Apache Airavata Cerebrum, an Integrated Neuroscience Computational Framework

## Introduction

Welcome to the Apache Airavata Cerebrum repository for the Integrated Neuroscience Computational Framework. This project aims to revolutionize how we understand and model the human brain by integrating cellular-level brain atlases with advanced computational tools. Our goal is to create a cohesive, open-source framework that allows for the seamless application of existing tools within a streamlined, lightweight environment.

## Features

- **Integration of Brain Atlases**: Merging publicly available cellular-level brain atlases into a single, accessible platform.
- **Comprehensive Modeling Tools**: Incorporating computational tools designed for modeling the entire brain.
- **Open-Source Framework**: Developing a user-friendly, open-source environment for neuroscience research.
- **Streamlined Environment**: Ensuring a lightweight, efficient framework for both beginners and advanced users.

# Try Airavata Cerebrum
Airavata Cerebrum requires python3.10+ environment.
It is currently tested only in Linux operating system.
Cerebrum depends upon NEST and BMTK, which  depends upon MPI. 
Since conda's MPI causes conflicts, we recommend 
that MPI is installed from the OS. 
In case of Ubuntu, this can be accomplished by
```
sudo apt install openmpi-bin  libopenmpi-dev
```

Further, we recommend create a virtual environment using conda as below:
```
conda create -n cerebrum python=3.10 nest-simulator
conda activate cerebrum
```

The following pip command will download and install Airavata Cerebrum into 
the environment created above. 
```
pip3 install git+https://github.com/apache/airavata-cerebrum.git
```

Check the `resources/notebooks/V1L4-Notebook.ipynb` folder for examples of usage.

See [INSTALL.md](INSTALL.md) for details about how to install for a 
development environment and other issues.
