SELECT t3.name2, t3.key1, t3.key2, t4.key1, t4.key2
  FROM      testjoin as t3
  INNER JOIN testjoin as t4
  USING (name2)
     WHERE t3.name1="name1" AND t4.name1="name2" AND t4.key2>=t3.key2 AND t4.key1>=t3.key1 AND
        NOT EXISTS (SELECT *
                      FROM      testjoin as t1
                      LEFT JOIN testjoin as t2
                        ON t1.name2=t2.name2 AND t1.key1=t2.key1 AND t1.key2=t2.key2
                           WHERE t1.name1="name1" AND t2.name1="name2" AND t1.name2=t3.name2 AND t1.key1=t3.key1 AND t1.key2=t3.key2);
