SELECT name AS name,
       version AS version_vmware_cluster, subversion AS subversion_vmware_cluster, architecture AS architecture_vmware_cluster
FROM software_cmdb WHERE clustername="vmware_cluster" AND
   (name, architecture) NOT IN (SELECT name, architecture FROM software_cmdb WHERE clustername="gfs-node1");                 ;
