"""

Comoonics cluster configuration package

Provides modules to manage and query the cluster configuration. Discovers type 
of used cluster configuration by parsing given cluster configuration.
"""
import os.path

# needed files
clusterconf = "/etc/cluster/cluster.conf"
clusterdtd = "/opt/atix/comoonics-cs/xml/rh-cluster.dtd"

# xpathes and attribute names
cluster_name = "cluster"
cluster_path = "/cluster"
cluster_name_attribute = "name"
cluster_configversion_attribute = "config_version"

cman_name = "cman"
cman_path = os.path.join(cluster_path,cman_name)
cman_expectedvotes_attribute = "expected_votes"
clusternodes_name = "clusternodes"
clusternodes_path = os.path.join(cluster_path,clusternodes_name)

failoverdomain_name = "failoverdomain"
failoverdomain_path = os.path.join(cluster_path,"rm/failoverdomains",failoverdomain_name)
failoverdomainnode_name = "failoverdomainnode"
failoverdomainnode_path = os.path.join(failoverdomain_path,failoverdomainnode_name)

clusternode_name = "clusternode"
clusternode_path = os.path.join(clusternodes_path,clusternode_name)
clusternode_name_attribute = "name"
clusternode_nodeid_attribute = "nodeid"
clusternode_votes_attribute = "votes"

cominfo_name = "com_info"
cominfo_path = os.path.join(clusternode_path+"%s",cominfo_name)

rootvolume_name = "rootvolume"
rootvolume_path = os.path.join(cominfo_path,rootvolume_name)
rootvolume_name_attribute = "name"
rootvolume_fstype_attribute = "fstype"
rootvolume_mountopts_attribute = "mountopts"
netdev_name = "eth"
netdev_path = os.path.join(cominfo_path,netdev_name)
syslog_name = "syslog"
syslog_path = os.path.join(cominfo_path,syslog_name)
syslog_name_attribute = "name"
scsi_name = "scsi"
scsi_path = os.path.join(cominfo_path,scsi_name)
scsi_failover_attribute = "failover"