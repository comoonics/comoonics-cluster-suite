SELECT "gfs-node1" AS sourcename,
       master.name AS name,
       master.version AS version_master, master.subversion AS subversion_master, master.architecture AS architecture_master,
       "ni"           AS version_diffs,  "ni"              AS subversion_diffs,  "ni"                AS architecture_diffs
FROM software_cmdb AS master
   WHERE master.clustername="gfs-node1" AND
   (name, architecture) NOT IN (SELECT rpms.name, rpms.architecture FROM software_cmdb AS rpms WHERE clustername="vmware_cluster")
;