import requests
import json
import os
import pathlib
import subprocess
import time
import pandas as pd
import anndata
import matplotlib.pyplot as plt
import abc_atlas_access.abc_atlas_cache.abc_project_cache as abc_cache

from ..log.logging import LOGGER

ABC_VERSION = "20231215"
MANIFEST_URL = "https://allen-brain-cell-atlas.s3-us-west-2.amazonaws.com/releases/{}/manifest.json"
PARCEL_META_DATA_KEY = "cell_metadata_with_parcellation_annotation"
PARCEL_META_DATA_CSV = PARCEL_META_DATA_KEY + ".csv"
MERFISH_CCF_DATASET_KEY = "MERFISH-C57BL6J-638850-CCF"
PARCELLATION_SUBSTRUCTURE = "parcellation_substructure"
PARCELLATION_STRUCTURE = "parcellation_structure"
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
GABA = "GABA"
GABA_TYPES = ["Sst", "Lamp5", "Sst-Chodl", "Pvalb", "Vip", "GABA-Other"]
GLUT = "Glut"
GLUT_TYPES = [
    "IT",
    "ET",
    "CT",
    "NP",
    "Glut-Other",
]
GLUT_IT_TYPES = [
    "IT-CTX",
    "IT-ENT",
    "IT-Other",
]
# Column Names
GABA_COLUMNS = [GABA] + GABA_TYPES
GLUT_COLUMNS = [GLUT] + GLUT_IT_TYPES + GLUT_TYPES
# GABA subclasses
LAMP5_SUBCLASSES = set(["049 Lamp5 Gaba", "050 Lamp5 Lhx6 Gaba"])
SST_SUBCLASSES = set(["053 Sst Gaba", "265 PB Sst Gly-Gaba"])
SST_CHODL_SUBCLASSES = set(["056 Sst Chodl Gaba"])
PVALB_SUBCLASSES = set(["051 Pvalb chandelier Gaba", "052 Pvalb Gaba"])
VIP_SUBCLASSES = set(["046 Vip Gaba"])
# Glut subclasses
ET_SUBCLASSES = set(["022 L5 ET CTX Glut"])
CT_SUBCLASSES = set(["028 L6b/CT ENT Glut", "030 L6 CT CTX Glut", "031 CT SUB Glut"])
IT_OTHER_SUBCLASSES = set(
    [
        "002 IT EP-CLA Glut",
        "010 IT AON-TT-DP Glut",
        "018 L2 IT PPP-APr Glut",
        "019 L2/3 IT PPP Glut",
        "020 L2/3 IT RSP Glut",
    ]
)
IT_ENT_SUBCLASSES = set(
    [
        "003 L5/6 IT TPE-ENT Glut",
        "008 L2/3 IT ENT Glut",
        "009 L2/3 IT PIR-ENTl Glut",
        "011 L2 IT ENT-po Glut",
    ]
)
IT_CTX_SUBCLASSES = set(
    [
        "004 L6 IT CTX Glut",
        "005 L5 IT CTX Glut",
        "006 L4/5 IT CTX Glut",
        "007 L2/3 IT CTX Glut",
    ]
)
IT_SUBCLASSES = IT_ENT_SUBCLASSES | IT_CTX_SUBCLASSES | IT_OTHER_SUBCLASSES
NP_SUBCLASSES = set(["032 L5 NP CTX Glut", "033 NP SUB Glut", "034 NP PPP Glut"])
GLUT_SUBCLASS_SETMAP = {
    "IT-Other" : IT_OTHER_SUBCLASSES,
    "IT-ENT" : IT_ENT_SUBCLASSES,
    "IT-CTX" : IT_CTX_SUBCLASSES,
    "IT" : IT_SUBCLASSES,
    "ET" : ET_SUBCLASSES,
    "CT" : CT_SUBCLASSES,
    "NP" : NP_SUBCLASSES,
}
GABA_SUBCLASS_SETMAP = {
    "Vip": VIP_SUBCLASSES,
    "Pvalb": PVALB_SUBCLASSES,
    "Sst": SST_SUBCLASSES,
    "Lamp5": LAMP5_SUBCLASSES,
    "Sst-Chodl": SST_CHODL_SUBCLASSES
}
FRACTION_COLUMN_FMT = "{} fraction"
INHIBITORY_FRACTION_COLUMN = "inhibitory fraction"
FRACTION_WI_REGION_COLUMN = "fraction wi. region"


def download_merfish_manifest(manifest_url=MANIFEST_URL, version=ABC_VERSION):
    """
    Downloads the Manifiest JSON data from ABC AWS Store

    Parameters
    ----------
    manifest_url : str
        URL to the json manifest that describes ABC data (
        default is abc_mouse.MANIFEST_URL)
    version : str
        Dataset version (default is abc_mouse.ABC_VERSION)

    Returns
    -------
    dict
        manifest json as a dict
    """
    url = manifest_url.format(version)
    manifest = json.loads(requests.get(url).text)
    return manifest


def merfish_files_meta():
    """
    Downloads the Manifiest JSON data from ABC AWS Store and retrieve
    MERFISH-C57BL6J-638850 meta data JSON object.

    Parameters
    ----------
    None

    Returns
    -------
    tuple
        manifest, merf_data : manifest is dict representation of the json,
        merf_data is the value at
        manifest["file_listing"]["MERFISH-C57BL6J-638850"]["metadata"]

    """
    manifest = download_merfish_manifest()
    merf_meta = manifest["file_listing"]["MERFISH-C57BL6J-638850"]["metadata"]
    return manifest, merf_meta


def download_file(manifest, file_dict, download_base):
    """
    Given a file entry in manifest, download the file using AWS CLI 'aws'
    to the relative path constructed from the download_base.
    Assumes that the aws command is available is installed in the current
    environment.

    A simple file entry in manifest is as follows:
    {
     'version': '20230630',
     'relative_path': 'expression_matrices/WMB-10Xv3/20230630',
     'url': 'https://allen-brain-cell-atlas.s3.us-west-2.amazonaws.com/expression_matrices/WMB-10Xv3/20230630/',
     'view_link':
     'https://allen-brain-cell-atlas.s3.us-west-2.amazonaws.com/index.html#expression_matrices/WMB-10Xv3/20230630/',
     'total_size': 189424020276
    }

    Parameters
    ----------
    manifest : dict
        manifest json as a dict
    file_dict : dict
        file entry within the manifest json as a dict. An example:
        {
         'version': '20230630',
         'relative_path': 'expression_matrices/WMB-10Xv3/20230630',
         'url': 'https://allen-brain-cell-atlas.s3.us-west-2.amazonaws.com/expression_matrices/WMB-10Xv3/20230630/',
         'view_link':
         'https://allen-brain-cell-atlas.s3.us-west-2.amazonaws.com/index.html#expression_matrices/WMB-10Xv3/20230630/',
         'total_size': 189424020276
        }
    download_base : str
        Base directory on to which the file will be downloaded in the relative
        path.

    Returns
    -------
    int
        Return value of the aws download command.

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
    Construct a dictionary containing the file sizes in GB given in the
    manifest

    Parameters
    ----------
    manifest : dict
        manifest json as a dict.

    Returns
    -------
    dict
        A dictionary containing the file sizes in GB of each of the files.
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


def download_meta_data(manifest, download_base):
    """
    Download all the metadata files using AWS CLI listed in the manifest to
    download_base.
    Assumes that the AWS command line excutable is available and installed.

    Parameters
    ----------
    manifest : dict
        manifest json as a dict.
    download_base: str
        Directory to which meta data is to be downloaded (default is
        abc_mouse.ABC_BASE)

    Returns
    -------
    list
        List of return values of the executions download commands.
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


def download_abc_exp_matrices(manifest, download_base):
    """
    Download the following genes expression matrices listed in the manifest
    to download_base location:
       - ["WMB-10Xv2-TH"]["log2"]["files"]["h5ad"]
       - ["C57BL6J-638850"]["log2"]["files"]["h5ad"]
       - log2 expression matrices as h5ad files of the datasets:
          ["Zhuang-ABCA-1", "Zhuang-ABCA-2", "Zhuang-ABCA-3", "Zhuang-ABCA-4"]

    Parameters
    ----------
    manifest : dict
        manifest json as a dict.
    download_base: str
        Directory to which meta data is to be downloaded (default is
        abc_mouse.ABC_BASE)

    Returns
    -------
    list
        List of return values of the executions download commands.
    """
    download_results = []
    start = time.process_time()
    # Downloading data Expresssion matrices
    exp_matrices = manifest["file_listing"]["WMB-10Xv2"]["expression_matrices"]
    file_dict = exp_matrices["WMB-10Xv2-TH"]["log2"]["files"]["h5ad"]
    print("size:", file_dict["size"])
    result = download_file(manifest, file_dict, download_base)
    download_results.append(result)
    # Downloading the MERFISH expression matrix
    # datasets = ["MERFISH-C57BL6J-638850"]
    exp_matrices = manifest["file_listing"]["MERFISH-C57BL6J-638850"][
        "expression_matrices"
    ]
    file_dict = exp_matrices["C57BL6J-638850"]["log2"]["files"]["h5ad"]
    print("size:", file_dict["size"])
    result = download_file(manifest, file_dict, download_base)
    download_results.append(result)
    # MERFISH expression matrices
    datasets = ["Zhuang-ABCA-1", "Zhuang-ABCA-2", "Zhuang-ABCA-3", "Zhuang-ABCA-4"]
    for d in datasets:
        exp_matrices = manifest["file_listing"][d]["expression_matrices"]
        file_dict = exp_matrices[d]["log2"]["files"]["h5ad"]
        print("size:", file_dict["size"])
        result = download_file(manifest, file_dict, download_base)
        download_results.append(result)
    print("time taken: ", time.process_time() - start)
    return download_results


def download_image_volumes(manifest, download_base):
    """
    Download all the image volumes listed in the manifest to download_base

    Parameters
    ----------
    manifest : dict
        manifest json as a dict.
    download_base: str
        Directory to which meta data is to be downloaded (default is
        abc_mouse.ABC_BASE)

    Returns
    -------
    list
        List of return values of the executions download commands.
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
    download_base, version=ABC_VERSION, manifest_url=MANIFEST_URL
):
    """
    Downloads meta data, gene expression matrices and the image volumes to the
    download_base directory.

    Parameters
    ----------
    manifest : dict
        manifest json as a dict.
    version : str
        version string (default is ABC_VERSION)
    download_base: str
        Directory to which meta data is to be downloaded (default is
        abc_mouse.ABC_BASE)

    Returns
    -------
    None
    """
    manifest = download_merfish_manifest(manifest_url, version)
    download_size(manifest)
    download_meta_data(manifest, download_base)
    download_abc_exp_matrices(manifest, download_base)
    download_image_volumes(manifest, download_base)


def view_dir(manifest, dataset_id, download_base):
    """
    Return the view directory

    Parameters
    ----------
    manifest : dict
        manifest json as a dict.
    dataset_id : str
        Dataset identfier
    download_base: str
        Directory to which meta data is to be downloaded (default is
        abc_mouse.ABC_BASE)

    Returns
    -------
    str
        view_directory location
    """
    view_directory = os.path.join(
        download_base,
        manifest["directory_listing"][dataset_id]["directories"]["metadata"][
            "relative_path"
        ],
        "views",
    )
    return view_directory


def taxonomy_meta(manifest, data_key, download_base):
    """
    Return the taxonomy meta data, as located in data_key, from download_base.
    The relative paths to the meta data files in download_base are obtaned from
    the manifest JSON object.

    Parameters
    ----------
    manifest : dict
        manifest json as a dict.
    dataset_key : str
        Dataset identfier
    download_base: str
        Directory to which meta data is to be downloaded (default is
        abc_mouse.ABC_BASE)

    Returns
    -------
    pandas.DataFrame
       Taxonomy data for each of the cell, with each row being a cell.
    """
    taxonomy_metadata = manifest["file_listing"]["WMB-taxonomy"]["metadata"]
    #  Cluster Details from Taxonomy Data
    rpath = taxonomy_metadata[data_key]["files"]["csv"]["relative_path"]
    file = os.path.join(download_base, rpath)
    taxnm_meta_df = pd.read_csv(file, keep_default_na=False)
    if "cluster_alias" in taxnm_meta_df.columns:
        taxnm_meta_df.set_index("cluster_alias", inplace=True)
    return taxnm_meta_df


def taxonomy_cluster(manifest, download_base):
    """
    Return the taxonomy meta data, specifically cluster name annotation and the
    colors assigned for the clusters, from download_base.
    The relative paths to the meta data files in download_base are obtaned from
    the manifest JSON object.

    Parameters
    ----------
    manifest : dict
        manifest json as a dict.
    download_base: str
        Directory to which meta data is to be downloaded (default is
        abc_mouse.ABC_BASE)

    Returns
    -------
    (pandas.DataFrame, pandas.DataFrame)
       Cluster name and Cluster colors as two data frames for each of the cell,
       with each row being a cell.
    """
    #  Cluster Details from Taxonomy Data
    cluster_details = taxonomy_meta(
        manifest, "cluster_to_cluster_annotation_membership_pivoted", download_base
    )
    #
    # Membership Color
    cluster_colors = taxonomy_meta(
        manifest, "cluster_to_cluster_annotation_membership_color", download_base
    )
    return cluster_details, cluster_colors


def cell_metadata(file_meta, download_base):
    """
    Cell meta data frame obtained from download_base with the relative path
    of the meta data file obtained from file_meta JSON object.

    Parameters
    ----------
    manifest : dict
        manifest json as a dict.
    download_base: str
        Directory to which meta data is to be downloaded (default is
        abc_mouse.ABC_BASE)

    Returns
    -------
    pandas.DataFrame
       Cell meta data for each of the cell, with each row being a cell.

    """
    rpath = file_meta["cell_metadata"]["files"]["csv"]["relative_path"]
    file = os.path.join(download_base, rpath)
    cell_df = pd.read_csv(file, dtype={"cell_label": str})
    cell_df.set_index("cell_label", inplace=True)
    return cell_df


def gene_metadata(file_meta, download_base):
    """
    Gene meta data frame obtained from download_base with the relative path
    of the meta data file obtained from file_meta JSON object.

    Parameters
    ----------
    manifest : dict
        manifest json as a dict.
    download_base: str
        Directory to which meta data is to be downloaded (default is
        abc_mouse.ABC_BASE)

    Returns
    -------
    pandas.DataFrame
       Gene meta data for each of the cell, with each row being a gene.
    """
    # Gene Data Information
    rpath = file_meta["gene"]["files"]["csv"]["relative_path"]
    file = os.path.join(download_base, rpath)
    gene_df = pd.read_csv(file)
    gene_df.set_index("gene_identifier", inplace=True)
    return gene_df


def gene_expression_matrix(
    manifest,
    download_base,
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
    fig.set_size_inches(fig_width, fig_height)  # type:ignore
    if cmap is not None:
        plt.scatter(xx, yy, s=0.5, c=val, marker=".", cmap=cmap)
    elif cc is not None:
        plt.scatter(xx, yy, s=0.5, color=cc, marker=".")
    ax.set_ylim(11, 0)  # type:ignore
    ax.set_xlim(0, 11)  # type:ignore
    ax.axis("equal")   # type:ignore
    ax.set_xticks([])   # type:ignore
    ax.set_yticks([])   # type:ignore
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


def plot_heatmap(
    df,
    ylabel="Expression",
    lmin=0,
    lmax=5,
    fig_width=8,
    fig_height=4,
    cmap=plt.cm.magma_r,  # type:ignore
):
    """
    Plot Heat Map based on the input data frame
    """
    arr = df.to_numpy()
    fig, ax = plt.subplots()
    fig.set_size_inches(fig_width, fig_height)  # type:ignore
    im = ax.imshow(arr, cmap=cmap, aspect="auto", vmin=lmin, vmax=lmax)  # type:ignore
    xlabs = df.columns.values
    ylabs = df.index.values
    ax.set_xticks(range(len(xlabs)))  # type:ignore
    ax.set_xticklabels(xlabs)  # type:ignore
    ax.set_yticks(range(len(ylabs)))  # type:ignore
    ax.set_yticklabels(ylabs)  # type:ignore
    plt.setp(ax.get_xticklabels(), rotation=90)  # type:ignore
    cbar = ax.figure.colorbar(im, ax=ax)  # type:ignore
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
    """
    Cell meta data frame with flags added to indicate
    excitatory ('E'), inhibitory ('I'), Other ('O')
    based on whether the class of the cell property "class"
    ends with "Glut" (E) or "GABA" (I)
    """
    pred_glut = area_cell_df["class"].str.endswith("Glut")
    pred_gaba = area_cell_df["class"].str.endswith("GABA")
    pred_other = ~(pred_glut | pred_gaba)
    pred_other = pred_other.copy()
    # Flags for GABA and Glut cells
    area_cell_df.loc[:, "E"] = pred_glut
    area_cell_df.loc[:, "I"] = pred_gaba
    area_cell_df.loc[:, "O"] = pred_other
    return area_cell_df


def cell_meta_subclass_flags(area_cell_df, subclass_mapset: dict):
    pred_subclass = {}
    for kx, subx in subclass_mapset.items():
        pred_subclass[kx] = area_cell_df["subclass"].isin(subx)
    return pred_subclass


def cell_meta_gaba_flags(area_cell_df):
    if len(area_cell_df) == 0:
        return area_cell_df
    pred_gaba = area_cell_df["subclass"].str.endswith("Gaba")
    # GABA Sub types
    pred_gaba_subclass_map = cell_meta_subclass_flags(area_cell_df,
                                                      GABA_SUBCLASS_SETMAP)
    area_cell_df.loc[:, "GABA"] = pred_gaba
    for kv, pred_series in pred_gaba_subclass_map.items():
        area_cell_df.loc[:, kv] = pred_series
    gaba_classifieds = ["Vip", "Pvalb", "Sst", "Sst-Chodl", "Lamp5"]
    pred_gaba_classified = area_cell_df.loc[:, gaba_classifieds].any(
        axis="columns")
    area_cell_df.loc[:, "GABA-Other"] = pred_gaba & (~pred_gaba_classified)
    return area_cell_df


def cell_meta_glut_flags(area_cell_df: pd.DataFrame):
    if len(area_cell_df) == 0:
        return area_cell_df
    # Glut Sub-types
    pred_glut = area_cell_df["subclass"].str.endswith("Glut")
    pred_glut_subclass_map = cell_meta_subclass_flags(area_cell_df,
                                                      GLUT_SUBCLASS_SETMAP)
    area_cell_df.loc[:, "Glut"] = pred_glut
    for kv, pred_series in pred_glut_subclass_map.items():
        area_cell_df.loc[:, kv] = pred_series
    glut_classifieds = ["ET", "CT", "IT", "NP"]
    pred_glut_classified = area_cell_df.loc[:, glut_classifieds].any(
        axis="columns")
    area_cell_df.loc[:, "Glut-Other"] = pred_glut & (~pred_glut_classified)
    return area_cell_df


def cell_meta_type_flags(area_cell_df: pd.DataFrame):
    return cell_meta_glut_flags(
        cell_meta_gaba_flags(
            cell_meta_ei_flags(area_cell_df)))


def cell_meta_type_ratios(area_sumdf, ax, nregion):
    ratio_df = pd.DataFrame(index=area_sumdf.index)
    #
    ratio_df["Region"] = ax
    ratio_df["Layer"] = [x.replace(ax, "") for x in ratio_df.index]
    ratio_df["nregion"] = nregion
    ratio_df[INHIBITORY_FRACTION_COLUMN] = area_sumdf["I"] / area_sumdf["EI"]
    ratio_df[FRACTION_WI_REGION_COLUMN] = area_sumdf["T"] / nregion
    #
    for colx in GABA_TYPES:
        fraction_col = FRACTION_COLUMN_FMT.format(colx)
        ratio_df[fraction_col] = area_sumdf[colx] / area_sumdf[GABA]
    #
    for colx in GLUT_IT_TYPES:
        fraction_col = FRACTION_COLUMN_FMT.format(colx)
        ratio_df[fraction_col] = area_sumdf[colx] / area_sumdf[GLUT]
    #
    for colx in GLUT_TYPES:
        fraction_col = FRACTION_COLUMN_FMT.format(colx)
        ratio_df[fraction_col] = area_sumdf[colx] / area_sumdf[GLUT]
    return ratio_df


def region_ccf_cell_types(cell_ccf, region_list):
    #
    region_ctx_ccf = {}
    region_frac_ccf = {}
    region_cell_ccf = {}
    # Columns
    ei_cols = [PARCELLATION_SUBSTRUCTURE, "E", "I", "O"]
    sel_cols = ei_cols + GABA_COLUMNS + GLUT_COLUMNS
    #
    for region in region_list:
        # Select the CCF meta data specific to the above region
        region_df = cell_ccf.loc[cell_ccf[PARCELLATION_STRUCTURE] == region]
        # Ignore the regions for which no cells are available
        if len(region_df) == 0:
            continue
        # 1. Flags corresponding to meta data
        region_df = region_df.copy()
        region_df = cell_meta_type_flags(region_df)
        # 2. Group by sub structure and find summary counts for each layer
        region_ei_df = region_df[sel_cols].copy()
        region_ei_ctx = region_ei_df.groupby(PARCELLATION_SUBSTRUCTURE).sum()
        region_ei_ctx["T"] = region_ei_ctx["E"] + region_ei_ctx["I"] + region_ei_ctx["O"]  # type:ignore
        region_ei_ctx["EI"] = region_ei_ctx["E"] + region_ei_ctx["I"]   # type: ignore
        n_region_layers = len(region_df)
        region_name = region
        # 3. Compute the ratios
        region_ei_ratio = cell_meta_type_ratios(
            region_ei_ctx, region_name, n_region_layers
        )
        # Save to the data frame to the dict
        region_cell_ccf[region] = region_df
        region_ctx_ccf[region] = region_ei_ctx
        region_frac_ccf[region] = region_ei_ratio
    return region_cell_ccf, region_ctx_ccf, region_frac_ccf


def region_cell_type_ratios(region_name,
                            download_base):
    manifest, _ = merfish_files_meta()
    # Cell Meta and CCF Meta data
    merfish_ccf_view_dir = view_dir(manifest, MERFISH_CCF_DATASET_KEY,
                                    download_base)
    cell_ccf = cell_ccf_meta(
        os.path.join(merfish_ccf_view_dir, PARCEL_META_DATA_CSV)
    )
    _, _, region_frac_ccf = region_ccf_cell_types(cell_ccf, [region_name])
    return region_frac_ccf[region_name]


class ABCDbMERFISH_CCFQuery:
    def __init__(self, **params):
        """
        Initialize MERFISH Query
        Parameters
        ----------
        download_base : str (Mandatory)
           File location to store the manifest and the cells.json files

        """
        self.name = __name__ + ".ABCDbMERFISHQuery"
        self.download_base = params["download_base"]
        self.pcache = abc_cache.AbcProjectCache.from_s3_cache(self.download_base)
        self.pcache.load_latest_manifest()
        self.pcache.get_directory_metadata(MERFISH_CCF_DATASET_KEY)
        self.ccf_meta_file = self.pcache.get_metadata_path(MERFISH_CCF_DATASET_KEY,
                                                           PARCEL_META_DATA_KEY)

    def run(self, in_stream, **params):
        """
        Get the cell types ratios corresponding to a region

        Parameters
        ----------
        run_params: dict with the following keys:
            region : List[str]
             lis of regions of interest
        Returns
        -------
        dict of elements for each sub-regio:
        {
            subr 1 : {}
        }
        """
        #
        default_args = {}
        rarg = (
            {**default_args, **params} if params is not None else default_args
        )
        LOGGER.info("ABCDbMERFISH_CCFQuery Args : %s", rarg)
        region_list = rarg["region"]
        #
        mfish_ccf_df = pd.read_csv(self.ccf_meta_file)
        _, _, region_frac_map = region_ccf_cell_types(mfish_ccf_df, region_list)
        return [
            {
                rx: rdf.to_dict(orient="index") for rx, rdf in region_frac_map.items()
            }
        ]


ABC_QUERY_REGISTER = {
    "ABCDbMERFISH_CCFQuery" : ABCDbMERFISH_CCFQuery,
    __name__ + ".ABCDbMERFISH_CCFQuery": ABCDbMERFISH_CCFQuery
}

ABC_XFORM_REGISTER = {}
