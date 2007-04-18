select t1.* from software_cmdb as t1 \
    LEFT JOIN software_cmdb as t2 \
       USING (clustername, name) \
       where t1.clustername="mobilix-01" AND
        (t1.version != t2.version or t1.subversion != t2.subversion or t1.architecture != t2.architecture);