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
from ..model import structure as structure

def _log():
    return logging.getLogger(__name__)


class CfgTreeNames:
    SRC_DATA = "Source Data"
    LOCATIONS = "Locations"
    CONNECTIONS = "Connections"


#
# Base class for tree node
class CBTreeNode(itree.Node):
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
            case "int":
                return iwidgets.IntText(value=kwargs["default"], disabled=False)
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

class StructSidePanel(PanelBase):
    def __init__(self, struct_comp: structure.StructBase, **kwargs):
        super().__init__(**kwargs)
        for ekey, vmap in struct_comp.trait_ui().items():
            self.widget_map[ekey] = PanelBase.get_widget(
                vmap[CfgKeys.TYPE],
                default=vmap["default"],
            )

        self.link_map = self.widget_map
        # Set Widgets
        struct_widgets = [iwidgets.Label(struct_comp.name)]
        struct_widgets += [
            self.wrap(kx, wx)
            for kx, wx in struct_comp.trait_ui().items()
        ]
        self.layout = iwidgets.VBox(struct_widgets)

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
        left_width: str,
        **kwargs,
    ):
        self.tree: itree.Tree = itree.Tree()
        self.layout: iwidgets.TwoByTwoLayout = iwidgets.TwoByTwoLayout()
        self.panel_keys: typing.Set[str] = set([])
        self.panel_dict: typing.Dict[str, PanelBase] = {}
        self.left_width: str = left_width

    @abc.abstractmethod
    def init_tree(self) -> itree.Tree:
        return itree.Tree()
    
    @abc.abstractmethod
    def build(self) -> "TreeBase":
        return None

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

    @staticmethod
    def struct_tree_node(
        struct_obj: structure.StructBase
    ) -> CBTreeNode:
        tnode_class = types.new_class(
            struct_obj.__class__.__name__ + "Node",
            bases=(CBTreeNode, struct_obj.trait_type()),
        )
        return tnode_class(
            node_key=struct_obj.name,
            **struct_obj.model_dump(exclude=struct_obj.exclude())
        )


    @staticmethod
    def type_trait_tree_node(
        register_key: str, init_params: typing.Dict
    ) -> CBTreeNode | None:
        src_class: type[base.DbQuery] | type[base.OpXFormer] | None = find_type(
            register_key
        )
        if src_class:
            tnode_class = types.new_class(
                src_class.__name__ + "Node",
                bases=(CBTreeNode, src_class.trait_type()),
            )
            return tnode_class(**init_params)
        elif CfgKeys.NODE_KEY in init_params and CfgKeys.NAME in init_params:
            return CBTreeNode(**init_params)
        else:
            return None

    @staticmethod
    def wflow_step_tree_node(
        wf_step: typing.Dict[str, typing.Any]
    ) -> CBTreeNode | None:
        step_key = wf_step[CfgKeys.NAME]
        wf_dict = (
            {
                CfgKeys.NAME: wf_step[CfgKeys.LABEL],
                CfgKeys.NODE_KEY: wf_step[CfgKeys.NAME],
            }
            | wf_step[CfgKeys.INIT_PARAMS]
            | wf_step[CfgKeys.EXEC_PARAMS]
        )
        return ConfigTreeBase.type_trait_tree_node(step_key, wf_dict)


class ConfigTreeBase(TreeBase):
    def __init__(
        self,
        md_cfg: ModelDescConfig,
        md_cfg_template: ModelDescConfigTemplate,
        left_width: str,
        **kwargs,
    ):
        super().__init__(left_width, **kwargs)
        self.md_cfg: ModelDescConfig = md_cfg
        self.md_cfg_template: ModelDescConfigTemplate = md_cfg_template

    def init_db_node(
        self, db_key: str, db_desc: typing.Dict[str, typing.Any]
    ) -> CBTreeNode:
        db_node = CBTreeNode(name=db_desc[CfgKeys.LABEL], node_key=db_key)
        for wf_step in db_desc[CfgKeys.WORKFLOW]:
            db_node.add_node(ConfigTreeBase.wflow_step_tree_node(wf_step))
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

    def build(self) -> TreeBase:
        self.tree = self.init_tree()
        self.panel_dict = self.init_side_panels()
        self.tree.observe(self.tree_update, names="selected_nodes")
        self.layout = iwidgets.TwoByTwoLayout(top_left=self.tree, bottom_right=None)
        return self

    @abc.abstractmethod
    def init_tree(self) -> itree.Tree:
        return itree.Tree()


class SourceDataTreeView(ConfigTreeBase):
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
        root_node = CBTreeNode(name=CfgTreeNames.SRC_DATA, node_key="root")
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


class D2MLocationsTreeView(ConfigTreeBase):
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
    ) -> CBTreeNode:
        neuron_node = CBTreeNode(name=neuron_name, node_key="d2m_map.neuron")
        for db_key, db_desc in neuron_desc[CfgKeys.SRC_DATA].items():
            neuron_node.add_node(self.init_db_node(db_key, db_desc))
        return neuron_node

    def init_tree(self) -> itree.Tree:
        root_node = CBTreeNode(name=CfgKeys.LOCATIONS, node_key="root")
        for loc_name, loc_desc in self.d2m_map_desc[CfgKeys.LOCATIONS].items():
            loc_node = CBTreeNode(name=loc_name, node_key="d2m_map.location")
            for neuron_name, neuron_desc in loc_desc.items():
                neuron_node = self.init_neuron_node(neuron_name, neuron_desc)
                loc_node.add_node(neuron_node)
            root_node.add_node(loc_node)
        self.tree = itree.Tree(multiple_selection=False)
        self.tree.add_node(root_node)
        self.tree.layout.width = self.left_width
        return self.tree


class D2MConnectionsTreeView(ConfigTreeBase):
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
    ) -> CBTreeNode:
        conn_node = CBTreeNode(name=connect_name, node_key="d2m_map.connection")
        for db_key, db_desc in connect_desc[CfgKeys.SRC_DATA].items():
            db_node = CBTreeNode(name=db_desc[CfgKeys.LABEL], node_key=db_key)
            for wf_step in db_desc[CfgKeys.WORKFLOW]:
                db_node.add_node(ConfigTreeBase.wflow_step_tree_node(wf_step))
            self.panel_keys.union(
                set(wf_step[CfgKeys.NAME] for wf_step in db_desc[CfgKeys.WORKFLOW])
            )
            conn_node.add_node(self.init_db_node(db_key, db_desc))
        return conn_node

    def init_tree(self) -> itree.Tree:
        root_node = CBTreeNode(name=CfgTreeNames.CONNECTIONS, node_key="tree")
        for conn_name, conn_desc in self.d2m_map_desc[CfgKeys.CONNECTIONS].items():
            root_node.add_node(self.init_conncection_node(conn_name, conn_desc))
        self.tree = itree.Tree(multiple_selection=False)
        self.tree.add_node(root_node)
        self.tree.layout.width = self.left_width
        return self.tree

class NetworkTreeView(TreeBase):
    def __init__(
        self,
        net_struct: structure.Network,
        left_width="40%",
        **kwargs,
    ) -> None:
        super().__init__(left_width, **kwargs)
        self.net_struct = net_struct

    def init_region_side_panels(self, net_region: structure.Region) -> None:
        self.panel_dict[net_region.name] = StructSidePanel(net_region)
        for _, rx_neuron in net_region.neurons.items():
            self.panel_dict[rx_neuron.name] = StructSidePanel(rx_neuron)
            for _, nx_model in rx_neuron.neuron_models.items():
                self.panel_dict[nx_model.name] = StructSidePanel(nx_model)

    def init_conn_side_panels(self, net_connect: structure.Connection) -> None:
        self.panel_dict[net_connect.name] = StructSidePanel(net_connect)
        for _, cx_model in net_connect.connect_models.items():
            self.panel_dict[cx_model.name] = StructSidePanel(cx_model)

    def init_ext_net_side_panels(self, ext_net: structure.ExtNetwork) -> None:
        self.panel_dict[ext_net.name] = StructSidePanel(ext_net)
        for _, net_region in ext_net.locations.items():
            self.init_region_side_panels(net_region)
        for _, net_connect in ext_net.connections.items():
            self.init_conn_side_panels(net_connect)

    def init_side_panels(self) -> typing.Dict[str, PanelBase]:
        _log().info(
            "Start Left-side panel construction for [%s]", str(self.net_struct.name)
        )
        self.panel_dict[self.net_struct.name] = StructSidePanel(self.net_struct)
        #
        for _, net_region in self.net_struct.locations.items():
            self.init_region_side_panels(net_region)
        #
        for _, net_connect in self.net_struct.connections.items():
            self.init_conn_side_panels(net_connect)
        #
        for _, ext_net in self.net_struct.ext_networks.items():
            self.init_ext_net_side_panels(ext_net)
        _log().info("Completed Left-side panel construction")
        return self.panel_dict

    def region_node(self, net_region: structure.Region) -> CBTreeNode:
        region_node = TreeBase.struct_tree_node(net_region)
        for _, rx_neuron in net_region.neurons.items():
            neuron_node = TreeBase.struct_tree_node(rx_neuron)
            for _, nx_model in rx_neuron.neuron_models.items():
                neuron_node.add_node(TreeBase.struct_tree_node(nx_model))
            region_node.add_node(neuron_node)
        return region_node

    def connection_node(self, net_connect: structure.Connection) -> CBTreeNode:
        connect_node = TreeBase.struct_tree_node(net_connect)
        for _, cx_model in net_connect.connect_models.items():
            connect_node.add_node(TreeBase.struct_tree_node(cx_model))
        return connect_node

    def ext_network_node(self, ext_net: structure.ExtNetwork) -> CBTreeNode:
        ext_net_node = TreeBase.struct_tree_node(ext_net)
        location_node = CBTreeNode(node_key=ext_net.name + ".locations", name="Regions")
        for _, net_region in ext_net.locations.items():
            location_node.add_node(self.region_node(net_region))
        ext_net_node.add_node(location_node)
        connect_node = CBTreeNode(node_key=ext_net.name + ".connections", name="Connections")
        for _, net_connect in ext_net.connections.items():
            connect_node.add_node(self.connection_node(net_connect))
        ext_net_node.add_node(connect_node)
        return ext_net_node

    def init_tree(self) -> itree.Tree:
        root_node = TreeBase.struct_tree_node(self.net_struct)
        location_node = CBTreeNode(node_key="net.locations", name="Regions")
        #
        for _, net_region in self.net_struct.locations.items():
            location_node.add_node(self.region_node(net_region))
        root_node.add_node(location_node)
        #
        connect_node = CBTreeNode(node_key="net.connections", name="Connections")
        for _, net_connect in self.net_struct.connections.items():
            connect_node.add_node(self.connection_node(net_connect))
        root_node.add_node(connect_node)
        #
        ext_net_node = CBTreeNode(node_key="net.ext_networks", name="External Networks")
        for _, ext_net in self.net_struct.ext_networks.items():
            ext_net_node.add_node(self.ext_network_node(ext_net))
        root_node.add_node(ext_net_node)
        self.tree = itree.Tree(multiple_selection=False)
        self.tree.add_node(root_node)
        self.tree.layout.width = self.left_width
        return self.tree

    def build(self) -> TreeBase:
        self.tree = self.init_tree()
        self.panel_dict = self.init_side_panels()
        self.tree.observe(self.tree_update, names="selected_nodes")
        self.layout = iwidgets.TwoByTwoLayout(top_left=self.tree, bottom_right=None)
        return self
