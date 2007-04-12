"""
Class for logging to a generic database

"""
# here is some internal information
# $Id: ComDBLogger.py,v 1.2 2007-04-12 11:19:17 marc Exp $
#

import logging
import socket
from ComDBConnection import DBConnection
from comoonics import ComLog

class DBLogger(logging.Handler):
    __logLevelStr__="DBLogger"
    log=ComLog.getLogger(__logLevelStr__)
    DB_LOG_LEVEL=logging.DEBUG+5
    DB_LOG_LEVEL_NAME="DBLOG"
    logging.addLevelName(DB_LOG_LEVEL, DB_LOG_LEVEL_NAME)

    def __init__(self, **kwds):
        logging.Handler.__init__(self)
        self.tablename="logs"
        if kwds.has_key("dbhandle"):
            self.dbconnection=DBConnection(dbhandle=kwds["dbhandle"])
        else:
            self.dbconnection=DBConnection(hostname=kwds["hostname"], user=kwds["user"], password=kwds["password"], database=kwds["database"])
        for key in kwds.keys():
            setattr(self, key, kwds[key])
        if not hasattr(self,"logsource"):
            self.logsource=socket.gethostname()

    def getLogs(self, sourcenames, **kwds):
        if sourcenames:
            query=self.dbconnection.SelectQuery(From=self.tablename, where={"logsource": sourcenames}, **kwds)
        else:
            query=self.dbconnection.SelectQuery(From=self.tablename, **kwds)
        self.log.debug("getLogs(%s): %s" %(sourcenames, query))
        return self.dbconnection.selectQuery(query)


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
       record.lineno, self.dbconnection.db.escape_string(record.msg %record.args),exc_info)
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
    handler=DBLogger(hostname="mysql-server", user="atix", password="atix", database="atix_cmdb")
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
# Revision 1.2  2007-04-12 11:19:17  marc
# Hilti RPM Control
# - added logging for Exceptions (exc_info)
#
# Revision 1.1  2007/04/02 11:21:23  marc
# For Hilti RPM Control:
# - initial revision
#
