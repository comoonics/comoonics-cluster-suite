"""
Class for the BaseDB

FIXME: Should become a singleton based on table, dbname, user, pw
"""
# here is some internal information
# $Id: ComBaseDB.py,v 1.3 2007-03-14 13:16:48 marc Exp $
#

import MySQLdb

from comoonics import ComLog

class BaseDB(object):
    """
    Class for the cmdb representing a database connection an a tablename
    """
    log=ComLog.getLogger("BaseDB")

    def formatToSQLCompat(string):
        return string.replace("-", "_")
    formatToSQLCompat=staticmethod(formatToSQLCompat)

    def resolveWhere(where):
        """ resolves a where clause """
        whereclause=""
        if where != None:
            whereclause=" AND ".join(where)
        if whereclause != "":
            whereclause="WHERE %s" %(whereclause)
        return whereclause
    resolveWhere=staticmethod(resolveWhere)

    def resolveOrderBy(orderby):
        """ resolves a orderby clause via a list of names """
        if not orderby:
            return ""
        orderbyclause=""
        if type(orderby)==list:
            orderby.reverse()
            for ob in orderby:
                orderbyclause+=", "+BaseDB.formatToSQLCompat(ob)
            orderbyclause=orderbyclause[2:]
        if type(orderby)==str:
            orderbyclause=orderby
        if orderbyclause != "":
            orderbyclause=" ORDER BY "+orderbyclause
        return orderbyclause
    resolveOrderBy=staticmethod(resolveOrderBy)

    def BinOperatorFromList(thelist, operator_str):
        ret_list=list()
        for i in range(len(thelist)):
            thelist2=list(thelist[i+1:])
            for j in range(len(thelist2)):
                ret_list.append(thelist[i]+operator_str+thelist2[j])
        return ret_list
    BinOperatorFromList=staticmethod(BinOperatorFromList)

    def getLimit(limitup, limitdown):
        limit=""
        if limitup<0:
            limitup=0
        if limitup!=limitdown:
            limit="LIMIT %s,%s" %(limitup, limitdown)
        return limit
    getLimit=staticmethod(getLimit)

    def __init__(self, **kwds):
        """
        Creates a new databaseconnection
        Can be constructed like this
        __init__(hostname=.., user=.., password=.., database=.., tablename=..)
        __init__(dbhandle=.., tablename=..)
        """
        if kwds.has_key("dbhandle"):
            self.db=kwds["dbhandle"]
        else:
            self.db=MySQLdb.connect(host=kwds["hostname"], user=kwds["user"], passwd=kwds["password"], db=kwds["database"])
        self.tablename=kwds["tablename"]

    def selectQuery(self, query):
        """ Returns the recordset for this query. Where query is a SQL Query directly executen on the
            databasehandle """
        self.db.query(query)
        rs=self.db.store_result()
        return rs

    def updateRPM(self, insertquery, updatequery, selectquery, rpm, keys=["name", "version", "release", "arch"], keymapping=None):
        """
        Executes the updatequery selectquery returns more then 0 rows and the rpm unsuccessfully compared.
        rpm: if not given updatequery is always applyed if selectquery returns more then 0 rows
        keys: keys to compare with default (name, version, release, arch) selectquery has to be formulated apropriate
        """
        self.log.debug("selectquery: %s" % selectquery)
        rs=self.selectQuery(selectquery)
        rows=rs.fetch_row(1, 2)
        if len(rows) == 0:
            self.log.debug("insert %s" % insertquery)
            self.db.query(insertquery)
        else:
            ret=True
            row=rows[0]
            prefix=self.tablename+"."
            for key in keys:
#                self.log.debug("mappingkey: "+key)
                if keymapping and type(keymapping) == dict and keymapping.has_key(key) and keymapping[key] != None:
                    mapping=keymapping[key]
                else:
                    mapping=rpm[key]
#                self.log.debug("row[%s]:%s == %s: " %(prefix+key, row[prefix+key], mapping))

                ret=ret and row[prefix+key] != mapping
            if ret:
                self.log.debug("update %s" % updatequery)
                self.db.query(updatequery)

def test():
    testlist=[ "a", "b", "c", "d" ]
    print "Testing Binoperator with: "
    print BaseDB.BinOperatorFromList(testlist, "!=")

if __name__=="__main__":
    test()

########################
# $Log: ComBaseDB.py,v $
# Revision 1.3  2007-03-14 13:16:48  marc
# added support for comparing multiple n>2 sources
#
