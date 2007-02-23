"""
Class for the BaseDB

FIXME: Should become a singleton based on table, dbname, user, pw
"""
# here is some internal information
# $Id: ComBaseDB.py,v 1.1 2007-02-23 12:42:23 marc Exp $
#

import MySQLdb

from comoonics import ComLog

class BaseDB(object):
    """
    Class for the cmdb representing a database connection an a tablename
    """
    log=ComLog.getLogger("BaseDB")

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

    def formatToSQLCompat(self, string):
        return string.replace("-", "_")

    def resolveWhere(self, where):
        """ resolves a where clause """
        whereclause=""
        if where != None:
            whereclause=" AND ".join(where)
        if whereclause != "":
            whereclause="WHERE %s" %(whereclause)
        return whereclause

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
            ret=False
            row=rows[0]
            prefix=self.tablename+"."
            for key in keys:
                if keymapping and type(keymapping) == dict and keymapping.has_key(key) and keymapping[key] != None:
                    mapping=keymapping[key]
                else:
                    mapping=rpm[key]
                ret=ret and row[prefix+key] == mapping
            if ret:
                self.log.debug("update %s" % updatequery)
                self.db.query(updatequery)

########################
# $log$