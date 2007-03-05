SELECT name AS name,
       version AS version_gfs_node1, subversion AS subversion_gfs_node1, architecture AS architecture_gfs_node1
FROM software_cmdb WHERE clustername="gfs-node1" AND
   (name, architecture) NOT IN (SELECT name, architecture FROM software_cmdb WHERE clustername="vmware_cluster");                 ;
