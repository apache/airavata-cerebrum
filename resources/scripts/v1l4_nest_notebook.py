#!/usr/bin/env python
# coding: utf-8

import os
import argparse
import shutil

import logging
import airavata_cerebrum.util.desc_config as cbm_dcfg
import airavata_cerebrum.view.tree as cbm_tree
import airavata_cerebrum.model.desc as cbm_desc
import mousev1.model as mousev1

import json
import ast
import numpy as np
import pandas as pd
import IPython.display

import mousev1.operations as mousev1ops
import nest
import matplotlib.pyplot as plt


# Creating the base directory
v1l4_base_dir = "./v1l4"
sub_dirs = ["bkg", "network", "description", "components"]

# Create base directory if it doesn't exist
if not os.path.exists(v1l4_base_dir):
    os.makedirs(v1l4_base_dir)

# Create each subdirectory within the base directory
for sub_dir in sub_dirs:
    dir_path = os.path.join(v1l4_base_dir, sub_dir)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

print(f"Directories {v1l4_base_dir} and {sub_dirs} have been created.")

# File paths in the current directory
config_nest_file = 'config_nest.json'
custom_mod_file = 'custom_mod.json'
config_file = 'config.json'

# Check that files exist
if not all(os.path.exists(f) for f in [config_nest_file, custom_mod_file, config_file]):
    raise FileNotFoundError("One or more required files are missing in the current directory.")

# Paths to move the files to
description_dir = os.path.join(v1l4_base_dir, "description")

# Move config_file and custom_mod_file to ./v1l4/description
shutil.move(config_file, os.path.join(description_dir, config_file))
shutil.move(custom_mod_file, os.path.join(description_dir, custom_mod_file))

# Move config_nest_file to ./v1l4
shutil.move(config_nest_file, os.path.join(v1l4_base_dir, config_nest_file))

print(f"Moved {config_file} to {description_dir}")
print(f"Moved {custom_mod_file} to {description_dir}")
print(f"Moved {config_nest_file} to {v1l4_base_dir}")

# Update the file paths to the new locations
config_nest_file = os.path.join(v1l4_base_dir, config_nest_file)
custom_mod_file = os.path.join(description_dir, custom_mod_file)
config_file = os.path.join(description_dir, config_file)


# Paths for the source and destination of the symlinks
source_component_dir = "/home/scigap/projects/data/V1L4/components"
target_component_dir = os.path.join(v1l4_base_dir, "components")

source_source_data_file = "/home/scigap/projects/data/V1L4/source_data_output.json"
target_source_data_file = os.path.join(description_dir, "source_data_output.json")

source_bkg_file = "/home/scigap/projects/data/V1L4/bkg_spikes_250Hz_3s.h5"
target_bkg_dir = os.path.join(v1l4_base_dir, "bkg")

# Create symlinks
try:
    os.symlink(source_component_dir, target_component_dir)
    print(f"Symlink created: {target_component_dir} -> {source_component_dir}")
except FileExistsError:
    print(f"Symlink already exists: {target_component_dir}")

try:
    os.symlink(source_source_data_file, target_source_data_file)
    print(f"Symlink created: {target_source_data_file} -> {source_source_data_file}")
except FileExistsError:
    print(f"Symlink already exists: {target_source_data_file}")

try:
    os.symlink(source_bkg_file, os.path.join(target_bkg_dir, "bkg_spikes_250Hz_3s.h5"))
    print(f"Symlink created: {os.path.join(target_bkg_dir, 'bkg_spikes_250Hz_3s.h5')} -> {source_bkg_file}")
except FileExistsError:
    print(f"Symlink already exists: {os.path.join(target_bkg_dir, 'bkg_spikes_250Hz_3s.h5')}")


md_desc_config = cbm_dcfg.init_model_desc_config(
    name="v1l4",
    base_dir="./",
    config_files={"config": [config_file], "templates": ["config_template.json"] },
    config_dir="./v1l4/description/",
)

model_dex = cbm_desc.ModelDescription(
    config=md_desc_config.config,
    region_mapper=mousev1.V1RegionMapper,                                                                                                                                                                                                         
    neuron_mapper=mousev1.V1NeuronMapper,                                                                                                                                                                                                         
    connection_mapper=mousev1.V1ConnectionMapper,                                                                                                                                                                                                     
    network_builder=mousev1.V1BMTKNetworkBuilder,                                                                                                                                                                                                   
    custom_mod=custom_mod_file,                                                                                                                                                                                                               
    save_flag=True,
)

with open(custom_mod_file) as ifx:
    custom_mod_dict = json.load(ifx)
IPython.display.JSON(custom_mod_dict)

# mdb_data = model_dex.download_db_data()

with open("./v1l4/description/db_connect_output.json") as dbf:
    db_out_data = json.load(dbf)
ai_syn_data = db_out_data['airavata_cerebrum.dataset.ai_synphys'][0]
row_keys = set([ast.literal_eval(xk)[0] for xk in ai_syn_data.keys()])
col_keys = set([ast.literal_eval(xk)[1] for xk in ai_syn_data.keys()])
col_names = row_names = list(row_keys)
connect_matrix = np.zeros((len(row_names), len(col_names)))
for i, cx in enumerate(col_names):
    for j,rx in enumerate(row_names):
        connect_matrix[i, j] = ai_syn_data[repr((cx, rx))]
pd.DataFrame(connect_matrix, index=row_names, columns=col_names)

logging.basicConfig(level=logging.INFO)
# mdb_data = model_dex.db_post_ops()

msrc = model_dex.map_source_data()

with open(custom_mod_file) as ifx:
    custom_mod_dict = json.load(ifx)
IPython.display.JSON(custom_mod_dict)

msrc = model_dex.build_net_struct()
msrc = model_dex.apply_custom_mod()

bmtk_net_builder = mousev1.V1BMTKNetworkBuilder(model_dex.network_struct)
bmtk_net = bmtk_net_builder.build()

bmtk_net_builder.net.save(str(model_dex.config.network_dir))
bmtk_net_builder.bkg_net.save(str(model_dex.config.network_dir))

# Converting to 
mousev1ops.convert_ctdb_models_to_nest("./v1l4/components/point_neuron_models/", "./v1l4/components/cell_models/")

# Instantiate SonataNetwork
sonata_net = nest.SonataNetwork(config_nest_file)

# Create and connect nodes
node_collections = sonata_net.BuildNetwork()
print("Node Collections", node_collections.keys())

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

dmm = multi_meter.get()
Vms = dmm["events"]["V_m"]
ts = dmm["events"]["times"]
plt.figure(1)
plt.plot(ts, Vms)

spike_data = spike_rec.events
spike_senders = spike_data["senders"]
ts = spike_data["times"]
plt.figure(2)
plt.plot(ts, spike_senders, ".")
plt.savefig('nest_combined_plots.png')
plt.close()

