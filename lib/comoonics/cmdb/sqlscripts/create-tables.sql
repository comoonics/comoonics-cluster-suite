-- Create Table scripts
-- $Id: create-tables.sql,v 1.6 2004/09/24 14:56:15 marc Exp $

--
-- $Id: create-tables.sql,v 1.6 2004/09/24 14:56:15 marc Exp $
-- All tables for the hilti open infrastructure database hoi_config

--
-- Table structure for table 'software_cmdb'
--
CREATE TABLE IF NOT EXISTS software_cmdb (
  sw_type ENUM('rpm', 'proprietary', 'deb', 'local') NOT NULL DEFAULT "rpm",
  clustername char(50) NOT NULL,
  channel char(50) NOT NULL,
  channelversion char(50) NOT NULL,
  name char(50) NOT NULL,
  version char(50) NOT NULL,
  subversion char(50) NOT NULL,
  architecture char(50) NOT NULL,
  PRIMARY KEY  (sw_type, clustername, name, architecture)
) TYPE=InnoDB COMMENT='Installed Software on each cluster';

--
-- Table structure for table 'dsl' definite software library
--
CREATE TABLE IF NOT EXISTS dsl (
  sw_type ENUM('rpm', 'proprietary', 'deb', 'local') NOT NULL DEFAULT "rpm",
  channel char(50) NOT NULL,
  channelversion char(50) NOT NULL,
  name char(50) NOT NULL,
  version char(50) NOT NULL,
  subversion char(50) NOT NULL,
  architecture char(50) NOT NULL,
  file text NOT NULL,
  PRIMARY KEY  (sw_type, channel, channelversion, name, version, subversion, architecture)
) TYPE=InnoDB COMMENT='All RPMs on each channel';

--
-- Table structure for mapping software to stages. To track which software is installed at which stage.
--
CREATE TABLE IF NOT EXISTS dsl_stages (
  sw_type ENUM('rpm', 'proprietary', 'deb', 'local') NOT NULL DEFAULT "rpm",
  channel char(50) NOT NULL,
  channelversion char(50) NOT NULL,
  name char(50) NOT NULL,
  version char(50) NOT NULL,
  subversion char(50) NOT NULL,
  architecture char(50) NOT NULL,
  stage int(8) NOT NULL DEFAULT 0,
  PRIMARY KEY  (channel, channelversion, name, version, subversion, architecture, stage)
) TYPE=InnoDB COMMENT='Table structure for mapping software to stages. To track which software is installed at which stage.';

--
-- Table structure for holding informations of servers and clusters (sources).
-- To track categories of servers and types
--
CREATE TABLE IF NOT EXISTS sources (
  source_type ENUM('cluster', 'single', 'none') NOT NULL DEFAULT "cluster",
  name varchar(255) NOT NULL,
  category varchar(255) NOT NULL DEFAULT "unknown",
  architecture varchar(255) NOT NULL,
  operating_system varchar(255) NOT NULL,
  kernel_version varchar(255) NOT NULL,
  uptime varchar(255) NULL,
  lastimport TIMESTAMP( 14 ) ON UPDATE CURRENT_TIMESTAMP NOT NULL,
  PRIMARY KEY (name)
) TYPE=InnoDB COMMENT='Table structure for holding informations of servers and clusters (sources).'

--
-- $Log$