import collections
import aisynphys
from aisynphys.database import SynphysDatabase
from aisynphys.cell_class import CellClass, classify_cells, classify_pairs
from aisynphys.connectivity import measure_connectivity

from .. import base
from ..util.log.logging import LOGGER

PAIR_SEPARATOR = "~"


class CellClassSelection(
    collections.namedtuple("CellClassSelection", ["layer", "neuron", "criteria"])
):
    @property
    def name(self):
        return self.layer + "-" + self.neuron


CELL_CLASS_SELECT = [
    CellClassSelection(
        "L23", "Pyr", {"dendrite_type": "spiny", "cortical_layer": "2/3"}
    ),
    CellClassSelection("L23", "Pvalb", {"cre_type": "pvalb", "cortical_layer": "2/3"}),
    CellClassSelection("L23", "Sst", {"cre_type": "sst", "cortical_layer": "2/3"}),
    CellClassSelection("L23", "Vip", {"cre_type": "vip", "cortical_layer": "2/3"}),
    CellClassSelection(
        "L4", "Pyr", {"cre_type": ("nr5a1", "rorb"), "cortical_layer": "4"}
    ),
    CellClassSelection("L4", "Pvalb", {"cre_type": "pvalb", "cortical_layer": "4"}),
    CellClassSelection("L4", "Sst", {"cre_type": "sst", "cortical_layer": "4"}),
    CellClassSelection("L4", "Vip", {"cre_type": "vip", "cortical_layer": "4"}),
    CellClassSelection(
        "L5", "ET", {"cre_type": ("sim1", "fam84b"), "cortical_layer": "5"}
    ),
    CellClassSelection("L5", "IT", {"cre_type": "tlx3", "cortical_layer": "5"}),
    CellClassSelection("L5", "Pvalb", {"cre_type": "pvalb", "cortical_layer": "5"}),
    CellClassSelection("L5", "Sst", {"cre_type": "sst", "cortical_layer": "5"}),
    CellClassSelection("L5", "Vip", {"cre_type": "vip", "cortical_layer": "5"}),
    CellClassSelection(
        "L6", "Pyr", {"cre_type": "ntsr1", "cortical_layer": ("6a", "6b")}
    ),
    CellClassSelection(
        "L6", "Pvalb", {"cre_type": "pvalb", "cortical_layer": ("6a", "6b")}
    ),
    CellClassSelection(
        "L6", "Sst", {"cre_type": "sst", "cortical_layer": ("6a", "6b")}
    ),
    CellClassSelection(
        "L6", "Vip", {"cre_type": "vip", "cortical_layer": ("6a", "6b")}
    ),
]

CELL_LAYER_SET = set([x.layer for x in CELL_CLASS_SELECT])
CELL_NEURON_SET = set([x.neuron for x in CELL_CLASS_SELECT])


class AISynPhysQuery:
    def __init__(self, **params):
        """
        Initialize AI SynphysDatabase
        Parameters
        ----------
        download_base : str (Mandatory)
           File location to store the database
        projects : list[str] (optional)
           Run the database

        """
        self.name = __name__ + ".ABCDbMERFISHQuery"
        self.download_base = params["download_base"]
        aisynphys.config.cache_path = self.download_base
        self.sdb = SynphysDatabase.load_current("small")
        self.projects = self.sdb.mouse_projects
        if "projects" in params and params["projects"]:
            self.projects = params["projects"]
        self.qpairs = self.sdb.pair_query(project_name=self.projects).all()

    def select_cell_classes(self, layer_list, neuron_list=None):
        layer_set = CELL_LAYER_SET
        if layer_list:
            layer_set = set(layer_list)
        neuron_set = CELL_NEURON_SET
        if neuron_list:
            neuron_set = set(neuron_list)
        return {
            cselect.name: CellClass(name=cselect.name, **cselect.criteria)
            for cselect in CELL_CLASS_SELECT
            if (cselect.layer in layer_set) and (cselect.neuron in neuron_set)
        }

    def run(self, in_stream, **params):
        """
        Get the connectivity probabilities for given layter

        Parameters
        ----------
        run_params: dict with the following keys:
            layer : List[str]
             list of layers of interest
        Returns
        -------
        dict of elements for each sub-regio:
        {
            subr 1 : {}
        }
        """
        #
        default_args = {}
        rarg = {**default_args, **params} if params is not None else default_args
        LOGGER.info("AISynPhysQuery Args : %s", rarg)
        layer_list = rarg["layer"]
        cell_classes = self.select_cell_classes(layer_list)
        cell_groups = classify_cells(cell_classes.values(), pairs=self.qpairs)
        pair_groups = classify_pairs(self.qpairs, cell_groups)
        results = measure_connectivity(
            pair_groups, sigma=100e-6, dist_measure="lateral_distance"
        )
        LOGGER.info("AISynPhysQuery Args : %s", rarg)
        #
        return [
            {
                repr(
                    (
                        x[0].name,
                        x[1].name,
                    )
                ): y["adjusted_connectivity"][0]
                for x, y in results.items()
            }
        ]


#
#  ----- Registers and Filters ---
base.DbQuery.register(AISynPhysQuery)


def query_register():
    return [
        AISynPhysQuery,
    ]


def xform_register():
    return []
