SELECT rpms.clustername AS sourcename,
       rpms.name AS name,
       master.version AS version_master, master.subversion AS subversion_master, master.architecture AS architecture_master,
       rpms.version AS version_difference, rpms.subversion AS subversion_differences, rpms.architecture AS architecture_differences \
FROM software_cmdb AS master \
JOIN software_cmdb AS rpms USING (name, architecture)
   WHERE (master.version != rpms.version OR master.subversion!=rpms.subversion)
         AND master.clustername="gfs-node1" AND rpms.clustername="vmware_cluster";