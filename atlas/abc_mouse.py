import requests
import json
import os
import pathlib
import subprocess
import time
import pandas as pd
import numpy as np
import anndata
import matplotlib.pyplot as plt


ABC_BASE = "/storage/home/hhive1/schockalingam6/data2/airavata-cerebrum/brain_atlases/abc_mouse"
ABC_VERSION = "20231215"
MANIFEST_URL = "https://allen-brain-cell-atlas.s3-us-west-2.amazonaws.com/releases/{}/manifest.json"
PARCEL_META_DATA = "cell_metadata_with_parcellation_annotation.csv"
CCF_COLS = [
    "class",
    "subclass",
    "supertype",
    "cell_label",
    "parcellation_division",
    "parcellation_structure",
    "parcellation_substructure",
    "x_ccf",
    "y_ccf",
    "z_ccf",
]
CCF_FIELDS = [
    "subclass",
    "parcellation_division",
    "parcellation_structure",
    "parcellation_substructure",
    "x_ccf",
    "y_ccf",
    "z_ccf",
    "x",
    "y",
    "z",
]
CCF_COORDS = [
    "x_ccf",
    "y_ccf",
    "z_ccf",
    "x",
    "y",
    "z",
]


def download_merfish_manifest(manifest_url=MANIFEST_URL, version=ABC_VERSION):
    """
    Downloads the Manifiest JSON data from ABC AWS Store
    """
    url = manifest_url.format(version)
    manifest = json.loads(requests.get(url).text)
    return manifest


def merfish_files_meta():
    """
    Downloads the Manifiest JSON data from ABC AWS Store and retrieve 
    MERFISH-C57BL6J-638850 meta data JSON object.
    """
    manifest = download_merfish_manifest()
    merf_meta = manifest["file_listing"]["MERFISH-C57BL6J-638850"]["metadata"]
    return manifest, merf_meta


def download_file(manifest, file_dict, download_base=ABC_BASE):
    """
    Given a file entry in manifest, download the file to the relative path
    constructed from the download_base.

    A simple file entry in manifest is as follows:
    {
     'version': '20230630',
     'relative_path': 'expression_matrices/WMB-10Xv3/20230630',
     'url': 'https://allen-brain-cell-atlas.s3.us-west-2.amazonaws.com/expression_matrices/WMB-10Xv3/20230630/',
     'view_link': 'https://allen-brain-cell-atlas.s3.us-west-2.amazonaws.com/index.html#expression_matrices/WMB-10Xv3/20230630/',
     'total_size': 189424020276
    }
    """
    print(file_dict["relative_path"], file_dict["size"])
    local_path = os.path.join(download_base, file_dict["relative_path"])
    local_path = pathlib.Path(local_path)
    remote_path = manifest["resource_uri"] + file_dict["relative_path"]
    # Download command
    command = "aws s3 cp --no-sign-request %s %s" % (remote_path, local_path)
    print(command)
    # Run download command
    start = time.process_time()
    # Uncomment to download file
    result = subprocess.run(command.split(" "), stdout=subprocess.PIPE)
    print("time taken: ", time.process_time() - start)
    return result


def download_size(manifest):
    """
    Construct a dictionary containing the file sizes given in the manifest
    """
    to_gb = float(float(1024) ** 3)
    #
    file_size_dict = {}
    for r in manifest["directory_listing"]:
        r_dict = manifest["directory_listing"][r]
        for d in r_dict["directories"]:
            d_dict = r_dict["directories"][d]
            file_gb = d_dict["total_size"] / to_gb
            print(d_dict["relative_path"], ":", "%0.2f GB" % (file_gb))
            file_size_dict[d_dict["relative_path"]] = file_gb
    return file_size_dict


def download_meta_data(manifest, download_base=ABC_BASE):
    """
    Download all the metadata files listed in the manifest to download_base
    """
    download_results = []
    for r in manifest["directory_listing"]:
        r_dict = manifest["directory_listing"][r]
        for d in r_dict["directories"]:
            #
            if d != "metadata":
                continue
            d_dict = r_dict["directories"][d]
            local_path = os.path.join(download_base, d_dict["relative_path"])
            local_path = pathlib.Path(local_path)
            remote_path = manifest["resource_uri"] + d_dict["relative_path"]
            #
            command_pattern = "aws s3 sync --no-sign-request %s %s"
            command = command_pattern % (remote_path, local_path)
            print(command)
            #
            start = time.process_time()
            # Uncomment to download directories
            result = subprocess.run(command.split(), stdout=subprocess.PIPE)
            download_results.append(result)
            print("time taken: ", time.process_time() - start)
    return download_results


def download_abc_exp_matrices(manifest, download_base=ABC_BASE):
    """
    Download thefollowing genes expression matrices listed in the manifest 
    to download_base
       - ["WMB-10Xv2-TH"]["log2"]["files"]["h5ad"]
       - ["C57BL6J-638850"]["log2"]["files"]["h5ad"]
       - log2 files of ["Zhuang-ABCA-1", "Zhuang-ABCA-2",
                        "Zhuang-ABCA-3", "Zhuang-ABCA-4"]
    """
    # Downloading data Expresssion matrices
    exp_matrices = manifest["file_listing"]["WMB-10Xv2"]["expression_matrices"]
    file_dict = exp_matrices["WMB-10Xv2-TH"]["log2"]["files"]["h5ad"]
    print("size:", file_dict["size"])
    download_file(manifest, file_dict, download_base)
    # Downloading the MERFISH expression matrix
    # datasets = ["MERFISH-C57BL6J-638850"]
    exp_matrices = manifest["file_listing"]["MERFISH-C57BL6J-638850"][
        "expression_matrices"
    ]
    file_dict = exp_matrices["C57BL6J-638850"]["log2"]["files"]["h5ad"]
    print("size:", file_dict["size"])
    download_file(manifest, file_dict, download_base)
    # MERFISH expression matrices
    datasets = ["Zhuang-ABCA-1", "Zhuang-ABCA-2", "Zhuang-ABCA-3", "Zhuang-ABCA-4"]
    for d in datasets:
        exp_matrices = manifest["file_listing"][d]["expression_matrices"]
        file_dict = exp_matrices[d]["log2"]["files"]["h5ad"]
        print("size:", file_dict["size"])
        download_file(manifest, file_dict, download_base)


def download_image_volumes(manifest, download_base=ABC_BASE):
    """
    Download all the image volumes listed in the manifest to download_base
    """
    download_results = []
    for r in manifest["directory_listing"]:
        r_dict = manifest["directory_listing"][r]
        for d in r_dict["directories"]:
            if d != "image_volumes":
                continue
            d_dict = r_dict["directories"][d]
            local_path = os.path.join(download_base, d_dict["relative_path"])
            local_path = pathlib.Path(local_path)
            remote_path = manifest["resource_uri"] + d_dict["relative_path"]
            command_pattern = "aws s3 sync --no-sign-request %s %s"
            command = command_pattern % (remote_path, local_path)
            print(command)
            #
            start = time.process_time()
            # Uncomment to download directories
            result = subprocess.run(command.split(), stdout=subprocess.PIPE)
            download_results.append(result)
            print("time taken: ", time.process_time() - start)
    return download_results


def download_abc_data(
    manifest_url=MANIFEST_URL, version=ABC_VERSION, download_base=ABC_BASE
):
    """
    Downloads meta data, gene expression matrices and the image volumes to the
    download_base directory.
    """
    manifest = download_merfish_manifest(manifest_url, version)
    download_size(manifest)
    download_meta_data(manifest, download_base)
    download_abc_exp_matrices(manifest, download_base)
    download_image_volumes(manifest, download_base)


def view_dir(manifest, dataset_id, download_base=ABC_BASE):
    """
    Return the view directory
    """
    view_directory = os.path.join(
        download_base,
        manifest["directory_listing"][dataset_id]["directories"]["metadata"][
            "relative_path"
        ],
        "views",
    )
    return view_directory


def taxonomy_cluster(manifest, download_base=ABC_BASE):
    """
    Return the taxonomy meta data, specifically cluster name annotation and the
    colors assigned for the clusters, from download_base.
    The relative paths to the meta data files in download_base are obtaned from
    the manifest JSON object.
    """
    taxonomy_metadata = manifest["file_listing"]["WMB-taxonomy"]["metadata"]
    #  Cluster Details from Taxonomy Data
    rpath = taxonomy_metadata[
        "cluster_to_cluster_annotation_membership_pivoted"][
        "files"
    ]["csv"]["relative_path"]
    file = os.path.join(download_base, rpath)
    cluster_details = pd.read_csv(file, keep_default_na=False)
    cluster_details.set_index("cluster_alias", inplace=True)
    # Membership Color
    rpath = taxonomy_metadata[
        "cluster_to_cluster_annotation_membership_color"][
        "files"
    ]["csv"]["relative_path"]
    file = os.path.join(download_base, rpath)
    cluster_colors = pd.read_csv(file)
    cluster_colors.set_index("cluster_alias", inplace=True)
    return cluster_details, cluster_colors


def cell_metadata(file_meta, download_base=ABC_BASE):
    """
    Cell meta data frame obtained from download_base with the relative path
    of the meta data file obtained from file_meta JSON object.
    """
    rpath = file_meta["cell_metadata"]["files"]["csv"]["relative_path"]
    file = os.path.join(download_base, rpath)
    cell = pd.read_csv(file, dtype={"cell_label": str})
    cell.set_index("cell_label", inplace=True)
    return cell


def gene_metadata(file_meta, download_base=ABC_BASE):
    """
    Gene meta data frame obtained from download_base with the relative path
    of the meta data file obtained from file_meta JSON object.
    """
    # Gene Data Information
    rpath = file_meta["gene"]["files"]["csv"]["relative_path"]
    file = os.path.join(download_base, rpath)
    gene = pd.read_csv(file)
    gene.set_index("gene_identifier", inplace=True)
    return gene


def gene_expression_matrix(
    manifest,
    download_base=ABC_BASE,
    data_id="C57BL6J-638850",
    source="MERFISH-C57BL6J-638850",
    transform="log2",
):
    """
    Gene expression matrix of data id (default 'C57BL6J-638850') from the
    download_base directory. source(default 'MERFISH-C57BL6J-638850') entry 
    is used to obtain the expression matrix JSON manifest.
    """
    # gene expresssion data
    expmat_manifest = manifest["file_listing"][source]["expression_matrices"]
    rpath = expmat_manifest[data_id][transform]["files"]["h5ad"]["relative_path"]
    file = os.path.join(download_base, rpath)
    adata = anndata.read_h5ad(file, backed="r")
    return adata


def plot_section(xx, yy, cc=None, val=None, fig_width=8, fig_height=8, cmap=None):
    """
    Plot a Section of the MERFISH co-ordinates
    """
    fig, ax = plt.subplots()
    fig.set_size_inches(fig_width, fig_height)
    if cmap is not None:
        plt.scatter(xx, yy, s=0.5, c=val, marker=".", cmap=cmap)
    elif cc is not None:
        plt.scatter(xx, yy, s=0.5, color=cc, marker=".")
    ax.set_ylim(11, 0)
    ax.set_xlim(0, 11)
    ax.axis("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    return fig, ax


def create_expression_dataframe(adata, gene_meta, section_meta):
    """
    Gene expression data frame with the genes and meta data variables as its
    columns
    """
    gdata = adata[:, gene_meta.index].to_df()
    gdata.columns = gene_meta.gene_symbol
    joined = section_meta.join(gdata)
    return joined


def aggregate_by_metadata(df, gnames, group_value, sort=False):
    """
    Aggregate gene expression by 'group_value' and report the average gene
    expression values of the list of genes given by 'gnames'
    """
    grouped = df.groupby(group_value)[gnames].mean()
    if sort:
        grouped = grouped.sort_values(by=gnames[0], ascending=False)
    return grouped


def plot_heatmap(df, fig_width=8, fig_height=4, cmap=plt.cm.magma_r):
    """
    Plot Heat Map based on the input data frame
    """
    arr = df.to_numpy()
    fig, ax = plt.subplots()
    fig.set_size_inches(fig_width, fig_height)
    im = ax.imshow(arr, cmap=cmap, aspect="auto", vmin=0, vmax=5)
    xlabs = df.columns.values
    ylabs = df.index.values
    ax.set_xticks(range(len(xlabs)))
    ax.set_xticklabels(xlabs)
    ax.set_yticks(range(len(ylabs)))
    res = ax.set_yticklabels(ylabs)
    plt.setp(ax.get_xticklabels(), rotation=90)
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.set_label("Expression")
    return im


def cell_ccf_meta(ccf_meta_file):
    """
    Data frame containing the Cell Allen CCF Meta
    """
    cell_ccf = pd.read_csv(ccf_meta_file)
    return cell_ccf


def valid_genes_symbols(gene_meta):
    """
    Genes that doesn't contain 'Blank'
    """
    return gene_meta[~gene_meta.gene_symbol.str.contains("Blank")].gene_symbol.values


def filter_invalid_genes(gene_meta, valid_genes):
    """
    Select the valid genes
    """
    # Remove "blank" genes
    pred = [x in valid_genes for x in gene_meta.gene_symbol]
    gf = gene_meta[pred]
    return gf


# def main():
#     #
#     agg = aggregate_by_metadata(ntexp, vgene_meta.gene_symbol,
#                                 "parcellation_substructure")
#     select_genes = [
#         "Rbp4",
#         "Tshz2",
#         "Slc17a8",
#         "Slc17a7",
#         "Cbln4",
#         "Calb1",
#         "Vwc2l",
#         "Hs3st4",
#         "Gpr88",
#         "Cdh9",
#         "Kcng1",
#         "Gad2",
#         "Vip",
#         "Pvalb",
#     ]
#     im = plot_heatmap(agg[select_genes])
