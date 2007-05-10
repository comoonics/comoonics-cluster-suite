SELECT t1.name2, t1.key1, t1.key2, t2.key1, t2.key2
  FROM      testjoin as t1
  LEFT JOIN testjoin as t2
    ON t1.name2=t2.name2 AND t1.key1=t2.key1 AND t1.key2=t2.key2 WHERE t1.name1="name1" AND t2.name1="name2";