"""
Class for the dsl

Methods for filling and getting informations from the definte software library (DSL)
"""
# here is some internal information
# $Id: ComDSL.py,v 1.2 2007-04-02 11:16:41 marc Exp $
#

import os
from comoonics.cmdb.ComBaseDB import BaseDB
from comoonics import ComLog
from comoonics.db.ComDBLogger import DBLogger

class DSL(BaseDB):
    """
    DSL Class
    """
    log=ComLog.getLogger("DSL")

    def __init__(self, **kwds):
        """
        Creates a connection to the database
        __init__(hostname=.., user=.., password=.., database=.., tablename=..)
        __init__(dbhandle=.., tablename=..)
        """
        if not kwds.has_key("tablename"):
            kwds["tablename"]="dsl"
        super(DSL, self).__init__(**kwds)

    def getChannelVersion(self, rpm):
        """
        Returns the first found channel channelversion combination from the dsl of the given rpm
        rpm: is a rpm_header as defined by python-rpm
        """
        selectquery="SELECT channel, channelversion FROM %s WHERE name=\"%s\" AND version=\"%s\" AND subversion=\"%s\" AND architecture=\"%s\";" %(self.tablename, rpm[0], rpm[1], rpm[2], rpm[3])
        #    ComLog.getLogger().debug("select %s" % selectquery)
        rs=self.selectQuery(selectquery)
        rows=rs.fetch_row()
        if len(rows) > 0:
            return rows[0]
        else:
            return ("unknownchannel", "noversion")

    def updateRPM(self, _rpm, rpmfile, channel, channelversion, channeldir):
        ret=super(DSL, self).updateRPM("INSERT INTO %s VALUES(\"rpm\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s/%s\");" % (self.tablename, channel, channelversion, _rpm["name"], _rpm["release"], _rpm["version"], _rpm["arch"], channeldir, rpmfile),
                  "UPDATE %s SET channel=\"%s\", channelversion=\"%s\", name=\"%s\", version=\"%s\", subversion=\"%s\", architecture=\"%s\", file=\"%s/%s\" WHERE name=\"%s\";" % (self.tablename, channel, channelversion, _rpm["name"], _rpm["release"], _rpm["version"], _rpm["arch"], channeldir, rpmfile, _rpm["name"]),
                  "SELECT name, version, subversion AS \"release\", architecture AS \"arch\" FROM %s WHERE name=\"%s\" AND version=\"%s\" AND subversion=\"%s\" AND architecture=\"%s\";" %(self.tablename, _rpm["name"], _rpm["release"], _rpm["version"], _rpm["arch"]),
                   _rpm)
        if ret==1:
            self.dblog.log(DBLogger.DB_LOG_LEVEL, "Added new software package %s-%s.%s.%s to channel %s, %s (table: %s)" %(_rpm["name"], _rpm["version"], _rpm["release"], _rpm["arch"], channel, channelversion, self.tablename))
        elif ret>1:
            self.dblog.log(DBLogger.DB_LOG_LEVEL, "Updated existing software package %s-%s.%s.%s in channel %s, %s (table: %s)" %(_rpm["name"], _rpm["version"], _rpm["release"], _rpm["arch"], channel, channelversion, self.tablename))


######################
# $Log: ComDSL.py,v $
# Revision 1.2  2007-04-02 11:16:41  marc
# For Hilti RPM Control:
# - added DBLogging
#
# Revision 1.1  2007/02/23 12:42:23  marc
# initial revision
#
