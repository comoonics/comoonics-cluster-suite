"""
Class for the dsl

Methods for filling and getting informations for sources for CMDB
"""
# here is some internal information
# $Id: ComSource.py,v 1.3 2007-04-02 11:16:00 marc Exp $
#

from comoonics.cmdb.ComBaseDB import BaseDB
from comoonics import ComLog
try:
    from comoonics.tools.ComSystemInformation import SystemInformation
except ImportError:
    from comoonics.ComSystemInformation import SystemInformation
from comoonics.db.ComDBLogger import DBLogger

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
        # to be compatible with mysql-python rhel4 and mysql4.1 dateformat it has to be formated
        selectquery="SELECT source_type AS type, name, category, architecture, operating_system AS operatingsystem, "+\
                    "kernel_version AS kernelversion, uptime, DATE_FORMAT(lastimport, '%Y%m%d%H%i%s') AS lastimport FROM sources"
        if name and name != "":
            selectquery+=" WHERE name LIKE \"%"+name+"%\";"
        Source.log.debug("getSourcesAsSysteminformations: %s" %(selectquery))
        rs=self.selectQuery(selectquery)
        row=rs.fetch_row(1,1)
        while row:
            sysinfos.append(SystemInformation(**row[0]))
            row=rs.fetch_row(1,1)
        return sysinfos

    def getSourceAsSysteminformation(self, name):
        selectquery="SELECT source_type AS type, name, category, architecture, operating_system AS operatingsystem, kernel_version AS kernelversion, uptime, lastimport FROM sources WHERE name=\""+name+"\";"
        rs=self.selectQuery(selectquery)
        if rs.num_rows > 0:
            row=rs.fetch_row(1,1)
            return SystemInformation(**row[0])
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

    def getSourcesForCategory(self, category):
        """
        Returns the category for the given sourcename
        """
        selectquery="SELECT DISTINCT name FROM %s WHERE category=\"%s\";" %(self.tablename, category)
        rs=self.selectQuery(selectquery)
        sources=list()
        row=rs.fetch_row()
        while row:
            sources.append(row[0][0])
            row=rs.fetch_row()
        self.log.debug("select %s %u, %u" %(selectquery, rs.num_rows(), len(sources)))
        return sources

    def updateSystemInformation(self, sysinfo, category):
        source_type=sysinfo.getType()
        ret=super(Source, self).updateRPM("INSERT INTO %s VALUES(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", NOW());" % (self.tablename, source_type, sysinfo.getName(), category, sysinfo.getArchitecture(), sysinfo.getOperatingsystem(), sysinfo.getKernelversion(), sysinfo.getUptime()),
                  "UPDATE %s SET source_type=\"%s\", category=\"%s\", architecture=\"%s\", operating_system=\"%s\", kernel_version=\"%s\", uptime=\"%s\", lastimport=Now() WHERE name=\"%s\";" % (self.tablename, source_type, category, sysinfo.getArchitecture(), sysinfo.getOperatingsystem(), sysinfo.getKernelversion(), sysinfo.getUptime(), sysinfo.getName()),
                  "SELECT name, source_type, category, architecture, operating_system, kernel_version, uptime FROM %s WHERE name=\"%s\";" %(self.tablename, sysinfo.getName()), None)
        if ret==1:
            self.dblog.log(DBLogger.DB_LOG_LEVEL, "Added new system %s, %s (table: %s)" %(sysinfo.getName(), category, self.tablename))
        elif ret>1:
            self.dblog.log(DBLogger.DB_LOG_LEVEL, "Updated existing system %s, %s (table: %s)" %(sysinfo.getName(), category, self.tablename))

    def removeSystemInformation(self, sysinfo, category):
        query="DELETE FROM %s WHERE name=\"%s\" AND category=\"%s\" AND architecture=\"%s\" " %(self.tablename, sysinfo.getName(), category, sysinfo.getArchitecture())
        self.log.debug(query)
        self.execQuery(query)

######################
# $Log: ComSource.py,v $
# Revision 1.3  2007-04-02 11:16:00  marc
# For Hilti RPM Control:
# - added DBLogging
# - changed getSourceForCategory to getSourcesForCategory
#
# Revision 1.2  2007/03/06 06:54:15  marc
# be compatible with mysql4.1 and mysql-python on rhel4
#
# Revision 1.1  2007/03/05 16:10:30  marc
# first rpm version
#
# Revision 1.1  2007/02/23 12:42:23  marc
# initial revision
#
