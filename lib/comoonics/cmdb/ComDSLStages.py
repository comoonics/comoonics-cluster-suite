"""
Class for the dsl_stages

Methods for filling and getting informations from the definte software library stages table(DSL)
"""
# here is some internal information
# $Id: ComDSLStages.py,v 1.1 2007-02-23 12:42:23 marc Exp $
#

import os
from comoonics.cmdb.ComBaseDB import BaseDB
from comoonics import ComLog

class DSLStages(BaseDB):
    """
    DSLStages Class
    """
    log=ComLog.getLogger("DSLStages")

    def __init__(self, **kwds):
        """
        Creates a connection to the database
        __init__(hostname=.., user=.., password=.., database=.., tablename=..)
        __init__(dbhandle=.., tablename=..)
        """
        if not kwds.has_key("tablename"):
            kwds["tablename"]="dsl_stages"
        super(DSLStages, self).__init__(**kwds)

    def updateRPM(self, rpm, channel, channelversion, stage):
        return super(DSLStages, self).updateRPM("INSERT INTO %s VALUES(\"rpm\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", %s);" % (self.tablename, channel, channelversion, rpm["name"], rpm["version"], rpm["release"], rpm["arch"], stage),
                      "UPDATE %s SET channel=\"%s\", channelversion=\"%s\", name=\"%s\", version=\"%s\", subversion=\"%s\", architecture=\"%s\", stage=%u WHERE name=\"%s\" AND version=\"%s\" AND subversion=\"%s\" AND architecture=\"%s\" AND stage=%u;" % (self.tablename, channel, channelversion, rpm["name"], rpm["version"], rpm["release"], rpm["arch"], stage, rpm["name"], rpm["version"], rpm["release"], rpm["arch"], stage),
                      "SELECT name, version, subversion AS \"release\", architecture AS \"arch\", stage FROM %s WHERE name=\"%s\" AND version=\"%s\" AND subversion=\"%s\" AND architecture=\"%s\" AND stage=%u;" %(self.tablename, rpm["name"], rpm["version"], rpm["release"], rpm["arch"], stage),
                      rpm, ["name", "version", "release", "arch", "stage"], {"stage": stage})

#################
# $Log: ComDSLStages.py,v $
# Revision 1.1  2007-02-23 12:42:23  marc
# initial revision
#
