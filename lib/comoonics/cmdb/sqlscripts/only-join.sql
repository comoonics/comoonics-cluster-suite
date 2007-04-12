SELECT rpms0.name AS name,
       rpms0.version AS "version_localhost.localdomain", rpms0.subversion AS "subversion_localhost.localdomain", rpms0.architecture AS "architecture_localhost.localdomain",
       rpms1.version AS "version_mobilix-01", rpms1.subversion AS "subversion_mobilix-01", rpms1.architecture AS "architecture_mobilix-01" \
FROM software_cmdb AS rpms0 \
JOIN software_cmdb AS rpms1 USING (name, version, subversion, architecture)
   WHERE rpms0.clustername="localhost.localdomain" AND rpms1.clustername="mobilix-01";