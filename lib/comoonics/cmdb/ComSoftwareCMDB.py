"""
Class for the software_cmdb

Methods for comparing systems and the like
"""
# here is some internal information
# $Id: ComSoftwareCMDB.py,v 1.18 2007/05/10 12:14:01 marc Exp $
#

import re
from comoonics.cmdb.ComBaseDB import BaseDB
from comoonics import ComLog
from comoonics.db.ComDBLogger import DBLogger
from ComSource import Source
from Packages import Package, Packages

class SoftwareCMDB(BaseDB):
    """
    Class for the software_cmdb
    """
    NOT_INSTALLED_STRING="not installed"
    SELECT_FOR_SOFTWARE=("channel",
                         "channelversion",
                         "name",
                         "version",
                         "subversion",
                         "architecture",
                         "sw_type")
    COMPARE_2_SOFTWARE=("name",
                        "version",
                        "subversion",
                        "architecture")
    SELECT_FOR_DIFFS_MASTER=("sourcename", "name", "version_master", "subversion_master", "architecture_master", "version_diffs", "subversion_diffs", "architecture_diffs")

    DIFFS_COLNAME="diffs"

    log=ComLog.getLogger("SoftwareCMDB")

    def __init__(self, **kwds):
        """
        Creates a Software CMDB class giving methods to deal with the sql table "software_cmdb"
        __init__(hostname=.., user=.., password=.., database=.., tablename=..)
        __init__(dbhandle=.., tablename=..)
        """
        if not kwds.has_key("tablename"):
            kwds["tablename"]="software_cmdb"
        super(SoftwareCMDB, self).__init__(**kwds)

    def getClusters(self):
        query="SELECT DISTINCT clustername FROM %s" %(self.tablename)
        rs=self.selectQuery(query)
        row=rs.fetch_row()
        clusters=list()
        while row:
            clusters.append(row[0][0])
            row=rs.fetch_row()
        return clusters
   
    def getPackages(self, sourcenames, master, colnames=None, limitup=0, limitdown=0, where=None): 
        """
        Returns a set of differences of the given sourcenamess.
        Parameter are the sourcenames to compare
        """
        if not colnames:
            colnames=list(SoftwareCMDB.COMPARE_2_SOFTWARE)
            colnames.append("clustername")
        if master:
            # Add master to the beginning
            sourcenames.insert(0, master)
        softwarecmdb=self._createSoftwareCMDB(sourcenames, colnames, limitup, limitdown, where)
        return softwarecmdb

    def _createSoftwareCMDB(self, sourcenames, colnames, limitup, limitdown, where):
        softwarecmdb=Packages(sourcenames)
        
        for sourcename in sourcenames:
            sourcesquery=self.selectQueryInstalledRpms(sourcename, colnames, where, limitup, limitdown)
            rs=self.selectQuery(sourcesquery)
            row=rs.fetch_row(1,1)
            while row:
                package=Package(**row[0])
                package.allsources=sourcenames
                softwarecmdb.add(package, sourcename)
                row=rs.fetch_row(1,1)
                
        return softwarecmdb
    
    def selectQueryInstalledRpms(self, sourcename, colnames=COMPARE_2_SOFTWARE, where=None, limitup=0, limitdown=0):
        """
        Returns all installed software on all sourcenames
        """
        table=self.tablename
        if not where:
            where=list()
            where.append("true")
        orwhere=list()
        orwhere.append('clustername="'+sourcename+'"')
        query="SELECT DISTINCT "+", ".join(colnames)+" FROM "+table+\
               "\n   WHERE "+" AND ".join(where) + " AND ("+" OR ".join(orwhere)+")"
        self.log.debug("selectQueryInstalledRpms: %s" %query)
        return query

    def updateRPM(self, _rpm, name, channelname, channelversion, count=1):
        """
        Updates the given rpmheader in the software_cmdb of this cluster
        rpm: the rpm-header defined by python-rpm with extensions like in ComDSL (channelname and -version)
        name: the name of the cluster/system
        count: the amount of rpms found with this name
        """
        insertquery="INSERT INTO %s VALUES(\"rpm\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");" \
                    %(self.tablename, name, channelname, channelversion, _rpm["name"], _rpm["version"], _rpm["release"], _rpm["arch"])
        selectquery="SELECT name, version, subversion AS \"release\", architecture AS \"arch\", channel AS channelname, channelversion FROM %s WHERE clustername=\"%s\" AND name=\"%s\" AND architecture=\"%s\"" \
                    %(self.tablename, name, _rpm["name"], _rpm["arch"])
        updatequery="UPDATE %s SET clustername=\"%s\", channel=\"%s\", channelversion=\"%s\", name=\"%s\", version=\"%s\", subversion=\"%s\", architecture=\"%s\" WHERE clustername=\"%s\" AND name=\"%s\";" \
                    %(self.tablename, name, channelname, channelversion, _rpm["name"], _rpm["version"], _rpm["release"], _rpm["arch"], name, _rpm["name"])
        unequal_list=["version", "release", "channelname", "channelversion"]
        if count > 1:
            selectquery += " AND version=\"%s\" AND subversion=\"%s\"" %(_rpm["version"], _rpm["release"])
            updatequery="UPDATE %s SET clustername=\"%s\", channel=\"%s\", channelversion=\"%s\", name=\"%s\", version=\"%s\", subversion=\"%s\", architecture=\"%s\" WHERE clustername=\"%s\" AND name=\"%s\" AND version=\"%s\";" \
                        %(self.tablename, name, channelname, channelversion, _rpm["name"], _rpm["version"], _rpm["release"], _rpm["arch"], name, _rpm["name"], _rpm["version"])
            unequal_list=["channelname", "channelversion"]
        # ComLog.getLogger().debug("select %s" % selectquery)
        ret=super(SoftwareCMDB, self).updateRPM(insertquery, updatequery, selectquery, _rpm,
                                               unequal_list,
                                               { "channelname": channelname, "channelversion": channelversion})
        self.updateRPMinTMP(_rpm, name, channelname, channelversion)
        if ret==1:
            self.dblog.log(DBLogger.DB_LOG_LEVEL, "Added new software package %s-%s.%s.%s (table: %s)" %(_rpm["name"], _rpm["version"], _rpm["release"], _rpm["arch"], self.tablename))
        elif ret>1:
            self.dblog.log(DBLogger.DB_LOG_LEVEL, "Updated existing software package %s-%s.%s.%s (table: %s)" %(_rpm["name"], _rpm["version"], _rpm["release"], _rpm["arch"], self.tablename))

    def cleanTMP(self, name):
        self._clean(name, self.tablename+"_tmp")
    def clean(self, name):
        self._clean(name, self.tablename)
    
    def _clean(self, name, tablename):
        query="DELETE FROM %s WHERE clustername=\"%s\";" %(tablename, name)
        self.dblog.log(DBLogger.DB_LOG_LEVEL, "Cleaning %s for %s" %(tablename, name))
        self.db.query(query)

    def updateRPMinTMP(self, _rpm, name, channelname, channelversion):
        query="INSERT INTO %s_tmp VALUES(\"rpm\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");" \
                    %(self.tablename, name, channelname, channelversion, _rpm["name"], _rpm["version"], _rpm["release"], _rpm["arch"])
        self.db.query(query)

    def deleteNotInTmp(self, name, names=""):
        _names=""
        if type(names)==list:
            for _name in names:
                _names+=" OR software_cmdb.name=\"%s\"" %(_name)
            if len(names)>0:
                _names=" AND ("+_names[3:]+")"
        else:
            _names="%s" %(names)

        query="""DELETE FROM software_cmdb  WHERE clustername="%s" AND
  (name, version, subversion, architecture)
  NOT IN (SELECT name, version, subversion, architecture FROM software_cmdb_tmp WHERE clustername="%s")
     %s;""" %(name, name, _names)

        self.log.debug("deleteNotInTmp: query: "+query)
        self.db.query(query)

        if self.db.affected_rows() > 0:
            self.dblog.log(DBLogger.DB_LOG_LEVEL, "Deleting old software %u." %(self.db.affected_rows()))

# $Log: ComSoftwareCMDB.py,v $
# Revision 1.18  2007/05/10 12:14:01  marc
# Hilti RPM Control
# - Bugfix for Where-Clause
#
# Revision 1.17  2007/05/10 08:22:47  marc
# Hilti RPM Control
# - fixed ambigous query in getSoftwareDublicates for mysql v3.
#
# Revision 1.16  2007/05/10 07:59:36  marc
# Hilti RPM Control:
# - BZ #46 Fixed
#
# Revision 1.15  2007/04/18 10:17:07  marc
# Hilti RPM Control
# - fixed ambigousness with mysql3 in getDublicateSoftware..
# - removed architecture in in getDublicateSoftware..
#
# Revision 1.14  2007/04/18 07:59:12  marc
# Hilti RPM Control
# - added getSoftwareDublicates
# - added Installed for Categories and Diffs
#
# Revision 1.13  2007/04/12 13:07:15  marc
# Hilti RPM Control
# - added also installed for diffs
#
# Revision 1.12  2007/04/12 12:20:48  marc
# Hilti RPM Control
# - new feature also installed for n:m compares
#
# Revision 1.11  2007/04/12 07:53:05  marc
# Hilti RPM Control
# - Bugfix in changing or adding multiple rpms with same name
#
# Revision 1.10  2007/04/11 11:48:40  marc
# Hilti RPM Control
# - support for multiple RPMs with same name
#
# Revision 1.9  2007/04/02 11:13:34  marc
# For Hilti RPM Control :
# - added MasterCompare
# - some bugfixes
#
# Revision 1.8  2007/03/14 16:51:42  marc
# fixed AND instead of OR in OnlyDiffs Join
#
# Revision 1.7  2007/03/14 15:26:34  marc
# compatible with mysql3 dialect and ambigousness. (RHEL4 has mysql3) (4th)
#
# Revision 1.6  2007/03/14 15:11:37  marc
# compatible with mysql3 dialect and ambigousness. (RHEL4 has mysql3) (3rd)
#
# Revision 1.5  2007/03/14 14:57:21  marc
# compatible with mysql3 dialect and ambigousness. (RHEL4 has mysql3)
#
# Revision 1.4  2007/03/14 14:37:24  marc
# compatible with mysql3 dialect and ambigousness. (RHEL4 has mysql3)
#
# Revision 1.3  2007/03/14 13:16:48  marc
# added support for comparing multiple n>2 sources
#
# Revision 1.2  2007/03/05 16:10:30  marc
# first rpm version
#
# Revision 1.1  2007/02/23 12:42:23  marc
# initial revision
#
