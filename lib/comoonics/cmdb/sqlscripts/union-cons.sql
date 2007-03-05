SELECT rpms0.name AS name,
       rpms0.version AS version_gfs_node1, rpms0.subversion AS subversion_gfs_node1, rpms0.architecture AS architecture_gfs_node1,
       rpms1.version AS version_vmware_cluster, rpms1.subversion AS subversion_vmware_cluster, rpms1.architecture AS architecture_vmware_cluster
FROM software_cmdb AS rpms0
JOIN software_cmdb AS rpms1 USING (name, architecture)
   WHERE rpms0.version != rpms1.version AND rpms0.subversion!=rpms1.subversion
         AND rpms0.clustername="gfs-node1" AND rpms1.clustername="vmware_cluster"
UNION
SELECT name AS name,
       "not installed" AS version_gfs_node1, "not installed" AS subversion_gfs_node1, "not installed" AS architecture_gfs_node1,
       version AS version_vmware_cluster, subversion AS subversion_vmware_cluster, architecture AS architecture_vmware_cluster
FROM software_cmdb WHERE clustername="vmware_cluster" AND
   (name, architecture) NOT IN (SELECT name, architecture FROM software_cmdb WHERE clustername="gfs-node1")
UNION
SELECT name AS name,
       version AS version_gfs_node1,              subversion AS subversion_gfs_node1,           architecture AS architecture_gfs_node1,
       "not installed" AS version_vmware_cluster, "not installed" AS subversion_vmware_cluster, "not installed" AS architecture_vmware_cluster
FROM software_cmdb WHERE clustername="gfs-node1" AND
   (name, architecture) NOT IN (SELECT name, architecture FROM software_cmdb WHERE clustername="vmware_cluster")
