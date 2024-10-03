import pandas as pd
import pprint
import json

#
#
import airavata_cerebrum.dataset.abc_mouse as abc_mouse
import airavata_cerebrum.model.structure as structure
import airavata_cerebrum.model.mousev1 as mousev1


LOCATION_CUSTOM_CONFIG = "./net_config/user_location_config.json"
DOWNLOAD_BASE = "../cache/abc_mouse/"


def load_json(file_name):
    with open(file_name) as in_fptr:
        return json.load(in_fptr)


def atlasdata2regionfractions(
    region_frac_df: pd.DataFrame, model_name: str
) -> structure.Network:
    loc_struct = {}
    for loc, row in region_frac_df.iterrows():
        neuron_struct = {}
        for gx in abc_mouse.GABA_TYPES:
            frac_col = abc_mouse.FRACTION_COLUMN_FMT.format(gx)
            neuron_struct[gx] = structure.Neuron(ei="i", fraction=float(row[frac_col]))
        for gx in abc_mouse.GLUT_TYPES:
            frac_col = abc_mouse.FRACTION_COLUMN_FMT.format(gx)
            neuron_struct[gx] = structure.Neuron(ei="e", fraction=float(row[frac_col]))
        loc_struct[loc] = structure.Region(
            name=str(loc),
            inh_fraction=float(row[abc_mouse.INHIBITORY_FRACTION_COLUMN]),
            region_fraction=float(row[abc_mouse.FRACTION_WI_REGION_COLUMN]),
            neurons=neuron_struct,
        )
    return structure.Network(name=model_name, locations=loc_struct)


def main():
    user_v1_update = structure.Network.model_validate(load_json(LOCATION_CUSTOM_CONFIG))
    # Get Ratio from
    v1_ei_df = abc_mouse.region_cell_type_ratios(DOWNLOAD_BASE, "VISp")
    # v1_ei_df.to_csv("region_test.csv")
    # v1_ei_df = pd.read_csv("region_test.csv", index_col=0)
    pd.set_option("display.max_columns", None)
    print(v1_ei_df)
    print("----------------------")
    #
    # Construt model node fraction struct
    net_model : structure.Network = atlasdata2regionfractions(v1_ei_df, "v1")
    pprint.pp(net_model.model_dump())
    print("----------------------")
    #
    # Update user preference
    net_model.apply_mod(user_v1_update)
    pprint.pp(net_model.model_dump())
    print("----------------------")
    #
    # NCells
    net_model.populate_ncells(296991)
    pprint.pp(net_model.model_dump())
    print("----------------------")
    #
    #
    net_model = structure.subset_network(net_model, ["VISp1"])
    pprint.pp(net_model.model_dump())
    #
    # Construct model
    net_builder = mousev1.V1BMTKNetworkBuilder(net_model)
    bmtk_net = net_builder.build()
    bmtk_net.save("output")


if __name__ == "__main__":
    main()
