--SELECT name AS name,
--       version AS version_vmware_cluster, subversion AS subversion_vmware_cluster, architecture AS architecture_vmware_cluster
--FROM software_cmdb WHERE clustername="vmware_cluster" AND
--   (name, architecture) NOT IN (SELECT name, architecture FROM software_cmdb WHERE clustername="gfs-node1");                 ;

-- not installed is spread in two steps
-- First step: only the notinstalled packages are selected (that means x installed on a and x not installed on b and vice versa)
SELECT nirpms0.name AS "name",
      nirpms0.version AS "version_localhost.localdomain", nirpms0.subversion AS "subversion_localhost.localdomain", nirpms0.architecture AS "architecture_localhost.localdomain",
      "not installed" AS "version_mobilix-01", "not installed" AS "subversion_mobilix-01", "not installed" AS "architecture_mobilix-01"
   FROM software_cmdb AS nirpms0
   JOIN software_cmdb AS nirpms1 USING (name, architecture)
   WHERE nirpms0.clustername="localhost.localdomain" AND nirpms1.clustername="mobilix-01"
    AND
      EXISTS
        (SELECT q1nirpms1.name, q1nirpms1.architecture FROM software_cmdb AS q1nirpms1
           WHERE q1nirpms1.clustername=nirpms0.clustername AND
              q1nirpms1.name=nirpms1.name AND q1nirpms1.architecture=nirpms1.architecture)
    AND
      NOT EXISTS
        (SELECT q1nirpms1.name, q1nirpms1.architecture FROM software_cmdb AS q1nirpms1
           WHERE q1nirpms1.clustername=nirpms1.clustername AND
              q1nirpms1.name=nirpms0.name AND q1nirpms1.architecture=nirpms0.architecture)
UNION
SELECT nirpms0.name AS "name",
      "not installed" AS "version_localhost.localdomain", "not installed" AS "subversion_localhost.localdomain", "not installed" AS "architecture_localhost.localdomain",
      nirpms0.version AS "version_mobilix-01", nirpms0.subversion AS "subversion_mobilix-01", nirpms0.architecture AS "architecture_mobilix-01"
   FROM software_cmdb AS nirpms0
   WHERE nirpms0.clustername="mobilix-01"
    AND
      NOT EXISTS
        (SELECT * FROM software_cmdb AS q1nirpms1
           WHERE q1nirpms1.clustername="localhost.localdomain" AND
              q1nirpms1.name=nirpms0.name AND q1nirpms1.architecture=nirpms0.architecture)
    AND
      EXISTS
        (SELECT * FROM software_cmdb AS q1nirpms1
           WHERE q1nirpms1.clustername="mobilix-01" AND
              q1nirpms1.name=nirpms0.name AND q1nirpms1.architecture=nirpms0.architecture);
-- Second step: only the packages are Count is greater then other count
-- (that means x installed on a and x installed on b and count(x) on a > count(x) on b then all notinstalled packages are selected)
SELECT nirpms0.name AS "name",
      "not installed" AS "version_localhost.localdomain", "not installed" AS "subversion_localhost.localdomain", "not installed" AS "architecture_localhost.localdomain",
      nirpms0.version AS "version_mobilix-01", nirpms0.subversion AS "subversion_mobilix-01", nirpms0.architecture AS "architecture_mobilix-01"
   FROM software_cmdb AS nirpms0
   JOIN software_cmdb AS nirpms1 USING (name, architecture)
   WHERE nirpms0.clustername="localhost.localdomain" AND nirpms1.clustername="mobilix-01"
    AND
      EXISTS
        (SELECT * FROM software_cmdb AS q1nirpms1
           WHERE q1nirpms1.clustername=nirpms0.clustername AND
              q1nirpms1.name=nirpms0.name AND q1nirpms1.architecture=nirpms0.architecture AND
              q1nirpms1.version=nirpms1.version AND q1nirpms1.subversion=nirpms1.subversion)
    AND
      NOT EXISTS
        (SELECT * FROM software_cmdb AS q1nirpms1
           WHERE q1nirpms1.clustername=nirpms1.clustername AND
              q1nirpms1.name=nirpms1.name AND q1nirpms1.architecture=nirpms1.architecture AND
              q1nirpms1.version=nirpms0.version AND q1nirpms1.subversion=nirpms0.subversion)
    AND
      (SELECT COUNT(name) FROM software_cmdb WHERE clustername=nirpms0.clustername AND name=nirpms0.name AND architecture=nirpms0.architecture GROUP BY name, architecture) >
      (SELECT COUNT(name) FROM software_cmdb WHERE clustername=nirpms1.clustername AND name=nirpms1.name AND architecture=nirpms1.architecture GROUP BY name, architecture)
GROUP BY nirpms0.version, nirpms0.subversion
UNION
SELECT nirpms0.name AS "name",
      "not installed" AS "version_localhost.localdomain", "not installed" AS "subversion_localhost.localdomain", "not installed" AS "architecture_localhost.localdomain",
      nirpms0.version AS "version_mobilix-01", nirpms0.subversion AS "subversion_mobilix-01", nirpms0.architecture AS "architecture_mobilix-01"
   FROM software_cmdb AS nirpms0
   JOIN software_cmdb AS nirpms1 USING (name, architecture)
   WHERE nirpms0.clustername="mobilix" AND nirpms1.clustername="localhost.localdomain"
    AND
      EXISTS
        (SELECT * FROM software_cmdb AS q1nirpms1
           WHERE q1nirpms1.clustername=nirpms0.clustername AND
              q1nirpms1.name=nirpms0.name AND q1nirpms1.architecture=nirpms0.architecture AND
              q1nirpms1.version=nirpms1.version AND q1nirpms1.subversion=nirpms1.subversion)
    AND
      NOT EXISTS
        (SELECT * FROM software_cmdb AS q1nirpms1
           WHERE q1nirpms1.clustername=nirpms1.clustername AND
              q1nirpms1.name=nirpms1.name AND q1nirpms1.architecture=nirpms1.architecture AND
              q1nirpms1.version=nirpms0.version AND q1nirpms1.subversion=nirpms0.subversion)
    AND
      (SELECT COUNT(name) FROM software_cmdb WHERE clustername=nirpms0.clustername AND name=nirpms0.name AND architecture=nirpms0.architecture GROUP BY name, architecture) >
      (SELECT COUNT(name) FROM software_cmdb WHERE clustername=nirpms1.clustername AND name=nirpms1.name AND architecture=nirpms1.architecture GROUP BY name, architecture)
GROUP BY nirpms0.version, nirpms0.subversion;


SELECT DISTINCT odrpms0.name AS "name", odrpms0.version AS "version_localhost.localdomain", MAX(odrpms0.subversion) AS "subversion_localhost.localdomain", MAX(odrpms0.architecture) AS "architecture_localhost.localdomain",odrpms1.version AS "version_mobilix-01", odrpms1.subversion AS "subversion_mobilix-01", odrpms1.architecture AS "architecture_mobilix-01",odrpms2.version AS "version_mobilix-02", odrpms2.subversion AS "subversion_mobilix-02", odrpms2.architecture AS "architecture_mobilix-02"
 FROM software_cmdb AS odrpms0
 INNER JOIN software_cmdb AS odrpms1 USING (name, architecture)
  INNER JOIN software_cmdb AS odrpms2 USING (name, architecture)
 WHERE odrpms0.clustername="localhost.localdomain" AND odrpms1.clustername="mobilix-01" AND odrpms2.clustername="mobilix-02"
  AND (odrpms0.version!=odrpms1.version OR odrpms0.version!=odrpms2.version OR odrpms1.version!=odrpms2.version OR odrpms0.subversion!=odrpms1.subversion OR odrpms0.subversion!=odrpms2.subversion OR odrpms1.subversion!=odrpms2.subversion)
  AND NOT EXISTS (
    SELECT * FROM software_cmdb AS odrpms3
      LEFT JOIN software_cmdb AS odrpms4 USING (name, architecture, version, subversion)
       LEFT JOIN software_cmdb AS odrpms5 USING (name, architecture, version, subversion)
      WHERE
         odrpms3.clustername="localhost.localdomain" AND
         odrpms3.version=odrpms0.version AND
         odrpms3.subversion=odrpms0.subversion AND
         odrpms4.clustername="mobilix-01" AND
         odrpms4.version=odrpms1.version AND
         odrpms4.subversion=odrpms1.subversion AND
         odrpms5.clustername="mobilix-02" AND
         odrpms5.version=odrpms2.version AND
         odrpms5.subversion=odrpms2.subversion)
  AND (SELECT COUNT(name) FROM software_cmdb AS odrpms6
  WHERE
     (odrpms6.clustername=odrpms0.clustername OR odrpms6.clustername=odrpms1.clustername OR odrpms6.clustername=odrpms2.clustername) AND
     odrpms6.name=odrpms0.name AND
     odrpms6.architecture=odrpms0.architecture GROUP BY name)% 3 = 0
  AND (NOT EXISTS (
    SELECT * FROM software_cmdb AS odrpms6
     WHERE
        odrpms6.clustername=odrpms0.clustername AND
        odrpms6.name=odrpms0.name AND
        odrpms6.architecture=odrpms0.architecture AND
        ((odrpms6.version=odrpms1.version AND odrpms6.subversion=odrpms1.subversion) OR
           (odrpms6.version=odrpms2.version AND odrpms6.subversion=odrpms2.subversion)) )
  OR NOT EXISTS (
    SELECT * FROM software_cmdb AS odrpms7
     WHERE
        odrpms7.clustername=odrpms1.clustername AND
        odrpms7.name=odrpms1.name AND
        odrpms7.architecture=odrpms1.architecture AND
        ((odrpms7.version=odrpms0.version AND odrpms7.subversion=odrpms0.subversion) OR
           (odrpms7.version=odrpms2.version AND odrpms7.subversion=odrpms2.subversion)) )
  OR NOT EXISTS (
    SELECT * FROM software_cmdb AS odrpms8
     WHERE
        odrpms8.clustername=odrpms2.clustername AND
        odrpms8.name=odrpms2.name AND
        odrpms8.architecture=odrpms2.architecture AND
        ((odrpms8.version=odrpms0.version AND odrpms8.subversion=odrpms0.subversion) OR
           (odrpms8.version=odrpms1.version AND odrpms8.subversion=odrpms1.subversion))) )
 GROUP BY odrpms0.version, odrpms0.subversion;
