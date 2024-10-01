import ast
import json
import collections
import parse
import pandas as pd
from airavata_cerebrum.model.structure import Connection, ConnectionModel


def make_connect_model(in_dcx):
    mdict = {}
    src_result = parse.parse("{}{:d}{}", in_dcx["source_label"])
    tgt_result = parse.parse("{}{:d}{}", in_dcx["target_label"])
    if type(src_result) is parse.Result and type(tgt_result) is parse.Result:
        _, source_l, source_name = src_result
        _, target_l, target_name = tgt_result
        mdict["target_model_id"] = str(in_dcx["target_model_id"])
        mdict["name"] = repr(
            (
                (str(source_l), source_name, ""),
                (str(target_l), target_name, str(mdict["target_model_id"])),
            )
        )
        mdict["weight_max"] = float(in_dcx["weight_max"])
        mdict["delay"] = float(in_dcx["delay"])
        prop_map = {}
        for pname in [
            "params_file",
            "PSP_scale_factor",
            "lognorm_shape",
            "lognorm_scale",
            "synphys_mean",
        ]:
            prop_map[pname] = in_dcx[pname]
        mdict["property_map"] = prop_map
        cx_name = repr(((str(source_l), source_name), (str(target_l), target_name)))
        return (cx_name, ConnectionModel.model_validate(mdict))
    else:
        return (None, None)


def make_connect(conn_str, conn_dct, model_lookup):
    presult = parse.parse("{}{:d}{}-{}{:d}{}", conn_str)
    if type(presult) is parse.Result:
        cdict = {}
        pre_ei, pre_layer, pre_name, post_ei, post_layer, post_name = presult
        cdict["pre"] = (str(pre_layer), pre_name)
        cdict["post"] = (str(post_layer), post_name)
        cdict["name"] = repr((cdict["pre"], cdict["post"]))
        conn_dct["pre_ei"] = pre_ei
        conn_dct["post_ei"] = post_ei
        conn_dct["A_literature_src"] = conn_dct["A_literature"]
        cdict["property_map"] = conn_dct
        if model_lookup and cdict["name"] in model_lookup:
            cmodels = model_lookup[cdict["name"]]
            cdict["models"] = {mx.name: mx for mx in cmodels}
        return (cdict["name"], Connection.model_validate(cdict))
    else:
        return (None, None)


def conn_dict(json_file, model_lookup):
    with open(json_file) as ifx:
        jconn_dict = json.load(ifx)
    return dict(make_connect(kv, rx, model_lookup) for kv, rx in jconn_dict.items())


def conn_model_dict(json_file):
    with open(json_file) as ifx:
        jconn_lst = json.load(ifx)
    cmdl_dict = collections.defaultdict(list)
    for rdict in jconn_lst:
        cx_name, connx_mdl = make_connect_model(rdict)
        if cx_name and connx_mdl:
            cmdl_dict[cx_name].append(connx_mdl)
    return cmdl_dict


def build_connections(conn_file, model_file):
    mdxx_dict = conn_model_dict(model_file)
    return conn_dict(conn_file, mdxx_dict)


def v1_main():
    connex = build_connections(
        "./v1/v1_conn_props_April2.json", "./v1/v1_edge_models_April2.json"
    )
    with open("./v1/v1_custom_full.json", "w") as ofx:
        json.dump(connex, ofx)


def bkg_conn_model(m_entry):
    _, lx, neuronx = parse.parse("{}{:d}{}", m_entry["population"])  # type:ignore
    rkeyx = (str(lx), neuronx)
    stgt_mid = str(m_entry["target_model_id"])
    cx_dict = {}
    cx_dict["name"] = repr(((str(lx), neuronx), stgt_mid))
    cx_dict["target_model_id"] = stgt_mid
    cx_dict["dynamics_params"] = m_entry["dynamics_params"]
    cx_dict["property_map"] = {
        "nsyns": m_entry["nsyns"],
        "unitary_PSP": m_entry["unitary_PSP"],
        "syn_weight": m_entry["syn_weight"],
        "target_median_fr": m_entry["target_median_fr"],
        "syn_weight_psp": m_entry["syn_weight_psp"],
    }
    return (rkeyx, cx_dict)


def bkg_connections(
    bkg_weights_file="./bkg_weights_model_l4.csv", out_file="./bkg_conn_net_l4.json"
):
    wdf = pd.read_csv(bkg_weights_file, sep=" ")
    bkg_mdl_lst = wdf.to_dict(orient="records")
    bkg_mx_lst = [bkg_conn_model(x) for x in bkg_mdl_lst]
    bkg_mx_dict = collections.defaultdict(list)
    for kx, vx in bkg_mx_lst:
        bkg_mx_dict[kx].append(vx)
    conn_dict = {
        repr(kb): {
            "name": repr(kb),
            "pre": ("bkg", ""),
            "post": kb,
            "property_map": {"n_conn": 4},
            "connect_models": {vbx["name"]: vbx for vbx in vb},
        }
        for kb, vb in bkg_mx_dict.items()
    }
    with open(out_file, "w") as ofx:
        json.dump(conn_dict, ofx, indent=4)
    return conn_dict


def lgn_conn_model(m_entry):
    _, lx, neuronx = parse.parse("{}{:d}{}", m_entry["population"])  # type:ignore
    rkeyx = (str(lx), neuronx)
    stgt_mid = str(m_entry["target_model_id"])
    cx_dict = {}
    cx_dict["name"] = repr(((str(lx), neuronx), stgt_mid))
    cx_dict["target_model_id"] = stgt_mid
    cx_dict["dynamics_params"] = m_entry["dynamics_params"]
    cx_dict["property_map"] = {
        "unitary_PSP": m_entry["unitary_PSP"],
        "syn_weight": m_entry["syn_weight"],
        "syn_weight_psp": m_entry["syn_weight_psp"],
    }
    return (rkeyx, cx_dict)


def lgn_connections(
    lgn_weights_file="./lgn_weights_model_l4.csv", out_file="./lgn_conn_net_l4.json"
):
    wdf = pd.read_csv(lgn_weights_file, sep=" ")
    lgn_mdl_lst = wdf.to_dict(orient="records")
    lgn_mx_lst = [lgn_conn_model(x) for x in lgn_mdl_lst]
    lgn_mx_dict = collections.defaultdict(list)
    for kx, vx in lgn_mx_lst:
        lgn_mx_dict[kx].append(vx)
    conn_dict = {
        repr(kb): {
            "name": repr(kb),
            "pre": ("lgn", ""),
            "post": kb,
            "property_map": {"n_conn": 4},
            "connect_models": {vbx["name"]: vbx for vbx in vb},
        }
        for kb, vb in lgn_mx_dict.items()
    }
    with open(out_file, "w") as ofx:
        json.dump(conn_dict, ofx, indent=4)
    return conn_dict


def main():
    pass


if __name__ == "__main__":
    main()
