"""
Class for the software_cmdb

Methods for comparing systems and the like
"""
# here is some internal information
# $Id: ComSoftwareCMDB.py,v 1.1 2007-02-23 12:42:23 marc Exp $
#

import os
from comoonics.cmdb.ComBaseDB import BaseDB
from comoonics import ComLog

class SoftwareCMDB(BaseDB):
    """
    Class for the software_cmdb
    """
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
                        "architecture",
                        "version",
                        "subversion",
                        "architecture")

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

    def getSoftware(self, clustername, select="*", limitup=0, limitdown=10, where=None):
        if where==None:
            where=list()
        where.append("clustername=\"%s\"" %(clustername))
        print "where: %s" %(where)
        whereclause=self.resolveWhere(where)
        print "whereclause: %s" %(whereclause)
        query="SELECT DISTINCT %s FROM %s %s LIMIT %s,%s" %(", ".join(select), self.tablename, whereclause, limitup, limitdown)
        print "query: %s" %(query)
        return self.selectQuery(query)

    def getDiffsFromSources(self, sourcenames):
        """
        Returns a resultset of differences of the given sourcenames.
        Parameter are the sourcesnames to compare
        RESTRICTION: Right now only the first 2 sourcenames can be compared (SHOULD BE FIXED)
        """
        columns=list()
        notinstalledcolumns=list()
        dbs=list()
        joincolumns=list()
        where=list()
        where2=list()
        for i in range(2):
            formatedname=self.formatToSQLCompat(sourcenames[i])
            columns.append("rpms"+str(i)+".version AS version_"+formatedname+", rpms"+str(i)+".subversion AS subversion_"+\
                           formatedname+", rpms"+str(i)+".architecture AS architecture_"+formatedname)
            notinstalledcolumns.append(columns[0]+', "not installed" AS version_'+formatedname+', "not installed" AS subversion_'+formatedname+',"not installed" AS architecture_'+formatedname)
            dbs.append(self.tablename+" AS rpms"+str(i))
            joincolumns.append( "rpms"+str(i)+".name" )
            where.append("rpms"+str(i)+".clustername=\""+sourcenames[i]+"\"")
            where2.append("rpms"+str(i)+".clustername=\""+sourcenames[i]+"\"")

        query="SELECT "+joincolumns[0]+", "+','.join(columns)+" FROM "+dbs[0]+" LEFT JOIN "+dbs[1]+" ON "+joincolumns[0]+"="+joincolumns[1]
        query+=" WHERE "+where[0]+" AND rpms0.clustername != rpms1.clustername AND (rpms0.version != rpms1.version OR rpms0.subversion != rpms1.subversion)"
#        ComLog.getLogger().debug("query %s" % query)

        query2="SELECT "+joincolumns[0]+", "+notinstalledcolumns[1]+' FROM '+dbs[0]+' WHERE '+where[0]+' AND rpms0.name NOT IN (SELECT name FROM '+dbs[1]+' WHERE '+where[1]+')'
#        ComLog.getLogger().debug("query2 %s" %query2)
        union=query+" UNION "+query2+' ORDER BY version_'+sourcenames[1]+', name;'
        self.log.debug("union: "+union)
        return self.selectQuery(union)

    def updateRPM(self, rpm, name, channelname, channelversion):
        """
        Updates the given rpmheader in the software_cmdb of this cluster
        rpm: the rpm-header defined by python-rpm with extensions like in ComDSL (channelname and -version)
        name: the name of the cluster/system
        """
        insertquery="INSERT INTO %s VALUES(\"rpm\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");" \
                    %(self.tablename, name, channelname, channelversion, rpm["name"], rpm["version"], rpm["release"], rpm["arch"])
        updatequery="UPDATE %s SET clustername=\"%s\", channel=\"%s\", channelversion=\"%s\", name=\"%s\", version=\"%s\", subversion=\"%s\", architecture=\"%s\" WHERE clustername=\"%s\" AND name=\"%s\";" \
                    %(self.tablename, name, channelname, channelversion, rpm["name"], rpm["version"], rpm["release"], rpm["arch"], name, rpm["name"])
        selectquery="SELECT name, version, subversion AS \"release\", architecture AS \"arch\", channel, channelversion FROM %s WHERE clustername=\"%s\" AND name=\"%s\" AND architecture=\"%s\";" \
                    %(self.tablename, name, rpm["name"], rpm["arch"])
        #    ComLog.getLogger().debug("select %s" % selectquery)
        super(SoftwareCMDB, self).updateRPM(insertquery, updatequery, selectquery, rpm,
                                               ["name", "version", "release", "arch", "channelname", "channelversion"],
                                               { "channelname": channelname, "channelversion": channelversion})

def main():
    cmdb=SoftwareCMDB("mysql-server.gallien.atix", "atix", "atix", "atix_cmdb", "software_cmdb")
    for cluster in cmdb.getClusters():
        print cluster

    rs=cmdb.getSoftware("lilr601", SoftwareCMDB.SELECT_FOR_SOFTWARE, 0, 10, ["name LIKE \"%comoonics%\""])
    softwarerow=rs.fetch_row()
    while softwarerow:
        print ",".join(softwarerow[0])
        softwarerow=rs.fetch_row()

    rs=cmdb.getDiffsFromCluster(("lilr201", "lilr202"))
    softwarerow=rs.fetch_row()
    while softwarerow:
        print ",".join(softwarerow[0])
        softwarerow=rs.fetch_row()

if __name__ == '__main__':
    main()

# $Log: ComSoftwareCMDB.py,v $
# Revision 1.1  2007-02-23 12:42:23  marc
# initial revision
#
