from airavata_cerebrum.util.desc_config import ModelDescConfig
from airavata_cerebrum.util.desc_config import ModelDescConfigTemplate
import airavata_cerebrum.view.tree as cbm_tree

md_config = ModelDescConfig(
    name="v1l4",
    base_dir="./",
    config_files={"config": ["config.json"]},
    config_dir="./v1l4/description/",
)
print("Checking if mandatory config keys exists : ", md_config.valid())

mdtp_config = ModelDescConfigTemplate(
    config_files={"templates": ["config_template.json"]},
    config_dir="./v1l4/description/",
)
print("Config loaded with ", len(mdtp_config.get_templates()), " templates")

# TODO:
src_tree = cbm_tree.SourceDataTreeView(md_config, mdtp_config)
src_tree.build()

loc_tree = cbm_tree.D2MLocationsTreeView(md_config, mdtp_config)
loc_tree.build()

conn_tree = cbm_tree.D2MConnectionsTreeView(md_config, mdtp_config)
conn_tree.build()
