"""
Class for connecting to a generic database

"""
# here is some internal information
# $Id: ComDBConnection.py,v 1.3 2007-06-13 09:03:52 marc Exp $
#

import MySQLdb
from exceptions import KeyError

class DBConnection(object):
    """
    Class for the cmdb representing a database connection an a tablename
    """

    def __init__(self, **kwds):
        """
        Creates a new databaseconnection
        Can be constructed like this
        __init__(hostname=.., user=.., password=.., database=.., tablename=.., dbclass=..., ...)
        __init__(dbhandle=..)
        By default a mysql database connection is selected
        all other parameters are copied one to one
        """
        self.db=None
        if kwds.has_key("dbhandle"):
            self.db=kwds["dbhandle"]
        else:
            self.db=MySQLdb.connect(host=kwds["hostname"], user=kwds["user"], passwd=kwds["password"], db=kwds["database"])

        for key in kwds.keys():
            setattr(self, key, kwds[key])

    def SelectQuery(self, *params, **kwds):
        if params and len(params)>0:
            query=params[0]
        elif kwds:
            selectclause="*"
            fromclause=""
            whereclause=""
            orderclause=""
            limitclause=""
            if kwds.has_key("select"):
                if isinstance(kwds["select"], basestring):
                    selectclause=kwds["select"]
                elif type(kwds["select"]) == list:
                    selectclause=", ".join(kwds["select"])
            if kwds.has_key("From"):
                fromclause="%s" %(kwds["From"])
            else:
                raise KeyError("Missing parameter from")
            if kwds.has_key("where"):
                if isinstance(kwds["where"], basestring):
                    whereclause=kwds["where"]
                elif type(kwds["where"]) == list:
                    whereclause=", ".join(kwds["where"])
                elif type(kwds["where"]) == dict:
                    where=kwds["where"]
                    for key in where:
                        if type(where[key]) == list:
                            _where=""
                            for value in where[key]:
                                _where+="OR %s=\"%s\"" %(key, self.db.escape_string(value))
                            _where=_where[3:]
                            whereclause+="(%s)" %(_where)
                        else:
                            whereclause+=" AND %s=\"%s\"" %(key, self.db.escape_string(where[key]))
                            whereclause=whereclause[4:]
            elif kwds.has_key("orwhere"):
                if isinstance(kwds["orwhere"], basestring):
                    whereclause=kwds["orwhere"]
                elif type(kwds["orwhere"]) == list:
                    whereclause=", ".join(kwds["orwhere"])
                elif type(kwds["orwhere"]) == dict:
                    where=kwds["orwhere"]
                    for key in where:
                        if type(where[key]) == list:
                            _where=""
                            for value in where[key]:
                                _where+="OR %s=\"%s\"" %(key, self.db.escape_string(value))
                            _where=_where[3:]
                            whereclause+="%s" %(_where)
                        else:
                            whereclause+=" OR %s=\"%s\"" %(key, self.db.escape_string(where[key]))
                            whereclause=whereclause[3:]
            if kwds.has_key("order"):
                if isinstance(kwds["order"], basestring):
                    orderclause=kwds["order"]
                elif type(kwds["order"]) == list:
                    orderclause=", ".join(kwds["order"])

            if kwds.has_key("limit"):
                limitclause=kwds["limit"]
            if kwds.has_key("limit1") and kwds.has_key("limit2"):
                if type(kwds["limit1"])==int and type(kwds["limit2"])==int:
                    limitclause="%u,%u" %(kwds["limit1"], kwds["limit2"])
                else:
                    limitclause="%s,%s" %(int(kwds["limit1"], int(kwds["limit2"])))

            if whereclause and whereclause != "" and not whereclause.upper().startswith("WHERE "):
                whereclause="WHERE %s" %(whereclause)

            if orderclause and orderclause != "" and not orderclause.upper().startswith("ORDER BY "):
                orderclause="ORDER BY %s" %(orderclause)

            if limitclause and limitclause != "" and not limitclause.upper().startswith("LIMIT "):
                limitclause="LIMIT %s" %(limitclause)

            query="SELECT %s FROM %s %s %s %s;" %(selectclause, fromclause, whereclause, orderclause, limitclause)

        return query

    def selectQuery(self, *params, **kwds):
        """ Returns the recordset for this query. Where query is a SQL Query directly executen on the
            databasehandle
           selectQuery(query | (
                      [select=selectclause | listofcolumns] | [From=table2select] |
                      [where=whereclause | where_pairs=dict],
                      [order=orderclause | listofcolumns] [limit=limitclause| (limit1=num, limit2)]))
        """
        query=self.SelectQuery(*params, **kwds)
        self.db.query(query)
        rs=self.db.store_result()
        return rs

    def execQuery(self, query):
        self.db.query(query)
        rs=self.db.store_result()
        return rs

    def close(self):
        self.db.close()

def test():
    testtable="logs"
    dbconnection=DBConnection(hostname="mysql-server", user="atix", password="atix", database="atix_cmdb")
    rs=dbconnection.selectQuery("show tables;")
    rows=rs.fetch_row(1, 2)
    print " ".join(rows[0].keys())
    while rows:
        print " ".join(rows[0].values())
        rows=rs.fetch_row(1, 2)

    query=dbconnection.SelectQuery(From=testtable, limit1=0, limit2=10)
    print "Query: %s" %(query)

    rs=dbconnection.selectQuery(query)
    rows=rs.fetch_row(1, 2)
    print " ".join(rows[0].keys())
    while rows:
        line=""
        for key in rows[0].keys():
            line+="%s, " %(rows[0][key])
        print line
        rows=rs.fetch_row(1, 2)

    dbconnection.close()
if __name__=="__main__":
    test()

########################
# $Log: ComDBConnection.py,v $
# Revision 1.3  2007-06-13 09:03:52  marc
# - using new ComLog api
# - default importing of ComDBLogger and registering at ComLog
#
# Revision 1.2  2007/04/27 08:51:57  marc
# MMG Support:
# - added execQuery
#
# Revision 1.1  2007/04/02 11:21:23  marc
# For Hilti RPM Control:
# - initial revision
#
