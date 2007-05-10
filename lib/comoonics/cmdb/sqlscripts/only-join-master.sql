SELECT rpms.clustername AS sourcename,
       rpms.name AS name,
       master.version AS version_master, master.subversion AS subversion_master, master.architecture AS architecture_master,
       rpms.version AS version_difference, rpms.subversion AS subversion_differences, rpms.architecture AS architecture_differences \
FROM software_cmdb AS master \
JOIN software_cmdb AS rpms USING (name, architecture)
   WHERE (master.version != rpms.version OR master.subversion!=rpms.subversion)
         AND master.clustername="gfs-node1" AND rpms.clustername="vmware_cluster";
         
SELECT rpms.clustername AS sourcename, rpms.name AS name, master.version AS version_master, master.subversion AS subversion_master, master.architecture AS architecture_master, rpms.version AS version_diffs, rpms.subversion AS subversion_diffs, rpms.architecture AS architecture_diffs
        FROM software_cmdb AS master
        INNER JOIN software_cmdb as rpms USING (name, architecture)
        WHERE master.clustername="localhost.localdomain" AND rpms.clustername="mobilix-01"
           AND master.version>=rpms.version AND master.subversion>=rpms.subversion AND
           NOT EXISTS (SELECT * FROM software_cmdb AS rpms1
  LEFT JOIN software_cmdb AS rpms2 USING (name, version, subversion, architecture)
  WHERE rpms1.clustername="localhost.localdomain" AND rpms2.clustername="mobilix-01" AND
      rpms2.name=master.name AND
      rpms2.version=master.version AND
      rpms2.subversion=master.subversion AND
      rpms2.architecture=master.architecture
        )