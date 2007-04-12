"""
Class for the BaseDB

FIXME: Should become a singleton based on table, dbname, user, pw
"""
# here is some internal information
# $Id: ComBaseDB.py,v 1.6 2007-04-12 07:52:56 marc Exp $
#

import MySQLdb
import logging

from comoonics import ComLog
from comoonics.db.ComDBLogger import DBLogger
from comoonics.db.ComDBConnection import DBConnection

class BaseDB(DBConnection):
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
                orderbyclause+=", \""+ob+"\""
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
        super(BaseDB, self).__init__(**kwds)
        self.tablename=kwds["tablename"]
        self.dblog=logging.getLogger("DB::"+self.__class__.__name__)
        if hasattr(self, "logsource"):
            self.dblog.addHandler(DBLogger(dbhandle=self.db, logsource=getattr(self, "logsource")))
        else:
            self.dblog.addHandler(DBLogger(dbhandle=self.db))
        self.dblog.setLevel(DBLogger.DB_LOG_LEVEL)

    def escapeSQL(self, toescape):
        ret=None
        if isinstance(toescape, basestring):
            ret=self.db.escape_string(toescape)
        elif type(toescape)==list:
            ret=list()
            for name in toescape:
                ret.append(self.escapeSQL(name))
        else:
            ret=self.db.escape("%s" %(toescape))
        return ret

#    def selectQuery(self, query):
#        """ Returns the recordset for this query. Where query is a SQL Query directly executen on the
#            databasehandle """
#        self.db.query(query)
#        rs=self.db.store_result()
#        return rs

    def updateRPM(self, insertquery, updatequery, selectquery, _rpm, keys=["name", "version", "release", "arch"], keymapping=None):
        """
        Executes the updatequery selectquery returns more then 0 rows and the rpm unsuccessfully compared.
        rpm: if not given updatequery is always applyed if selectquery returns more then 0 rows
        keys: keys to compare with default (name, version, release, arch) selectquery has to be formulated apropriate
        returns: 0 if nothing was updated, 1 if inserted and 2 if updated
        """
        #self.log.debug("selectquery: %s" % selectquery)
        _return=0
        rs=self.selectQuery(selectquery)
        count=rs.num_rows()
        log_array=list()

        if count == 0:
            #self.log.debug("insert %s" % insertquery)
            self.db.query(insertquery)
            _return=1
        else:
            rows=rs.fetch_row(1, 2)
            ret=False
            while rows and not ret:
                row=rows[0]
                prefix=self.tablename+"."
                if keys and _rpm:
                    for key in keys:
#                        self.log.debug("mappingkey: "+key+", keymapping %s" %(keymapping))
                        if keymapping and type(keymapping) == dict and keymapping.has_key(key) and keymapping[key] != None:
                            mapping=keymapping[key]
                        else:
                            mapping=_rpm[key]

                        ret=ret or row[prefix+key] != mapping
                        # self.log.debug("row[%s]:%s == %s: ret: %s" %(prefix+key, row[prefix+key], mapping, ret))
                else:
                    ret=True
                if ret:
                    #self.log.debug("update %s" % updatequery)
                    self.db.query(updatequery)
                    _return=2
                rows=rs.fetch_row(1, 2)
        return _return

def test():
    testlist=[ "a", "b", "c", "d" ]
    print "Testing Binoperator with: "
    print BaseDB.BinOperatorFromList(testlist, "!=")

if __name__=="__main__":
    test()

########################
# $Log: ComBaseDB.py,v $
# Revision 1.6  2007-04-12 07:52:56  marc
# Hilti RPM Control
# - Bugfix in changing or adding multiple rpms with same name
#
# Revision 1.5  2007/04/02 11:12:37  marc
# For Hilti RPM Control:
# - added BaseClass DBConnection
# - changed updateRPM when no select parameters were give to update then
#
# Revision 1.4  2007/03/14 16:51:21  marc
# fixed update error
#
# Revision 1.3  2007/03/14 13:16:48  marc
# added support for comparing multiple n>2 sources
#
