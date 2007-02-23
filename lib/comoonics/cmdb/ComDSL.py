"""
Class for the dsl

Methods for filling and getting informations from the definte software library (DSL)
"""
# here is some internal information
# $Id: ComDSL.py,v 1.1 2007-02-23 12:42:23 marc Exp $
#

import os
from comoonics.cmdb.ComBaseDB import BaseDB
from comoonics import ComLog

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

    def updateRPM(self, rpm, rpmfile, channel, channelversion, channeldir):
        return super(DSL, self).updateRPM("INSERT INTO %s VALUES(\"rpm\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s/%s\");" % (self.tablename, channel, channelversion, rpm["name"], rpm["release"], rpm["version"], rpm["arch"], channeldir, rpmfile),
                      "UPDATE %s SET channel=\"%s\", channelversion=\"%s\", name=\"%s\", version=\"%s\", subversion=\"%s\", architecture=\"%s\", file=\"%s/%s\" WHERE name=\"%s\";" % (self.tablename, channel, channelversion, rpm["name"], rpm["release"], rpm["version"], rpm["arch"], channeldir, rpmfile, rpm["name"]),
                      "SELECT name, version, subversion AS \"release\", architecture AS \"arch\" FROM %s WHERE name=\"%s\" AND version=\"%s\" AND subversion=\"%s\" AND architecture=\"%s\";" %(self.tablename, rpm["name"], rpm["release"], rpm["version"], rpm["arch"]),
                      rpm)


######################
# $Log: ComDSL.py,v $
# Revision 1.1  2007-02-23 12:42:23  marc
# initial revision
#
