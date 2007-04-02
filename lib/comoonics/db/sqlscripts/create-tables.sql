-- Create Table scripts
-- $Id: create-tables.sql,v 1.6 2004/09/24 14:56:15 marc Exp $

--
-- $Id: create-tables.sql,v 1.6 2004/09/24 14:56:15 marc Exp $
-- All tables for the hilti open infrastructure database hoi_config

--
-- Table structure for table 'software_cmdb'
--
CREATE TABLE IF NOT EXISTS logs (
  logid int(8) NOT NULL AUTO_INCREMENT,
  name varchar(255) NOT NULL,
  logsource varchar(255) NOT NULL,
  logtimestamp timestamp(14) NOT NULL DEFAULT NOW(),
  loglevel int(8) NOT NULL,
  logpathname varchar(255) NOT NULL,
  loglineno int(8),
  logmsg text NOT NULL,
  logexecinfo text,
  PRIMARY KEY  (logid)
) TYPE=InnoDB COMMENT='Pythonlog compatible logmessages';

--
-- $Log:$