"""
Class for the software_cmdb

Methods for comparing systems and the like
"""
# here is some internal information
# $Id: ComSoftwareCMDB.py,v 1.2 2007-03-05 16:10:30 marc Exp $
#

import os
from comoonics.cmdb.ComBaseDB import BaseDB
from comoonics import ComLog

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

    def getSoftwareForCategory(self, category, select="*", limitup=0, limitdown=0, where=None, orderby=None):
        from ComSource import Source
        source=Source(dbhandle=self.db)
        sname=source.getSourceForCategory(category)
        return self.getSoftware(sname, select, limitup, limitdown, where)

    def getSoftware(self, clustername, select="*", limitup=0, limitdown=0, where=None, orderby=None):
        if where==None:
            where=list()
        limit=BaseDB.getLimit(limitup, limitdown)
        where.append("clustername=\"%s\"" %(clustername))
        self.log.debug("where: %s" %(where))
        whereclause=BaseDB.resolveWhere(where)
        orderbyclause=BaseDB.resolveOrderBy(orderby)
        self.log.debug("whereclause: %s" %(whereclause))
        query="SELECT DISTINCT %s FROM %s %s %s %s;" %(", ".join(select), self.tablename, whereclause, orderbyclause, limit)
        self.log.debug("query: %s" %(query))
        return self.selectQuery(query)

    def getColnamesForDiff(sourcenames):
        colnames=list()
        colnames.append(SoftwareCMDB.COMPARE_2_SOFTWARE[0])
        for sourcename in sourcenames:
            for colname in SoftwareCMDB.COMPARE_2_SOFTWARE[1:]:
                colnames.append(colname+"_"+BaseDB.formatToSQLCompat(sourcename))
        return colnames
    getColnamesForDiff=staticmethod(getColnamesForDiff)

    def getDiffsFromSources(self, sourcenames, colnames=None, limitup=0, limitdown=0, orderby=None, Diffs=True, NotInstalled=True):
        """
        Returns a resultset of differences of the given sourcenames.
        Parameter are the sourcesnames to compare
        RESTRICTION: Right now only the first 2 sourcenames can be compared (SHOULD BE FIXED)
        """
        orderbyclause=BaseDB.resolveOrderBy(orderby)
        limit=BaseDB.getLimit(limitup, limitdown)
        self.log.debug("orderbyclause: %s, limit: %s" %(orderbyclause, limit))
        if not colnames:
            self.log.debug("getting colnames")
            colnames=self.getColnamesForDiff(sourcenames)
        j=0
#        ComLog.getLogger().debug("query %s" % query)
        queries=list()
        if Diffs:
            queries.append(self.selectQueryOnlyDiffs(sourcenames, colnames))

        if NotInstalled:
            queries+=self.selectQueriesNotInstalled(sourcenames, colnames)
        union="\n UNION \n".join(queries)+orderbyclause+" "+limit+";"
        self.log.debug("union: "+union)
        return self.selectQuery(union)

    def selectQueriesNotInstalled(self, sourcenames, colnames):
        queries=list()
        revnames=list(sourcenames)
        revnames.reverse()
        NOTINSTALLED_COL="\""+SoftwareCMDB.NOT_INSTALLED_STRING+"\" AS "
        index=(len(colnames)-1)/len(sourcenames)
        querycolumns=self.getAllColnamesNotInstalled(colnames[1:], SoftwareCMDB.COMPARE_2_SOFTWARE[1:], sourcenames)
        self.log.debug("querycolumns: %s" %(querycolumns))
        for i in range(len(sourcenames)):
            self.log.debug("selectQueriesNotInstalled : %s, next_index: %u"%(querycolumns[i], (i+1)%len(sourcenames)))
            queries.append("SELECT name, "+querycolumns[i]+" FROM "+self.tablename+" AS rpms"+str(i)+\
                  " WHERE rpms"+str(i)+".clustername=\""+sourcenames[i]+"\" "+\
                  " AND (name, architecture) NOT IN (SELECT name, architecture FROM "+self.tablename+\
                  " WHERE clustername=\""+sourcenames[(i+1)%len(sourcenames)]+"\")")
        return queries

    def getAllColnamesNotInstalled(self, colnames, colparts, sourcenames):
         ret_colnames=list()
         ilen=len(sourcenames)
         jlen=len(colnames)
         klen=len(colparts)
#         self.log.debug("ilen: %u, jlen: %u, klen: %u" %(ilen, jlen, klen))
         basecolnames=list(colnames)
         for i in range(ilen):
             copy_colnames=""
             for j in range(jlen):
                 if j>=klen*i and j<klen*(i+1):
                     copy_colnames+="\""+SoftwareCMDB.NOT_INSTALLED_STRING+"\" AS "+colnames[j]+", "
                 else:
                     copy_colnames+="rpms"+str(i)+"."+colparts[j%klen]+" AS "+colnames[i]+", "
#             self.log.debug("getAllColnamesNotInstalled: "+copy_colnames[:-2])
             ret_colnames.append(copy_colnames[:-2])
         return ret_colnames
#>>> y=list(x)
#>>> y.reverse()
#>>> result=list()
#>>> for a in x:
#...    line=list()
#...    line.append("x")
#...    for b in y[:-1]:
#...       line.append(b)
#...    result.append(line)
#...
#>>> print result
#[['x', 'b'], ['x', 'b']]


#       queries.append("SELECT name, "+columns[0]+", "+notinstalledcolumns[1]+' FROM '+dbs[0]+' WHERE '+where[0]+' AND rpms0.name NOT IN (SELECT name FROM '+dbs[1]+' WHERE '+where[1]+')')
#        ComLog.getLogger().debug("query2 %s" %query2)
#        queries.append("SELECT "+joincolumns[1]+", "+notinstalledcolumns[0]+", "+columns[1]+' FROM '+dbs[1]+' WHERE '+where[1]+' AND rpms1.name NOT IN (SELECT name FROM '+dbs[0]+' WHERE '+where[0]+')')


    def selectQueryOnlyDiffs(self, sourcenames, colnames):
        """
        Returns the select query that only filters differences between installed Software.
        See selectNotInstalledQuery.
        """
        j=0
        version_unequalcols=list()
        subversion_unequalcols=list()
        columns=list()
        dbs=list()
        where=list()
        for i in range(len(sourcenames)):
            formatedname=self.formatToSQLCompat(sourcenames[i])
            columns.append("rpms"+str(i)+".version AS "+colnames[j+1]+", rpms"+str(i)+".subversion AS "+\
                           colnames[j+2]+", rpms"+str(i)+".architecture AS "+colnames[j+3])
            dbs.append(self.tablename+" AS rpms"+str(i))
            where.append("rpms"+str(i)+".clustername=\""+sourcenames[i]+"\"")
            version_unequalcols.append("rpms"+str(i)+".version")
            subversion_unequalcols.append("rpms"+str(i)+".subversion")

            j+=3

        query="SELECT rpms0.name AS name, "+','.join(columns)+"\n FROM "+dbs[0]+"\n JOIN "+dbs[1]+\
              " USING (name, architecture)\n"+\
              " WHERE "+" AND ".join(where)+"\n   AND "+\
              " AND ".join(BaseDB.BinOperatorFromList(version_unequalcols, "!="))+"\n   AND "+\
              " AND ".join(BaseDB.BinOperatorFromList(subversion_unequalcols, "!="))
        return query

    def getDiffsFromCategories(self, categories, limitup=0, limitdown=0, orderby=None):
        """
        Returns a resultset of differences of the given categories.
        Parameter are the sourcesnames to compare
        RESTRICTION: Right now only the first 2 categories can be compared (SHOULD BE FIXED)
        """
        from ComSource import Source
        sources=list()
        source=Source(dbhandle=self.db)
        for category in categories:
            sname=source.getSourceForCategory(category)
            if sname:
                sources.append(sname)
        if len(sources) == 0:
            return None
        else:
            return self.getDiffsFromSources(sources, SoftwareCMDB.getColnamesForDiff(categories), limitup, limitdown, orderby)

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
        selectquery="SELECT name, version, subversion AS \"release\", architecture AS \"arch\", channel AS channelname, channelversion FROM %s WHERE clustername=\"%s\" AND name=\"%s\" AND architecture=\"%s\";" \
                    %(self.tablename, name, rpm["name"], rpm["arch"])
        #    ComLog.getLogger().debug("select %s" % selectquery)
        super(SoftwareCMDB, self).updateRPM(insertquery, updatequery, selectquery, rpm,
                                               ["version", "release", "channelname", "channelversion"],
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

    rs=cmdb.getDiffsFromSources(("lilr201", "lilr202"))
    softwarerow=rs.fetch_row()
    while softwarerow:
        print ",".join(softwarerow[0])
        softwarerow=rs.fetch_row()

if __name__ == '__main__':
    main()

# $Log: ComSoftwareCMDB.py,v $
# Revision 1.2  2007-03-05 16:10:30  marc
# first rpm version
#
# Revision 1.1  2007/02/23 12:42:23  marc
# initial revision
#
