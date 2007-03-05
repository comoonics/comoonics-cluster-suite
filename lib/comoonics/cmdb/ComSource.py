"""
Class for the dsl

Methods for filling and getting informations for sources for CMDB
"""
# here is some internal information
# $Id: ComSource.py,v 1.1 2007-03-05 16:10:30 marc Exp $
#

import os
from comoonics.cmdb.ComBaseDB import BaseDB
from comoonics import ComLog
from comoonics.ComSystemInformation import RedhatClusterSystemInformation

class Source(BaseDB):
    """
    Source Class
    """
    log=ComLog.getLogger("Source")

    def __init__(self, **kwds):
        """
        Creates a connection to the database
        __init__(hostname=.., user=.., password=.., database=.., tablename=..)
        __init__(dbhandle=.., tablename=..)
        """
        if not kwds.has_key("tablename"):
            kwds["tablename"]="sources"
        super(Source, self).__init__(**kwds)

    def getSourcesAsSysteminformations(self, name=None):
        sysinfos=list()
        selectquery="SELECT source_type AS type, name, category, architecture, operating_system AS operatingsystem, kernel_version AS kernelversion, uptime, lastimport FROM sources"
        if name and name != "":
            selectquery+=" WHERE name LIKE \"%"+name+"%\";"
        Source.log.debug("getSourcesAsSysteminformations: %s" %(selectquery))
        rs=self.selectQuery(selectquery)
        row=rs.fetch_row(1,1)
        while row:
            from comoonics.ComSystemInformation import SystemInformation
            sysinfos.append(SystemInformation(**row[0]))
            row=rs.fetch_row(1,1)
        return sysinfos

    def getSourceAsSysteminformation(self, name):
        selectquery="SELECT source_type AS type, name, category, architecture, operating_system AS operatingsystem, kernel_version AS kernelversion, uptime, lastimport FROM sources WHERE name=\""+name+"\";"
        rs=self.selectQuery(selectquery)
        if rs.num_rows > 0:
            row=rs.fetch_row(1,1)
            from comoonics.ComSystemInformation import SystemInformation
            systeminformation=SystemInformation(**row[0])
        else:
            return None

    def getCategories(self):
        """
        Returns the first found channel channelversion combination from the dsl of the given rpm
        rpm: is a rpm_header as defined by python-rpm
        """
        selectquery="SELECT DISTINCT category FROM %s;" %(self.tablename)
        self.log.debug("select %s" % selectquery)
        rs=self.selectQuery(selectquery)
        categories=list()
        row=rs.fetch_row()
        while row:
            categories.append(row[0][0])
            row=rs.fetch_row()
        return categories

    def getSourceForCategory(self, category):
        """
        Returns the category for the given sourcename
        """
        selectquery="SELECT DISTINCT name FROM %s WHERE category=\"%s\" LIMIT 1" %(self.tablename, category)
        self.log.debug("select %s" % selectquery)
        rs=self.selectQuery(selectquery)
        categories=list()
        row=rs.fetch_row()
        if len(row)==0:
            return None
        else:
            return row[0][0]

    def updateSystemInformation(self, sysinfo, category):
        values=dict()
        if isinstance(sysinfo, RedhatClusterSystemInformation):
            source_type="cluster"
        else:
            source_type="single"
#        values["uptime"]=sysinfo.getUptime()
#        values["source_type"]=source_type
#        values["category"]=category
#        values["architecture"]=sysinfo.getArchitecture()
#        values["operating_system"]=sysinfo.getOperatingsystem()
#        values["kernel_version"]=sysinfo.getKernelversion()
        return super(Source, self).updateRPM("INSERT INTO %s VALUES(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", NOW());" % (self.tablename, source_type, sysinfo.getName(), category, sysinfo.getArchitecture(), sysinfo.getOperatingsystem(), sysinfo.getKernelversion(), sysinfo.getUptime()),
                      "UPDATE %s SET source_type=\"%s\", category=\"%s\", architecture=\"%s\", operating_system=\"%s\", kernel_version=\"%s\", uptime=\"%s\", lastimport=Now() WHERE name=\"%s\";" % (self.tablename, source_type, category, sysinfo.getArchitecture(), sysinfo.getOperatingsystem(), sysinfo.getKernelversion(), sysinfo.getUptime(), sysinfo.getName()),
                      "SELECT name, source_type, category, architecture, operating_system, kernel_version, uptime FROM %s WHERE name=\"%s\";" %(self.tablename, sysinfo.getName()), values, values.keys())


######################
# $Log: ComSource.py,v $
# Revision 1.1  2007-03-05 16:10:30  marc
# first rpm version
#
# Revision 1.1  2007/02/23 12:42:23  marc
# initial revision
#
