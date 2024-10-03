import argparse
import nest



#@synaptic_weight
def weight_function_recurrent(edges, src_nodes, trg_nodes):
    return edges["syn_weight"].values


#@synaptic_weight
def weight_function_bkg(edges, src_nodes, trg_nodes):
    return weight_function_recurrent(edges, src_nodes, trg_nodes)


def main(config_file, output_dir, n_thread):
    # Instantiate SonataNetwork
    sonata_net = nest.SonataNetwork(config_file)

    # Create and connect nodes
    node_collections = sonata_net.BuildNetwork()

    print(node_collections.keys())
    # Connect spike recorder to a population
    s_rec = nest.Create("spike_recorder")
    nest.Connect(node_collections["v1l4"], s_rec)

    # Simulate the network
    sonata_net.Simulate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the pointnet simulation with the given config file."
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        default="./v1l4/output_bkg/",
        help="This option will override the output directory specified in the config file.",
    )
    parser.add_argument(
        "config_file",
        type=str,
        nargs="?",
        default="./v1l4/config_nest.json",
        help="The config file to use for the simulation.",
    )
    parser.add_argument(
        "-n", "--n_thread", type=int, default=1, help="Number of threads to use."
    )
    args = parser.parse_args()

    main(
        args.config_file,
        output_dir=args.output_dir,
        n_thread=args.n_thread,
    )
