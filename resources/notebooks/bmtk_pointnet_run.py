import argparse
from bmtk.simulator import pointnet
from bmtk.simulator.pointnet.pyfunction_cache import synaptic_weight
import nest


# try:
#     nest.Install("glifmodule")
# except Exception as e:
#     print("GLIF Module Install Fail", e)
#     pass
# 
# try:
#     nest.Install("glif_psc_double_alpha_module")
# except Exception as e:
#     print("GLIF DOUBLE ALPHA Module Install Fail", e)
#     pass
# 

@synaptic_weight
def weight_function_recurrent(edges, src_nodes, trg_nodes):
    return edges["syn_weight"].values


@synaptic_weight
def weight_function_bkg(edges, src_nodes, trg_nodes):
    return weight_function_recurrent(edges, src_nodes, trg_nodes)


def main(config_file, output_dir, n_thread):
    configure = pointnet.Config.from_json(config_file)
    configure.build_env()
    graph = pointnet.PointNetwork.from_config(configure)
    sim = pointnet.PointSimulator.from_config(configure, graph, n_thread=n_thread)
    sim.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the pointnet simulation with the given config file."
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        default=None,
        help="This option will override the output directory specified in the config file.",
    )
    parser.add_argument(
        "config_file",
        type=str,
        nargs="?",
        default="config.json",
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
