# Roadmap 

## 2024

**Add functionality for adding model construction process to Sonata model files**
Sonata files do not have information / workflow on how the model is constructed, especially for complex models that depend on Atlas dataset. This makes the changes on the large-scale models difficult.

**Solution:**
Develop a package (will be part of Cerebrum) that can 
1. Store the information on model construction
2. Allow for variations of model construction 

If possible, to develop an intelligent system which will decide if you need to just update parameters or reconstruct the model based on the requested change to the model.

**Demonstration**
Single layer of visual cortex
In the whole V1 network model
