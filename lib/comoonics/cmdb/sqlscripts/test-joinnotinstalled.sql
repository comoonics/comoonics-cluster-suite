SELECT t3.name2, t3.key1, t3.key2, t4.key1, t4.key2
     FROM      testjoin as t3
     LEFT JOIN testjoin as t4   USING (name2,key1,key2)
     WHERE t3.name1="name1" AND t4.name1="name2";
SELECT DISTINCT t4.name2, t3.key1, t3.key2, t4.key1, t4.key2
      FROM      testjoin as t3
      LEFT JOIN testjoin as t4
         USING (name2) WHERE t3.name1="name1" AND t4.name1="name2" AND
         (t3.key1!=t4.key1 or t3.key2!=t4.key2) AND
         NOT EXISTS (SELECT * FROM testjoin AS t2 WHERE t2.name1="name2" AND t2.name2=t3.name2 AND t2.key1=t3.key1 AND t2.key2=t3.key2);
