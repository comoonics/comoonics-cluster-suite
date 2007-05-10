SELECT rpms0.name AS "name", rpms0.version AS "version_mobilix-01", rpms0.subversion AS "subversion_mobilix-01", rpms0.architecture AS "architecture_mobilix-01",rpms1.version AS "version_localhost.localdomain", rpms1.subversion AS "subversion_localhost.localdomain", rpms1.architecture AS "architecture_localhost.localdomain"
   FROM software_cmdb AS rpms0
     LEFT JOIN   software_cmdb AS rpms1 USING (name, version, subversion, architecture)
       WHERE rpms0.clustername="mobilix-01" AND rpms1.clustername="localhost.localdomain";