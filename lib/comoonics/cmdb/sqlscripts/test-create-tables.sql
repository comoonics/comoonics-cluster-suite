DROP TABLE testjoin;
CREATE TABLE IF NOT EXISTS testjoin (
  name1 char(50) NOT NULL,
  name2 char(50) NOT NULL,
  key1 char(50) NOT NULL,
  key2 char(50) NOT NULL,
  PRIMARY KEY  (name1, name2, key1, key2)
) TYPE=InnoDB;

-- EQUAL
INSERT INTO testjoin VALUES("name1", "name1", "key1", "key1");
INSERT INTO testjoin VALUES("name2", "name1", "key1", "key1");

-- DIFF ONE
INSERT INTO testjoin VALUES("name1", "name2", "key2", "key2");
INSERT INTO testjoin VALUES("name2", "name2", "key2", "key3");

-- DIFF MULT1 (key2)
INSERT INTO testjoin VALUES("name1", "name3", "key2", "key2");
INSERT INTO testjoin VALUES("name1", "name3", "key2", "key3");
INSERT INTO testjoin VALUES("name2", "name3", "key2", "key2");
INSERT INTO testjoin VALUES("name2", "name3", "key2", "key5");

-- DIFF MULT1 (key2)
INSERT INTO testjoin VALUES("name1", "name4", "key3", "key6");
INSERT INTO testjoin VALUES("name1", "name4", "key3", "key7");

INSERT INTO testjoin VALUES("name2", "name4", "key3", "key6");
INSERT INTO testjoin VALUES("name2", "name4", "key3", "key7");
INSERT INTO testjoin VALUES("name2", "name4", "key3", "key8");

-- DIFF MULT1 (key2 other site)
INSERT INTO testjoin VALUES("name1", "name5", "key3", "key6");
INSERT INTO testjoin VALUES("name1", "name5", "key3", "key7");
INSERT INTO testjoin VALUES("name1", "name5", "key3", "key8");

INSERT INTO testjoin VALUES("name2", "name5", "key3", "key6");
INSERT INTO testjoin VALUES("name2", "name5", "key3", "key7");
