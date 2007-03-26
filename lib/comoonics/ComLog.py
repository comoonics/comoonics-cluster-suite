"""Comoonics Logging module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComLog.py,v 1.6 2007-03-26 08:31:13 marc Exp $
#

__version__ = "$Revision: 1.6 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ComLog.py,v $

import logging
import traceback
#import exceptions

global __default_log
logging.basicConfig()
__default_log=logging.getLogger("")
__default_log.setLevel(logging.DEBUG)

#try:
#    logging.basicConfig(level=logging.DEBUG)
#except Exception:
#    logging.basicConfig()


def getLogger(name=""):
    """
    Returns a new logger for the given name with derived level from rootlogger.
    """
    return logging.getLogger(name)
#    return __default_log

#def setLogger(name, logger):
#    __default_log=logger
#
def setLevel(debuglevel, name=""):
    logging.getLogger(name).setLevel(debuglevel)

def getLevel():
    __default_log.getEffectiveLevel()

def debugTraceLog(nameorlogger=None):
    logTrace(nameorlogger, logging.DEBUG)

def infoTraceLog(nameorlogger=None):
    logTrace(nameorlogger, logging.INFO)

def warningTraceLog(nameorlogger=None):
    logTrace(nameorlogger, logging.WARNING)

def criticalTraceLog(nameorlogger=None):
    logTrace(nameorlogger, logging.CRITICAL)

def errorTraceLog(nameorlogger=None):
    logTrace(nameorlogger, logging.ERROR)

def logTrace(nameorlogger=None, level=logging.DEBUG):
    if nameorlogger and type(nameorlogger)==str:
        logger=getLogger(nameorlogger)
    elif nameorlogger and isinstance(nameorlogger, logging.Logger):
        logger=nameorlogger
    else:
        logger=getLogger()
    if logger.getEffectiveLevel() == level:
#        pass
        from StringIO import StringIO
        buf=StringIO()
        traceback.print_exc(None, buf)
        logger.log(level, buf.getvalue())

def __testLogger(name):
    logger=getLogger(name)
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")
    __line("Error for "+name)
    try:
        from exceptions import IOError
        raise IOError("testioerror")
    except:
        debugTraceLog(name)
        infoTraceLog(name)
        warningTraceLog(name)
        errorTraceLog(name)
        criticalTraceLog(name)

def __line(text):
    getLogger().info("-------------------------- %s --------------------------------------" %(text))

def main():
    getLogger().info("Testing ComLog:")
    loggers={"test1": logging.DEBUG,
             "test2": logging.INFO,
             "test3": logging.WARNING}
    for loggername in loggers.keys():
        __line("%s level: %s" %(loggername, logging.getLevelName(loggers[loggername])))
        setLevel(loggers[loggername], loggername)
        __testLogger(loggername)

    __line("mylogger without level")
    __testLogger("mylogger")

if __name__ == "__main__":
    main()

# $Log: ComLog.py,v $
# Revision 1.6  2007-03-26 08:31:13  marc
# - added logTrace and debugLogTrace and the like
#
# Revision 1.5  2007/03/09 09:09:57  marc
# added logTrace and friends.
#
# Revision 1.4  2007/03/09 08:49:55  marc
# just another test and little more docu
#
# Revision 1.3  2007/03/09 08:45:38  marc
# implemented the loggernames and levels and a testingfunction
#
# Revision 1.2  2007/03/05 16:12:04  marc
# added setLogger
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.7  2006/07/03 16:09:45  marc
# added setLoglevel
#
# Revision 1.6  2006/06/28 17:27:26  marc
# comment out import exceptions
#
# Revision 1.5  2006/06/23 11:50:10  mark
# moved log to bottom
#
# Revision 1.4  2006/06/23 07:56:47  mark
# added comaptibility to Python 2.3
#
# Revision 1.3  2006/06/14 10:51:34  mark
# added Log Tag
#
