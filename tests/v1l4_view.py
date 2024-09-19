from ipywidgets.widgets.widget import typing
import traitlets
import types
import ipywidgets as iwidgets
import ipytree as itree
from airavata_cerebrum import base
from airavata_cerebrum.util.desc_config import ModelDescConfigTemplate
from airavata_cerebrum.util import class_qual_name
from airavata_cerebrum.register import find_type


class CfgTreeNode(itree.Node):
    node_key = traitlets.Unicode()


class CTDbCellApiQueryNode(itree.Node):
    node_key = traitlets.Unicode()
    species = traitlets.Unicode()

    @staticmethod
    def source():
        from airavata_cerebrum.dataset.abm_celltypes import CTDbCellApiQuery

        return class_qual_name(CTDbCellApiQuery)


class CTDbGlifApiQueryNode(itree.Node):
    node_key = traitlets.Unicode()
    key = traitlets.Unicode()
    first = traitlets.Bool()

    @staticmethod
    def source():
        from airavata_cerebrum.dataset.abm_celltypes import CTDbGlifApiQuery

        return class_qual_name(CTDbGlifApiQuery)


class ABCDbMERFISH_CCFQueryNode(itree.Node):
    node_key = traitlets.Unicode()
    download_base = traitlets.Unicode()
    region = traitlets.List()

    @staticmethod
    def source():
        from airavata_cerebrum.dataset.abc_mouse import ABCDbMERFISH_CCFQuery

        return class_qual_name(ABCDbMERFISH_CCFQuery)


class AISynPhysQueryNode(itree.Node):
    node_key = traitlets.Unicode()
    download_base = traitlets.Unicode()
    layer = traitlets.List()

    @staticmethod
    def source():
        from airavata_cerebrum.dataset.ai_synphys import AISynPhysQuery

        return class_qual_name(AISynPhysQuery)


class TQDMWrapperNode(itree.Node):
    node_key = traitlets.Unicode()

    @staticmethod
    def source():
        from airavata_cerebrum.operations.xform import TQDMWrapper

        return class_qual_name(TQDMWrapper)


class CTExplainedRatioFilterNode(itree.Node):
    node_key = traitlets.Unicode()
    ratio = traitlets.Float()

    @staticmethod
    def source():
        from airavata_cerebrum.operations.abm_celltypes import CTExplainedRatioFilter

        return class_qual_name(CTExplainedRatioFilter)


class CTPropertyFilterNode(itree.Node):
    node_key = traitlets.Unicode()
    key = traitlets.Unicode()
    region = traitlets.Unicode()
    layer = traitlets.Unicode()
    line = traitlets.Unicode()
    reporter_status = traitlets.Unicode()

    @staticmethod
    def source():
        from airavata_cerebrum.operations.abm_celltypes import CTPropertyFilter

        return class_qual_name(CTPropertyFilter)


class CTModelNameFilterNode(itree.Node):
    node_key = traitlets.Unicode()
    name = traitlets.Unicode()

    @staticmethod
    def source():
        from airavata_cerebrum.operations.abm_celltypes import CTModelNameFilter

        return class_qual_name(CTModelNameFilter)


class ABCDbMERFISH_CCFLayerRegionFilterNode(itree.Node):
    node_key = traitlets.Unicode()
    region = traitlets.Unicode()
    sub_region = traitlets.Unicode()

    @staticmethod
    def source():
        from airavata_cerebrum.operations.abc_mouse import (
            ABCDbMERFISH_CCFLayerRegionFilter,
        )

        return class_qual_name(ABCDbMERFISH_CCFLayerRegionFilter)


class ABCDbMERFISH_CCFFractionFilterNode(itree.Node):
    node_key = traitlets.Unicode()
    region = traitlets.Unicode()
    cell_type = traitlets.Unicode()

    @staticmethod
    def source():
        from airavata_cerebrum.operations.abc_mouse import (
            ABCDbMERFISH_CCFFractionFilter,
        )

        return class_qual_name(ABCDbMERFISH_CCFFractionFilter)


class CTDbNode(itree.Node):
    node_key = traitlets.Unicode()

    @staticmethod
    def source():
        import airavata_cerebrum.dataset.abm_celltypes as abm_ct

        return abm_ct.__name__


class ABCDbMERFISHNode(itree.Node):
    node_key = traitlets.Unicode()

    @staticmethod
    def source():
        import airavata_cerebrum.dataset.abc_mouse as abc_m

        return abc_m.__name__


class AISynPhysNode(itree.Node):
    node_key = traitlets.Unicode()

    @staticmethod
    def source():
        import airavata_cerebrum.dataset.ai_synphys as ai_synphys

        return ai_synphys.__name__


class RootNode(itree.Node):

    @staticmethod
    def source():
        return "root"


class D2MLocationNode(itree.Node):

    @staticmethod
    def source():
        return "d2m_map.location"


class D2MNeuronNode(itree.Node):

    @staticmethod
    def source():
        return "d2m_map.neuron"


class D2MConnectionNode(itree.Node):

    @staticmethod
    def source():
        return "d2m_map.connection"


NODE_CLASSES = [
    RootNode,
    #
    TQDMWrapperNode,
    #
    CTDbNode,
    CTDbGlifApiQueryNode,
    CTDbCellApiQueryNode,
    CTExplainedRatioFilterNode,
    CTPropertyFilterNode,
    CTModelNameFilterNode,
    #
    ABCDbMERFISHNode,
    ABCDbMERFISH_CCFQueryNode,
    ABCDbMERFISH_CCFLayerRegionFilterNode,
    ABCDbMERFISH_CCFFractionFilterNode,
    #
    AISynPhysNode,
    AISynPhysQueryNode,
    #
    D2MLocationNode,
    D2MNeuronNode,
    D2MConnectionNode,
]


CEREBRUM_TREE_NODE_MAP = {}
for clx in NODE_CLASSES:
    CEREBRUM_TREE_NODE_MAP[clx.source()] = clx


NON_QRY_XFORM_CLASSES = [
    RootNode,
    #
    TQDMWrapperNode,
    #
    CTDbNode,
    #
    ABCDbMERFISHNode,
    #
    AISynPhysNode,
]


NON_QRY_XFORM_NODE_MAP = {}
for clx in NON_QRY_XFORM_CLASSES:
    NON_QRY_XFORM_NODE_MAP[clx.source()] = clx


def get_config_tree_node(node_key: str, init_params: typing.Dict) -> itree.Node | None:
    src_class: type[base.DbQuery] | type[base.OpXFormer] | None = find_type(node_key)
    if src_class:
        tnode_class = types.new_class(
            src_class.__name__ + "Node",
            bases=(CfgTreeNode, src_class.trait_type()),
        )
    else:
        if node_key in NON_QRY_XFORM_NODE_MAP:
            tnode_class = NON_QRY_XFORM_NODE_MAP[node_key]
        else:
            return None
    return tnode_class(**init_params)


def get_cfg_tree_node(query_key, query_dict):
    return CEREBRUM_TREE_NODE_MAP[query_key](**query_dict)


class BaseView:
    def __init__(self, **kwargs):
        self.panel = None
        self.widget_map = {}
        self.link_map = {}
        self.links = []

    def clear_links(self):
        for lx in self.links:
            lx.unlink()
        self.links.clear()

    def update(self, new_val):
        self.clear_links()
        if not new_val:
            return
        for slot, widx in self.link_map.items():
            self.links.append(iwidgets.link((new_val, slot), (widx, "value")))

    @staticmethod
    def get_widget(widget_key, **kwargs):
        match widget_key:
            case "float":
                return iwidgets.FloatText(value=kwargs["default"], disabled=False)
            case "text":
                return iwidgets.Text(value=kwargs["default"], disabled=False)
            case "textarea":
                return iwidgets.Textarea(value=kwargs["default"], disabled=False)
            case "option":
                return iwidgets.Dropdown(
                    options=kwargs["options"],
                    disabled=False,
                )
            case "check":
                return iwidgets.Checkbox(
                    value=bool(kwargs["default"]),
                    disabled=False,
                    indent=True,
                )
            case "tags":
                return iwidgets.TagsInput(
                    value=kwargs["default"],
                    allowed_tags=kwargs["allowed"],
                    allowed_duplicates=False,
                )


class QXTemplateView(BaseView):
    def __init__(self, template_map, **kwargs):
        super().__init__(**kwargs)
        for ekey, vmap in template_map["init_params"].items():
            self.widget_map[ekey] = BaseView.get_widget(vmap["type"], **vmap)
        for ekey, vmap in template_map["exec_params"].items():
            self.widget_map[ekey] = BaseView.get_widget(vmap["type"], **vmap)

        self.link_map = self.widget_map
        # Set Widgets
        init_widgets = [iwidgets.Label(" Init Arguments : ")]
        if "init_params" in template_map and template_map["init_params"]:
            init_widgets += [
                self.wrap(kx, wx) for kx, wx in template_map["init_params"].items()
            ]
        else:
            init_widgets[0].value += " N/A "
        exec_widgets = [iwidgets.Label(" Exec Arguments : ")]
        if "exec_params" in template_map and template_map["exec_params"]:
            exec_widgets += [
                self.wrap(kx, wx) for kx, wx in template_map["exec_params"].items()
            ]
        else:
            exec_widgets[0].value += " N/A "
        self.panel = iwidgets.VBox(init_widgets + exec_widgets)

    def wrap(self, widget_key, template_dict):
        return iwidgets.HBox(
            [iwidgets.Label(template_dict["label"] + " :"), self.widget_map[widget_key]]
        )


def get_model_template(
    name="v1l4",
    base_dir="./",
    config_files={"templates": "config_template.json", "config": "config.json"},
    config_dir="./v1l4/description/",
):
    return ModelDescConfigTemplate(name, base_dir, config_files, config_dir)


def source_data_tree(src_data_desc):
    root_node = RootNode(name="Data Base")
    for db_key, db_args in src_data_desc.items():
        query_dict = {"name": db_args["label"], "node_key": db_key}
        dbn_obj = get_cfg_tree_node(db_key, query_dict)
        if not dbn_obj:
            continue
        for wf_step in db_args["db_connect"]["workflow"]:
            step_key = wf_step["name"]
            wf_dict = (
                {
                    "name": wf_step["label"],
                    "node_key": wf_step["name"],
                }
                | wf_step["init_params"]
                | wf_step["exec_params"]
            )
            step_obj = get_cfg_tree_node(step_key, wf_dict)
            dbn_obj.add_node(step_obj)
        for wf_step in db_args["post_ops"]["workflow"]:
            step_key = wf_step["name"]
            wf_dict = (
                {
                    "name": wf_step["label"],
                    "node_key": wf_step["name"],
                }
                | wf_step["init_params"]
                | wf_step["exec_params"]
            )
            step_obj = get_cfg_tree_node(step_key, wf_dict)
            dbn_obj.add_node(step_obj)
        root_node.add_node(dbn_obj)
    tree = itree.Tree(multiple_selection=False)
    tree.add_node(root_node)
    tree.layout.width = "40%"
    return tree


def d2m_map_loc_tree(d2m_map_desc):
    root_node = RootNode(name="Locations")
    for loc_name, loc_desc in d2m_map_desc["locations"].items():
        cfg_obj = get_cfg_tree_node(
            "d2m_map.location", {"name": loc_name, "node_key": "d2m_map.location"}
        )
        if not cfg_obj:
            continue
        for neuron_name, neuron_desc in loc_desc.items():
            neuron_dict = {"name": neuron_name, "node_key": "d2m_map.neuron"}
            neuron_obj = get_cfg_tree_node("d2m_map.neuron", neuron_dict)
            src_data_desc = neuron_desc["source_data"]
            for db_key, db_args in src_data_desc.items():
                dbn_dict = {"name": db_args["label"], "node_key": db_key}
                dbn_obj = get_cfg_tree_node(db_key, dbn_dict)
                if not dbn_obj:
                    continue
                for wf_step in db_args["workflow"]:
                    step_key = wf_step["name"]
                    wf_dict = (
                        {
                            "name": wf_step["label"],
                            "node_key": wf_step["name"],
                        }
                        | wf_step["init_params"]
                        | wf_step["exec_params"]
                    )
                    step_obj = get_cfg_tree_node(step_key, wf_dict)
                    dbn_obj.add_node(step_obj)
                neuron_obj.add_node(dbn_obj)
            cfg_obj.add_node(neuron_obj)
        root_node.add_node(cfg_obj)
    tree = itree.Tree(multiple_selection=False)
    tree.add_node(root_node)
    tree.layout.width = "40%"
    return tree


def d2m_map_connect_tree(d2m_map_desc):
    root_node = RootNode(name="Connections")
    for conn_name, conn_desc in d2m_map_desc["connections"].items():
        conn_obj = get_cfg_tree_node(
            "d2m_map.connection", {"name": conn_name, "node_key": "d2m_map.connection"}
        )
        if not conn_obj:
            continue
        root_node.add_node(conn_obj)
        # TODO
    tree = itree.Tree(multiple_selection=False)
    tree.add_node(root_node)
    tree.layout.width = "40%"
    return tree
