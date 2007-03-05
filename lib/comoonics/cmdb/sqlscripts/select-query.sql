SELECT rpms0.name AS name, rpms0.version AS version_development, rpms0.subversion AS subversion_development, rpms0.architecture AS architecture_development,rpms1.version AS version_production, rpms1.subversion AS subversion_production, rpms1.architecture AS architecture_production \
FROM software_cmdb AS rpms0 \
LEFT JOIN software_cmdb AS rpms1 ON rpms0.name=rpms1.name \
   WHERE rpms0.clustername="gfs-node1" AND rpms0.clustername != rpms1.clustername AND \
      (rpms0.version != rpms1.version OR rpms0.subversion != rpms1.subversion)