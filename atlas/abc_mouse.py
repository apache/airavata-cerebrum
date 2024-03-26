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
TAXONOMY_META_FIELDS = [
    "cluster",
    "cluster_annotation_term",
    "cluster_annotation_term_set",
    "cluster_to_cluster_annotation_membership",
    "cluster_to_cluster_annotation_membership_pivoted",
    "cluster_to_cluster_annotation_membership_color",
    "cluster_annotation_term_with_counts",
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


def taxonomy_meta(manifest, data_key, download_base=ABC_BASE):
    """
    Return the taxonomy meta data, as located in data_key, from download_base.
    The relative paths to the meta data files in download_base are obtaned from
    the manifest JSON object.
    """
    taxonomy_metadata = manifest["file_listing"]["WMB-taxonomy"]["metadata"]
    #  Cluster Details from Taxonomy Data
    rpath = taxonomy_metadata[data_key]["files"]["csv"]["relative_path"]
    file = os.path.join(download_base, rpath)
    taxnm_meta_df = pd.read_csv(file, keep_default_na=False)
    if "cluster_alias" in taxnm_meta_df.columns:
        taxnm_meta_df.set_index("cluster_alias", inplace=True)
    return taxnm_meta_df


def taxonomy_cluster(manifest, download_base=ABC_BASE):
    """
    Return the taxonomy meta data, specifically cluster name annotation and the
    colors assigned for the clusters, from download_base.
    The relative paths to the meta data files in download_base are obtaned from
    the manifest JSON object.
    """
    taxonomy_metadata = manifest["file_listing"]["WMB-taxonomy"]["metadata"]
    #
    #  Cluster Details from Taxonomy Data
    cluster_details = taxonomy_meta(
        manifest, "cluster_to_cluster_annotation_membership_pivoted", download_base
    )
    # rpath = taxonomy_metadata["cluster_to_cluster_annotation_membership_pivoted"][
    #     "files"
    # ]["csv"]["relative_path"]
    # file = os.path.join(download_base, rpath)
    # cluster_details = pd.read_csv(file, keep_default_na=False)
    # cluster_details.set_index("cluster_alias", inplace=True)
    #
    # Membership Color
    cluster_colors = taxonomy_meta(
        manifest, "cluster_to_cluster_annotation_membership_color", download_base
    )
    #
    # rpath = taxonomy_metadata["cluster_to_cluster_annotation_membership_color"][
    #     "files"
    # ]["csv"]["relative_path"]
    # file = os.path.join(download_base, rpath)
    # cluster_colors = pd.read_csv(file)
    # cluster_colors.set_index("cluster_alias", inplace=True)
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


def plot_heatmap(df, ylabel="Expression", lmin=0, lmax=5, fig_width=8, fig_height=4,
                 cmap=plt.cm.magma_r):
    """
    Plot Heat Map based on the input data frame
    """
    arr = df.to_numpy()
    fig, ax = plt.subplots()
    fig.set_size_inches(fig_width, fig_height)
    im = ax.imshow(arr, cmap=cmap, aspect="auto", vmin=lmin, vmax=lmax)
    xlabs = df.columns.values
    ylabs = df.index.values
    ax.set_xticks(range(len(xlabs)))
    ax.set_xticklabels(xlabs)
    ax.set_yticks(range(len(ylabs)))
    res = ax.set_yticklabels(ylabs)
    plt.setp(ax.get_xticklabels(), rotation=90)
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.set_label(ylabel)
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


def cell_meta_ei_flags(area_cell_df):
    pred_glut = area_cell_df["class"].str.endswith("Glut")
    pred_gaba = area_cell_df["class"].str.endswith("GABA")
    pred_other = ~(pred_glut | pred_gaba)
    # Flags for GABA and Glut cells
    area_cell_df.loc[:, ["E"]] = pred_glut
    area_cell_df.loc[:, ["I"]] = pred_gaba
    area_cell_df.loc[:, ["O"]] = pred_other
    return area_cell_df


def cell_meta_gaba_flags(area_cell_df):
    if len(area_cell_df) == 0:
        return area_cell_df
    # GABA Sub types
    pred_gaba = area_cell_df["subclass"].str.endswith("Gaba")
    pred_lamp5 = area_cell_df["subclass"].isin(
        set(["049 Lamp5 Gaba", "050 Lamp5 Lhx6 Gaba"])
    )
    pred_sst = area_cell_df["subclass"].isin(
        set(["053 Sst Gaba", "265 PB Sst Gly-Gaba"])
    )
    pred_sst_chodl = area_cell_df["subclass"].isin(set(["056 Sst Chodl Gaba"]))
    pred_pvalb = area_cell_df["subclass"].isin(
        set(["051 Pvalb chandelier Gaba", "052 Pvalb Gaba"])
    )
    pred_vip = area_cell_df["subclass"].isin(set(["046 Vip Gaba"]))
    pred_other = pred_gaba & (
        ~(pred_lamp5 | pred_sst | pred_sst_chodl | pred_pvalb | pred_vip)
    )
    # Select only GABA and Glut cells
    area_cell_df.loc[:, ["GABA"]] = pred_gaba
    area_cell_df.loc[:, ["Vip"]] = pred_vip
    area_cell_df.loc[:, ["Pvalb"]] = pred_pvalb
    area_cell_df.loc[:, ["Sst"]] = pred_sst
    area_cell_df.loc[:, ["Lamp5"]] = pred_lamp5
    area_cell_df.loc[:, ["Sst-Chodl"]] = pred_sst_chodl
    area_cell_df.loc[:, ["GABA-Other"]] = pred_other
    return area_cell_df


def cell_meta_glut_flags(area_cell_df):
    if len(area_cell_df) == 0:
        return area_cell_df
    # Glut Sub-types
    pred_glut = area_cell_df["subclass"].str.endswith("Glut")
    pred_et = area_cell_df["subclass"].isin(set(["022 L5 ET CTX Glut"]))
    pred_ct = area_cell_df["subclass"].isin(
        set(["028 L6b/CT ENT Glut", "030 L6 CT CTX Glut", "031 CT SUB Glut"])
    )
    pred_it_oth = area_cell_df["subclass"].isin(
        set(
            [
                "002 IT EP-CLA Glut",
                "010 IT AON-TT-DP Glut",
                "018 L2 IT PPP-APr Glut",
                "019 L2/3 IT PPP Glut",
                "020 L2/3 IT RSP Glut",
            ]
        )
    )
    pred_it_ent = area_cell_df["subclass"].isin(
        set(
            [
                "003 L5/6 IT TPE-ENT Glut",
                "008 L2/3 IT ENT Glut",
                "009 L2/3 IT PIR-ENTl Glut",
                "011 L2 IT ENT-po Glut",
            ]
        )
    )
    pred_it_ctx = area_cell_df["subclass"].isin(
        set(
            [
                "004 L6 IT CTX Glut",
                "005 L5 IT CTX Glut",
                "006 L4/5 IT CTX Glut",
                "007 L2/3 IT CTX Glut",
            ]
        )
    )
    pred_np = area_cell_df["subclass"].isin(
        set(["032 L5 NP CTX Glut", "033 NP SUB Glut", "034 NP PPP Glut"])
    )
    pred_it = pred_it_ctx | pred_it_ent | pred_it_oth
    pred_other = pred_glut & (~(pred_et | pred_ct | pred_it | pred_np))
    # Select only Glut cells
    area_cell_df.loc[:, ["Glut"]] = pred_glut
    area_cell_df.loc[:, ["IT-Other"]] = pred_it_oth
    area_cell_df.loc[:, ["IT-ENT"]] = pred_it_ent
    area_cell_df.loc[:, ["IT-CTX"]] = pred_it_ctx
    area_cell_df.loc[:, ["IT"]] = pred_it
    area_cell_df.loc[:, ["ET"]] = pred_et
    area_cell_df.loc[:, ["CT"]] = pred_ct
    area_cell_df.loc[:, ["NP"]] = pred_np
    area_cell_df.loc[:, ["Glut-Other"]] = pred_other
    return area_cell_df


def cell_meta_type_flags(area_cell_df):
    area_cell_df = cell_meta_ei_flags(area_cell_df)
    return cell_meta_glut_flags(cell_meta_gaba_flags(area_cell_df))


def cell_meta_type_ratios(area_sumdf, ax, nregion):
    area_sumdf["Region"] = ax
    area_sumdf["Layer"] = [x.replace(ax, "") for x in area_sumdf.index]
    area_sumdf["nregion"] = nregion
    area_sumdf["T"] = area_sumdf["E"] + area_sumdf["I"] + area_sumdf["O"]
    area_sumdf["EI"] = area_sumdf["E"] + area_sumdf["I"]
    area_sumdf["inhibitory fraction"] = area_sumdf["I"] / area_sumdf["EI"]
    area_sumdf["fraction wi. region"] = area_sumdf["T"] / nregion
    #
    area_sumdf["Vip fraction"] = area_sumdf["Vip"] / area_sumdf["GABA"]
    area_sumdf["Pvalb fraction"] = area_sumdf["Pvalb"] / area_sumdf["GABA"]
    area_sumdf["SSt fraction"] = area_sumdf["Sst"] / area_sumdf["GABA"]
    area_sumdf["Lamp5 fraction"] = area_sumdf["Lamp5"] / area_sumdf["GABA"]
    area_sumdf["Sst-Chodl fraction"] = area_sumdf["Sst-Chodl"] / area_sumdf["GABA"]
    area_sumdf["GABA Other fraction"] = area_sumdf["GABA-Other"] / area_sumdf["GABA"]
    area_sumdf["IT-CTX fraction"] = area_sumdf["IT-CTX"] / area_sumdf["Glut"]
    area_sumdf["IT-ENT fraction"] = area_sumdf["IT-ENT"] / area_sumdf["Glut"]
    area_sumdf["IT-Other fraction"] = area_sumdf["IT-Other"] / area_sumdf["Glut"]
    area_sumdf["IT fraction"] = area_sumdf["IT"] / area_sumdf["Glut"]
    area_sumdf["ET fraction"] = area_sumdf["ET"] / area_sumdf["Glut"]
    area_sumdf["CT fraction"] = area_sumdf["CT"] / area_sumdf["Glut"]
    area_sumdf["NP fraction"] = area_sumdf["NP"] / area_sumdf["Glut"]
    area_sumdf["Glut Other fraction"] = area_sumdf["Glut-Other"] / area_sumdf["Glut"]
    return area_sumdf


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
