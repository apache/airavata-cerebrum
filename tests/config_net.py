import pandas as pd
import pprint
import json

#
#
import airavata_cerebrum.dataset.abc_mouse as abc_mouse
import airavata_cerebrum.operations.netops as netops
import airavata_cerebrum.model.builder as builder
import airavata_cerebrum.model.structure as structure


LOCATION_CUSTOM_CONFIG = "./net_config/user_location_config.json"
DOWNLOAD_BASE = "../cache/abc_mouse/"


def load_json(file_name):
    with open(file_name) as in_fptr:
        return json.load(in_fptr)


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
    net_model = netops.atlasdata2regionfractions(v1_ei_df, "v1")
    pprint.pp(net_model.model_dump())
    print("----------------------")
    #
    # Update user preference
    net_model = netops.update_user_input(net_model, user_v1_update)
    pprint.pp(net_model.model_dump())
    print("----------------------")
    #
    # NCells
    net_model = netops.fractions2ncells(net_model, 296991)
    pprint.pp(net_model.model_dump())
    print("----------------------")
    #
    #
    net_model = netops.subset_network(net_model, ["VISp1"])
    pprint.pp(net_model.model_dump())
    #
    # Construct model
    bmtk_net = builder.add_nodes_cylinder(net_model)
    bmtk_net.save("output")


if __name__ == "__main__":
    main()
