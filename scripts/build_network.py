import pandas as pd
import pprint

#
#
from data import abc_mouse
from operations import netops
from model import builder, regions

USER_V1_UPDATE = regions.Network(
    name="v1",
    dims={"core_radius": 400.0, "radius": 845.0},
    locations={
        "VISp1": regions.Region(
            name="VISp1",
            inh_fraction=1.0,
            dims={"depth_range": [50, 169]},
            neurons={
                "Sst": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.856,
                        "nsyn_lognorm_scale": 2808.682,
                    },
                ),
                "Lamp5": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.856,
                        "nsyn_lognorm_scale": 2808.682,
                    },
                ),
                "Sst-Chodl": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.856,
                        "nsyn_lognorm_scale": 2808.682,
                    },
                ),
                "Pvalb": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.856,
                        "nsyn_lognorm_scale": 2808.682,
                    },
                ),
                "Vip": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.856,
                        "nsyn_lognorm_scale": 2808.682,
                    },
                ),
                "GABA-Other": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.856,
                        "nsyn_lognorm_scale": 2808.682,
                    },
                ),
            },
        ),
        "VISp2/3": regions.Region(
            name="VISp2/3",
            dims={"depth_range": [169, 357]},
            neurons={
                "Sst": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.55,
                        "nsyn_lognorm_scale": 5305.151,
                    },
                ),
                "Lamp5": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.55,
                        "nsyn_lognorm_scale": 5305.151,
                    },
                ),
                "Sst-Chodl": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.55,
                        "nsyn_lognorm_scale": 5305.151,
                    },
                ),
                "Pvalb": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.433,
                        "nsyn_lognorm_scale": 7432.587,
                    },
                ),
                "Vip": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.537,
                        "nsyn_lognorm_scale": 2355.279,
                    },
                ),
                "GABA-Other": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.537,
                        "nsyn_lognorm_scale": 2355.279,
                    },
                ),
                "IT": regions.Neuron(
                    ei="e",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.363,
                        "nsyn_lognorm_scale": 3815.682,
                    },
                ),
            },
        ),
        "VISp4": regions.Region(
            name="VISp4",
            dims={"depth_range": [357, 505]},
            neurons={
                "Sst": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.55,
                        "nsyn_lognorm_scale": 5305.151,
                    },
                ),
                "Lamp5": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.55,
                        "nsyn_lognorm_scale": 5305.151,
                    },
                ),
                "Pvalb": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.433,
                        "nsyn_lognorm_scale": 7432.587,
                    },
                ),
                "Vip": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.537,
                        "nsyn_lognorm_scale": 2355.279,
                    },
                ),
                "GABA-Other": regions.Neuron(
                    ei="i",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.55,
                        "nsyn_lognorm_scale": 5305.151,
                    },
                ),
                "IT": regions.Neuron(
                    ei="e",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.345,
                        "nsyn_lognorm_scale": 2188.765,
                    },
                ),
                "ET": regions.Neuron(
                    ei="e",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.345,
                        "nsyn_lognorm_scale": 2188.765,
                    },
                ),
                "CT": regions.Neuron(
                    ei="e",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.345,
                        "nsyn_lognorm_scale": 2188.765,
                    },
                ),
                "NP": regions.Neuron(
                    ei="e",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.345,
                        "nsyn_lognorm_scale": 2188.765,
                    },
                ),
                "Glut-Other": regions.Neuron(
                    ei="e",
                    fraction=0.0,
                    dims={
                        "nsyn_lognorm_shape": 0.345,
                        "nsyn_lognorm_scale": 2188.765,
                    },
                ),
            },
        ),
        "VISp5": regions.Region(name="VISp5", dims={"depth_range": [505, 665]}),
        "VISp6a": regions.Region(name="VISp6a", dims={"depth_range": [665, 829]}),
        "VISp6b": regions.Region(name="VISp6b", dims={"depth_range": [665, 829]}),
    },
)


def main():
    # Get Ratio from
    v1_ei_df = abc_mouse.region_cell_type_ratios("VISp")
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
    net_model = netops.update_user_input(net_model, USER_V1_UPDATE)
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
