"""
Class for logging to a generic database

"""
# here is some internal information
# $Id: ComDBLogger.py,v 1.7 2008-08-14 12:05:24 marc Exp $
#

import logging
import socket
from ComDBConnection import DBConnection
from comoonics import ComLog

class DBLogger(logging.Handler):
    """
    This class is a logging.Handler that stores LogRecords produced by loggers in a table of a relational database.
    The defaults tablename is "log".
    """
    __logLevelStr__="comoonics.db.DBLogger"
    log=ComLog.getLogger(__logLevelStr__)
    DB_LOG_LEVEL=logging.DEBUG+5
    DB_LOG_LEVEL_NAME="DBLOG"
    logging.addLevelName(DB_LOG_LEVEL, DB_LOG_LEVEL_NAME)

    def __init__(self, *args, **kwds):
        """
        __init__(self, dbhandle)
        __init__(self, hostname, user, password, database)
        __init__(self, dbhandle=, [tablename=])
        __init__(self, hostname=, user=, password=, database=, [tablename=])
        dbhandle: is a handle already connected to a valid database
        hostname: hostname of the databaseserver
        user: user allowed to login to the database and databaseserver
        password: the password for the user
        database: the database to use
        """
        logging.Handler.__init__(self)
        self.logsource=None
        self.tablename="logs"
        if kwds and kwds.has_key("dbhandle"):
            self.dbconnection=DBConnection(dbhandle=kwds["dbhandle"])
        elif kwds and kwds.has_key("hostname") and kwds.has_key("user") and kwds.has_key("password") and kwds.has_key("database"):
            self.dbconnection=DBConnection(hostname=kwds["hostname"], user=kwds["user"], password=kwds["password"], database=kwds["database"])
        elif kwds:
            
            raise TypeError, "At least 1 or 4 keyword/value pairs expected. Give are " %len(kwds.keys())
        if kwds:
            for key in kwds.keys():
                setattr(self, key, kwds[key])

        if args and len(args)==1:
            self.dbconnection==DBConnection(dbhandle=args[0])
        elif args and len(args)==4:
            self.dbconnection=DBConnection(hostname=args[0], user=args[1], password=args[2], database=args[3])
        elif args:
            raise TypeError, "Either 1 or 4-5 parameters expected. Given are %u" %len(args)
        if not hasattr(self,"logsource") or not self.logsource:
            self.logsource=socket.gethostname()

    def getLogs(self, sourcenames, **kwds):
        """
        returns a recordset of all logentries found with the keywords.
        sourcenames: are all logsource
        kwds: directly passed to dbconnection.SelectQuery
        """
        if sourcenames:
            if kwds.has_key("where"):
                _where=kwds["where"]
            else:
                _where=dict()
                _where["logsource"]=sourcenames
            kwds["where"]=_where
            query=self.dbconnection.SelectQuery(From=self.tablename, **kwds)
        else:
            query=self.dbconnection.SelectQuery(From=self.tablename, **kwds)
        self.log.debug("getLogs(%s): %s" %(sourcenames, query))
        return self.dbconnection.selectQuery(query)

    def cleanLogs(self, sourcenames, **kwds):
        if isinstance(sourcenames, basestring):
            sourcenames=[sourcenames]
        query="DELETE FROM %s WHERE (%s) AND (%s)" %(self.tablename, " OR ".join(map(lambda sname: "logsource=\"%s\"" %sname, sourcenames)), kwds.get("where", "True"))
        ret=self.dbconnection.execQuery(query)
        self.log.debug("cleanLogs: query=%s, ret=%s" %(query, ret))

    def LogRecordToInsert(self, record):
        exc_info=None
        if record.exc_info:
            #buf=""
            #for exc_info in record.exc_info:
            #    buf+="<%s> %s; " %(type(exc_info), exc_info)
            import traceback
            (_class, _exception, _traceback)=record.exc_info
            exc_info=self.dbconnection.db.escape_string("".join(traceback.format_exception(_class, _exception, _traceback)))
            #self.log.debug("LogRecordToInsert, exc_info: %s" %(exc_info))
        else:
            exc_info="NULL"
        _logmsg=""
        try:
            _logmsg=str(record.msg) %record.args
        except:
            _logmsg=str(record.msg)
        
        _logmsg=self.dbconnection.db.escape_string(_logmsg)
        query="""
INSERT INTO %s
  SET name="%s",
    logsource="%s",
    logtimestamp=DEFAULT,
    loglevel=%u,
    logpathname="%s",
    loglineno=%u,
    logmsg="%s",
    logexecinfo="%s";
"""  %(self.tablename, record.name, self.logsource, record.levelno, record.pathname,
       record.lineno, _logmsg,exc_info)
#        self.log.debug("LogRecordToInsert: "+query)
        return query

    def emit(self, record):
        self.dbconnection.db.query(self.LogRecordToInsert(record))
        self.dbconnection.db.commit()

def test():
    logger=logging.getLogger("test")
    logger.setLevel(logging.DEBUG)
    DBLogger.log.setLevel(logging.DEBUG)
    logarray=("a", "b", "c")
    handlers=(DBLogger(hostname="mysql-server", user="atix", password="atix", database="atix_cmdb"),
              DBLogger("mysql-server", "atix", "atix", "atix_cmdb"))
    for handler in handlers:
        logger.addHandler(handler)
        print "Logging test:"
        logger.log(DBLogger.DB_LOG_LEVEL, "debugtes asdasfd asdfa\"- %s" %(",".join(logarray)))

        print "Exception test:"
        from exceptions import TypeError
        try:
            raise TypeError("TypeError x")
        except TypeError, e:
            logger.log(DBLogger.DB_LOG_LEVEL, "%s" %(e), exc_info=e)
        sources=list()
        sources.append(handler.logsource)
        rs=handler.getLogs(sources, select=["loglevel", "logid", "logsource", "logmsg", "logpathname", "logexecinfo", "logtimestamp"])
        print "Got %u rows." %(handler.dbconnection.db.affected_rows())
        rows=rs.fetch_row(1, 2)
        print " ".join(rows[0].keys())
        while rows:
            line=""
            for key in rows[0].keys():
                line+="%s, " %(rows[0][key])
            print line
            rows=rs.fetch_row(1, 2)

if __name__=="__main__":
    test()

########################
# $Log: ComDBLogger.py,v $
# Revision 1.7  2008-08-14 12:05:24  marc
# work around format bug
#
# Revision 1.6  2008/02/28 14:19:37  marc
# small bugfix in exeception logging
#
# Revision 1.5  2007/06/19 15:09:55  marc
# fixed logging
#
# Revision 1.4  2007/06/13 09:03:52  marc
# - using new ComLog api
# - default importing of ComDBLogger and registering at ComLog
#
# Revision 1.3  2007/04/18 07:56:48  marc
# Hilti RPM Control:
# - added support for where in getLogs
#
# Revision 1.2  2007/04/12 11:19:17  marc
# Hilti RPM Control
# - added logging for Exceptions (exc_info)
#
# Revision 1.1  2007/04/02 11:21:23  marc
# For Hilti RPM Control:
# - initial revision
#
