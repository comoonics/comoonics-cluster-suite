SELECT rpms0.name AS name,
       rpms0.version AS version_gfs_node1, rpms0.subversion AS subversion_gfs_node1, rpms0.architecture AS architecture_gfs_node1,
       rpms1.version AS version_vmware_cluster, rpms1.subversion AS subversion_vmware_cluster, rpms1.architecture AS architecture_vmware_cluster \
FROM software_cmdb AS rpms0 \
JOIN software_cmdb AS rpms1 USING (name, architecture)
   WHERE (rpms0.version != rpms1.version OR rpms0.subversion!=rpms1.subversion)
         AND rpms0.clustername="gfs-node1" AND rpms1.clustername="vmware_cluster";