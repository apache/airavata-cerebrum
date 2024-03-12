import requests
import json
import os
import pathlib
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


def download_merfish_manifest(version=ABC_VERSION):
    # use_local_cache = False
    # manifest_path = 'releases/%s/manifest.json' % version
    # if not use_local_cache :
    url = MANIFEST_URL.format(version)
    manifest = json.loads(requests.get(url).text)
    return manifest


def merfish_files_meta():
    manifest = download_merfish_manifest()
    merf_meta = manifest["file_listing"]["MERFISH-C57BL6J-638850"]["metadata"]
    return manifest, merf_meta


def view_dir(manifest, dataset_id, download_base=ABC_BASE):
    view_directory = os.path.join(
        download_base,
        manifest["directory_listing"][dataset_id]["directories"]["metadata"][
            "relative_path"
        ],
        "views",
    )
    return view_directory


def taxonomy_cluster(manifest, download_base=ABC_BASE):
    taxonomy_metadata = manifest["file_listing"]["WMB-taxonomy"]["metadata"]
    #  Cluster Details from Taxonomy Data
    rpath = taxonomy_metadata["cluster_to_cluster_annotation_membership_pivoted"][
        "files"
    ]["csv"]["relative_path"]
    file = os.path.join(download_base, rpath)
    cluster_details = pd.read_csv(file, keep_default_na=False)
    cluster_details.set_index("cluster_alias", inplace=True)
    # Membership Color
    rpath = taxonomy_metadata["cluster_to_cluster_annotation_membership_color"][
        "files"
    ]["csv"]["relative_path"]
    file = os.path.join(download_base, rpath)
    cluster_colors = pd.read_csv(file)
    cluster_colors.set_index("cluster_alias", inplace=True)
    return cluster_details, cluster_colors


def cell_metadata(file_meta, download_base=ABC_BASE):
    rpath = file_meta["cell_metadata"]["files"]["csv"]["relative_path"]
    file = os.path.join(download_base, rpath)
    cell = pd.read_csv(file, dtype={"cell_label": str})
    cell.set_index("cell_label", inplace=True)
    return cell


def gene_metadata(file_meta, download_base=ABC_BASE):
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
    # gene expresssion data
    expmat_manifest = manifest["file_listing"][source]["expression_matrices"]
    rpath = expmat_manifest[data_id][transform]["files"]["h5ad"]["relative_path"]
    file = os.path.join(download_base, rpath)
    adata = anndata.read_h5ad(file, backed="r")
    return adata


def plot_section(xx, yy, cc=None, val=None, fig_width=8, fig_height=8, cmap=None):
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
    gdata = adata[:, gene_meta.index].to_df()
    gdata.columns = gene_meta.gene_symbol
    joined = section_meta.join(gdata)
    return joined


def aggregate_by_metadata(df, gnames, value, sort=False):
    grouped = df.groupby(value)[gnames].mean()
    if sort:
        grouped = grouped.sort_values(by=gnames[0], ascending=False)
    return grouped


def plot_heatmap(df, fig_width=8, fig_height=4, cmap=plt.cm.magma_r):
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
    cell_ccf = pd.read_csv(ccf_meta_file)
    return cell_ccf


def valid_genes_symbols(gene_meta):
    return gene_meta[~gene_meta.gene_symbol.str.contains("Blank")].gene_symbol.values


def filter_invalid_genes(gene_meta, valid_genes):
    # Remove "blank" genes
    pred = [x in valid_genes for x in gene_meta.gene_symbol]
    gf = gene_meta[pred]
    return gf


# def main():
#    #
#     agg = aggregate_by_metadata(ntexp, vgene_meta.gene_symbol, "parcellation_substructure")
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
