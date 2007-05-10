--SELECT rpms0.name AS name,
--      rpms0.version AS "version_localhost.localdomain", rpms0.subversion AS "subversion_localhost.localdomain", rpms0.architecture AS "architecture_localhost.localdomain",
--       rpms1.version AS "version_mobilix-01", rpms1.subversion AS "subversion_mobilix-01", rpms1.architecture AS "architecture_mobilix-01" \
--FROM software_cmdb AS rpms0 \
--JOIN software_cmdb AS rpms1 USING (name, version, subversion, architecture)
--   WHERE rpms0.clustername="localhost.localdomain" AND rpms1.clustername="mobilix-01";

-- All but dublicates
-- First  NOT EXISTS filters all equal already installed packages out
SELECT DISTINCT rpms0.name AS "name", MAX(rpms0.version) AS "version_mobilix-01", MAX(rpms0.subversion) AS "subversion_mobilix-01", rpms0.architecture AS "architecture_mobilix-01",rpms1.version AS "version_localhost.localdomain", rpms1.subversion AS "subversion_localhost.localdomain", rpms1.architecture AS "architecture_localhost.localdomain"
 FROM software_cmdb AS rpms0
 INNER JOIN software_cmdb AS rpms1 USING (name, architecture)
 WHERE rpms0.clustername ="localhost.localdomain"
    AND rpms1.clustername="mobilix-01"
    AND (rpms0.version!=rpms1.version OR rpms0.subversion!=rpms1.subversion) AND
       (NOT EXISTS (SELECT * FROM software_cmdb AS rpms2
                     LEFT JOIN   software_cmdb AS rpms3 USING (name, version, subversion, architecture)
                     WHERE rpms2.clustername="localhost.localdomain" AND rpms3.clustername="mobilix-01" AND
                      rpms2.name=rpms0.name AND
                      rpms2.version=rpms0.version AND rpms2.subversion=rpms0.subversion AND
                      rpms3.version=rpms1.version AND rpms3.subversion=rpms1.subversion AND
                      rpms2.architecture=rpms0.architecture)
)
GROUP BY rpms0.version, rpms0.subversion;

-- Order right left
SELECT DISTINCT rpms0.name AS "name", MAX(rpms0.version) AS "version_mobilix-01", MAX(rpms0.subversion) AS "subversion_mobilix-01", rpms0.architecture AS "architecture_mobilix-01",rpms1.version AS "version_localhost.localdomain", rpms1.subversion AS "subversion_localhost.localdomain", rpms1.architecture AS "architecture_localhost.localdomain"
 FROM software_cmdb AS rpms0
 INNER JOIN software_cmdb AS rpms1 USING (name, architecture)
 WHERE rpms0.clustername ="mobilix-01"
    AND rpms1.clustername="localhost.localdomain"
    AND (rpms0.version!=rpms1.version OR rpms0.subversion!=rpms1.subversion) AND
       (NOT EXISTS (SELECT * FROM software_cmdb AS rpms2
                     LEFT JOIN   software_cmdb AS rpms3 USING (name, version, subversion, architecture)
                     WHERE rpms2.clustername="mobilix-01" AND rpms3.clustername="localhost.localdomain" AND
                      rpms2.name=rpms0.name AND
                      rpms2.version=rpms0.version AND rpms2.subversion=rpms0.subversion AND
                      rpms2.architecture=rpms0.architecture)
)
GROUP BY rpms0.version, rpms0.subversion;

-- All and no dublicates
-- First  NOT EXISTS filters all equal already installed packages out
SELECT DISTINCT rpms0.name AS "name", MAX(rpms0.version) AS "version_mobilix-01", MAX(rpms0.subversion) AS "subversion_mobilix-01", rpms0.architecture AS "architecture_mobilix-01",rpms1.version AS "version_localhost.localdomain", rpms1.subversion AS "subversion_localhost.localdomain", rpms1.architecture AS "architecture_localhost.localdomain"
 FROM software_cmdb AS rpms0
 JOIN software_cmdb AS rpms1 USING (name, architecture)
 WHERE rpms0.clustername ="localhost.localdomain"
    AND rpms1.clustername="mobilix-01"
    AND (rpms0.version!=rpms1.version OR rpms0.subversion!=rpms1.subversion) AND
       (NOT EXISTS (SELECT * FROM software_cmdb AS rpms2
                     LEFT JOIN   software_cmdb AS rpms3 USING (name, version, subversion, architecture)
                     WHERE rpms2.clustername="localhost.localdomain" AND rpms3.clustername="mobilix-01" AND
                      rpms2.name=rpms0.name AND
                      rpms2.version=rpms0.version AND rpms2.subversion=rpms0.subversion AND
                      rpms3.version=rpms1.version AND rpms3.subversion=rpms1.subversion AND
                      rpms2.architecture=rpms0.architecture)
    AND
       (NOT EXISTS (SELECT * FROM software_cmdb AS rpms4 WHERE clustername="localhost.localdomain" AND
                      rpms4.name=rpms0.name AND rpms4.architecture=rpms0.architecture AND
                      rpms4.version=rpms1.version AND rpms4.subversion=rpms1.subversion))
    AND
       (NOT EXISTS (SELECT * FROM software_cmdb AS rpms4 WHERE clustername="mobilix-01" AND
                      rpms4.name=rpms0.name AND rpms4.architecture=rpms0.architecture AND
                      rpms4.version=rpms0.version AND rpms4.subversion=rpms0.subversion))
)
GROUP BY rpms0.version, rpms0.subversion;

-- New try.
SELECT DISTINCT t1.name, MAX(t1.version), MAX(t1.subversion), t2.version, t2.subversion FROM software_cmdb AS t1  JOIN software_cmdb AS t2 USING(name, architecture) WHERE t1.clustername="localhost.localdomain" AND t2.clustername="mobilix-01" AND (t1.version!=t2.version OR t1.subversion != t2.subversion) GROUP BY t1.version, t1.subversion;
