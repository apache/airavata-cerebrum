import abc
import itertools
import logging
import typing
import types
import ipywidgets as iwidgets
import ipytree as itree
import traitlets

from .. import base
from ..register import find_type
from ..util.desc_config import CfgKeys, ModelDescConfig, ModelDescConfigTemplate


def _log():
    return logging.getLogger(__name__)


class CfgTreeNames:
    SRC_DATA = "Source Data"
    LOCATIONS = "Locations"
    CONNECTIONS = "Connections"


#
# Base class for tree node
class CfgTreeNode(itree.Node):
    node_key = traitlets.Unicode()


# Base class for side panel
class PanelBase:
    def __init__(self, **kwargs):
        self.layout = None
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


class CfgSidePanel(PanelBase):
    def __init__(self, template_map, **kwargs):
        super().__init__(**kwargs)
        for ekey, vmap in template_map["init_params"].items():
            self.widget_map[ekey] = PanelBase.get_widget(vmap["type"], **vmap)
        for ekey, vmap in template_map["exec_params"].items():
            self.widget_map[ekey] = PanelBase.get_widget(vmap["type"], **vmap)

        self.link_map = self.widget_map
        # Set Widgets
        init_widgets = [iwidgets.Label(" Init Arguments : ")]
        if CfgKeys.INIT_PARAMS in template_map and template_map[CfgKeys.INIT_PARAMS]:
            init_widgets += [
                self.wrap(kx, wx)
                for kx, wx in template_map[CfgKeys.INIT_PARAMS].items()
            ]
        else:
            init_widgets[0].value += " N/A "
        exec_widgets = [iwidgets.Label(" Exec Arguments : ")]
        if CfgKeys.EXEC_PARAMS in template_map and template_map[CfgKeys.EXEC_PARAMS]:
            exec_widgets += [
                self.wrap(kx, wx)
                for kx, wx in template_map[CfgKeys.EXEC_PARAMS].items()
            ]
        else:
            exec_widgets[0].value += " N/A "
        self.layout = iwidgets.VBox(init_widgets + exec_widgets)

    def wrap(self, widget_key, twid_dict):
        return iwidgets.HBox(
            [
                iwidgets.Label(twid_dict[CfgKeys.LABEL] + " :"),
                self.widget_map[widget_key],
            ]
        )


class TreeBase(abc.ABC):
    def __init__(
        self,
        md_cfg: ModelDescConfig,
        md_cfg_template: ModelDescConfigTemplate,
        left_width: str,
        **kwargs,
    ):
        self.md_cfg: ModelDescConfig = md_cfg
        self.md_cfg_template: ModelDescConfigTemplate = md_cfg_template
        self.tree: itree.Tree = itree.Tree()
        self.layout: iwidgets.TwoByTwoLayout = iwidgets.TwoByTwoLayout()
        self.panel_keys: typing.Set[str] = set([])
        self.panel_dict: typing.Dict[str, PanelBase] = {}
        self.left_width: str = left_width

    def init_db_node(
        self, db_key: str, db_desc: typing.Dict[str, typing.Any]
    ) -> CfgTreeNode:
        db_node = CfgTreeNode(name=db_desc[CfgKeys.LABEL], node_key=db_key)
        for wf_step in db_desc[CfgKeys.WORKFLOW]:
            db_node.add_node(TreeBase.wflow_step_tree_node(wf_step))
            self.panel_keys.add(wf_step[CfgKeys.NAME])
        return db_node

    def init_side_panels(self) -> typing.Dict[str, PanelBase]:
        _log().info(
            "Start Left-side panel construction for [%s]", str(self.panel_dict.keys())
        )
        for pkey in self.panel_keys:
            _log().debug("Initializing Panels for [%s]", pkey)
            ptemplate = self.md_cfg_template.get_template_for(pkey)
            self.panel_dict[pkey] = CfgSidePanel(ptemplate)
        _log().info("Completed Left-side panel construction")
        return self.panel_dict

    def build(self):
        self.tree = self.init_tree()
        self.panel_dict = self.init_side_panels()
        self.tree.observe(self.tree_update, names="selected_nodes")
        self.layout = iwidgets.TwoByTwoLayout(top_left=self.tree, bottom_right=None)
        return self.layout

    def tree_update(self, change):
        new_val = change["new"]
        if not len(new_val):
            return
        _log().warning("Key : " + new_val[0].node_key)
        node_key = new_val[0].node_key
        if node_key in self.panel_dict:
            _log().warning("Key in Panel ")
            side_panel = self.panel_dict[node_key]
            side_panel.update(new_val[0])
            self.layout.bottom_right = side_panel.layout

    @abc.abstractmethod
    def init_tree(self) -> itree.Tree:
        return itree.Tree()

    @staticmethod
    def type_trait_tree_node(
        register_key: str, init_params: typing.Dict
    ) -> CfgTreeNode | None:
        src_class: type[base.DbQuery] | type[base.OpXFormer] | None = find_type(
            register_key
        )
        if src_class:
            tnode_class = types.new_class(
                src_class.__name__ + "Node",
                bases=(CfgTreeNode, src_class.trait_type()),
            )
            return tnode_class(**init_params)
        elif CfgKeys.NODE_KEY in init_params and CfgKeys.NAME in init_params:
            return CfgTreeNode(**init_params)
        else:
            return None

    @staticmethod
    def wflow_step_tree_node(
        wf_step: typing.Dict[str, typing.Any]
    ) -> CfgTreeNode | None:
        step_key = wf_step[CfgKeys.NAME]
        wf_dict = (
            {
                CfgKeys.NAME: wf_step[CfgKeys.LABEL],
                CfgKeys.NODE_KEY: wf_step[CfgKeys.NAME],
            }
            | wf_step[CfgKeys.INIT_PARAMS]
            | wf_step[CfgKeys.EXEC_PARAMS]
        )
        return TreeBase.type_trait_tree_node(step_key, wf_dict)


class SourceDataTreeView(TreeBase):
    def __init__(
        self,
        md_cfg: ModelDescConfig,
        md_cfg_template: ModelDescConfigTemplate,
        left_width="40%",
        **kwargs,
    ) -> None:
        super().__init__(md_cfg, md_cfg_template, left_width, **kwargs)
        self.src_data_desc = md_cfg.config[CfgKeys.SRC_DATA]

    def init_tree(self) -> itree.Tree:
        root_node = CfgTreeNode(name=CfgTreeNames.SRC_DATA, node_key="root")
        for db_key, db_desc in self.src_data_desc.items():
            db_node = self.init_db_node(
                db_key,
                {
                    CfgKeys.LABEL: db_desc[CfgKeys.LABEL],
                    CfgKeys.WORKFLOW: itertools.chain(
                        db_desc[CfgKeys.DB_CONNECT][CfgKeys.WORKFLOW],
                        db_desc[CfgKeys.POST_OPS][CfgKeys.WORKFLOW],
                    ),
                },
            )
            root_node.add_node(db_node)
        self.tree = itree.Tree(multiple_selection=False)
        self.tree.add_node(root_node)
        self.tree.layout.width = self.left_width
        return self.tree


class D2MLocationsTreeView(TreeBase):
    def __init__(
        self,
        md_cfg: ModelDescConfig,
        md_cfg_template: ModelDescConfigTemplate,
        left_width="40%",
        **kwargs,
    ) -> None:
        super().__init__(md_cfg, md_cfg_template, left_width, **kwargs)
        self.d2m_map_desc = md_cfg.config[CfgKeys.DB2MODEL_MAP]

    def init_neuron_node(
        self, neuron_name: str, neuron_desc: typing.Dict[str, typing.Any]
    ) -> CfgTreeNode:
        neuron_node = CfgTreeNode(name=neuron_name, node_key="d2m_map.neuron")
        for db_key, db_desc in neuron_desc[CfgKeys.SRC_DATA].items():
            neuron_node.add_node(self.init_db_node(db_key, db_desc))
        return neuron_node

    def init_tree(self) -> itree.Tree:
        root_node = CfgTreeNode(name=CfgKeys.LOCATIONS, node_key="root")
        for loc_name, loc_desc in self.d2m_map_desc[CfgKeys.LOCATIONS].items():
            loc_node = CfgTreeNode(name=loc_name, node_key="d2m_map.location")
            for neuron_name, neuron_desc in loc_desc.items():
                neuron_node = self.init_neuron_node(neuron_name, neuron_desc)
                loc_node.add_node(neuron_node)
            root_node.add_node(loc_node)
        self.tree = itree.Tree(multiple_selection=False)
        self.tree.add_node(root_node)
        self.tree.layout.width = self.left_width
        return self.tree


class D2MConnectionsTreeView(TreeBase):
    def __init__(
        self,
        md_cfg: ModelDescConfig,
        md_cfg_template: ModelDescConfigTemplate,
        left_width="40%",
        **kwargs,
    ) -> None:
        super().__init__(md_cfg, md_cfg_template, left_width, **kwargs)
        self.d2m_map_desc = md_cfg.config[CfgKeys.DB2MODEL_MAP]

    def init_conncection_node(
        self, connect_name: str, connect_desc: typing.Dict[str, typing.Any]
    ) -> CfgTreeNode:
        conn_node = CfgTreeNode(name=connect_name, node_key="d2m_map.connection")
        for db_key, db_desc in connect_desc[CfgKeys.SRC_DATA].items():
            db_node = CfgTreeNode(name=db_desc[CfgKeys.LABEL], node_key=db_key)
            for wf_step in db_desc[CfgKeys.WORKFLOW]:
                db_node.add_node(TreeBase.wflow_step_tree_node(wf_step))
            self.panel_keys.union(
                set(wf_step[CfgKeys.NAME] for wf_step in db_desc[CfgKeys.WORKFLOW])
            )
            conn_node.add_node(self.init_db_node(db_key, db_desc))
        return conn_node

    def init_tree(self) -> itree.Tree:
        root_node = CfgTreeNode(name=CfgTreeNames.CONNECTIONS, node_key="tree")
        for conn_name, conn_desc in self.d2m_map_desc[CfgKeys.CONNECTIONS].items():
            root_node.add_node(self.init_conncection_node(conn_name, conn_desc))
        self.tree = itree.Tree(multiple_selection=False)
        self.tree.add_node(root_node)
        self.tree.layout.width = "40%"
        return self.tree
