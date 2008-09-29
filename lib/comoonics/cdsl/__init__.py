"""

Comoonics cdsl package

Provides modules to manage cdsls on filesystem and in inventoryfile. Offers 
functionality to create, manipulate and check cdsls on filesystem/in inventoryfile. 
Discovers needed cdsl type by looking after type of used cluster configuration.
"""

import os.path

#Files
DEFAULT_INVENTORY="/var/lib/cdsl/cdsl_inventory.xml"

#xpathes for elements
cdsls_element = "cdsls"
cdsls_path = "/cdsls"
cdsls_configversion_attribute = "config_version"


cdsl_element = "cdsl"
cdsl_path = os.path.join(cdsls_path,cdsl_element)
cdsl_attribute_src = "src"
cdsl_type_attribute = "type"
cdsl_timestamp_attribute = "timestamp"

defaults_element = "defaults"
defaults_path = os.path.join(cdsls_path,defaults_element)
defaults_cdsltree_attribute = "cdsltree"
defaults_cdsltreeshared_attribute = "cdsltree_shared"
defaults_cdsllink_attribute = "cdsl_link"
defaults_root_attribute = "root"
defaults_mountpoint_attribute = "mountpoint"
defaults_defaultdir_attribute = "default_dir"
defaults_maxnodeidnum_attribute = "maxnodeidnum"
defaults_nodeprefix_attribute = "node_prefix"
defaults_usenodeids_attribute = "use_nodeids"


nodes_element = "nodes"
nodes_path = os.path.join(cdsl_path,nodes_element)

nodesdefault_element = "nodesdefault"
nodesdefault_path = os.path.join(defaults_path,nodesdefault_element)


noderef_element = "noderef"
noderef_path = os.path.join(nodes_path,noderef_element)
noderef_ref_attribute = "ref"

nodedefault_element = "nodes_path"
nodedefault_path = os.path.join(nodesdefault_path,nodedefault_element)
nodedefault_id_attribute = "id"
nodedefault_cdsltree_attribute = "cdsltree"
nodedefault_cdsltree_shared_attribute = "cdsltree_shared"
nodedefault_cdsllink_attribute = "cdsl_link"
nodedefault_root_attribute = "root"
nodedefault_mountpoint_attribute = "mountpoint"
nodedefault_defaultdir_attribute = "default_dir"
nodedefault_maxnodeidnum_attribute = "maxnodeidnum"
nodedefault_nodeprefix_attribute = "node_prefix"
nodedefault_usenodeids_attribute = "use_nodeids"


"""
#define defaultvalues
cdsltree_default = "cluster/cdsl"
cdsltreeShared_default = "cluster/shared"
cdslLink_default = "/cdsl.local"
maxnodeidnum_default = "0"
useNodeids_default = "False"

noderef_path_part = "nodes/noderef/@ref"
"""