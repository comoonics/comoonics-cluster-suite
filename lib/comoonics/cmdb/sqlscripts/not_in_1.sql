SELECT rpms0.name,
       rpms0.version AS version_gfs_node1, rpms0.subversion AS subversion_gfs_node1, rpms0.architecture AS architecture_gfs_node1,
       rpms1.version AS version_mobilix_01, rpms1.subversion AS subversion_mobilix_01, rpms1.architecture AS architecture_mobilix_01,
       "ni" AS version_vmware_cluster, "ni" AS subversion_vmware_cluster, "ni" AS architecture_vmware_cluster
FROM software_cmdb AS rpms0 \
JOIN software_cmdb AS rpms1 USING (name, architecture)
   WHERE rpms0.clustername="gfs-node1" AND rpms1.clustername="mobilix-01" AND \
   (name,architecture) NOT IN (SELECT name, architecture FROM software_cmdb WHERE clustername="vmware_cluster")
   ;