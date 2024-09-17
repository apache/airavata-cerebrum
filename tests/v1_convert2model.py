import json
import collections
import parse
from airavata_cerebrum.model.structure import Connection, ConnectionModel


def make_connect_model(in_dcx):
    mdict = {}
    src_result = parse.parse("{}{:d}{}", in_dcx["source_label"])
    tgt_result = parse.parse("{}{:d}{}", in_dcx["target_label"])
    if type(src_result) is parse.Result and type(tgt_result) is parse.Result:
        _, source_l, source_name = src_result
        _, target_l, target_name = tgt_result
        mdict["target_model_id"] = str(in_dcx["target_model_id"])
        mdict["name"] = repr(((str(source_l), source_name, ""),
                              (str(target_l), target_name, str(mdict["target_model_id"]))))
        mdict["weight_max"] = float(in_dcx["weight_max"])
        mdict["delay"] = float(in_dcx["delay"])
        prop_map = {}
        for pname in ["params_file", "PSP_scale_factor", "lognorm_shape", "lognorm_scale", "synphys_mean"]:
            prop_map[pname] = in_dcx[pname]
        mdict["property_map"] = prop_map
        cx_name = repr(((str(source_l), source_name),
                        (str(target_l), target_name)))
        return (cx_name, ConnectionModel.model_validate(mdict))
    else:
        return (None, None)


def make_connect(conn_str, conn_dct, model_lookup):
    presult = parse.parse(
        "{}{:d}{}-{}{:d}{}", conn_str
    )
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
            cdict["models"] = {mx.name : mx for mx in cmodels}
        return (cdict["name"], Connection.model_validate(cdict))
    else:
        return (None, None)


def conn_dict(json_file, model_lookup):
    with open(json_file) as ifx:
        jconn_dict = json.load(ifx)
    return dict(
        make_connect(kv, rx, model_lookup) for kv, rx in jconn_dict.items()
    )


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


def main():
    connex = build_connections(
        "./v1/v1_conn_props_April2.json",
        "./v1/v1_edge_models_April2.json"
    )
    with open("./v1/v1_custom_full.json", "w") as ofx:
        json.dump(connex, ofx)


if __name__ == "__main__":
    main()
