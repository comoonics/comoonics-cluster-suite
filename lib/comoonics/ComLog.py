"""Comoonics Logging module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComLog.py,v 1.3 2007-03-09 08:45:38 marc Exp $
#

__version__ = "$Revision: 1.3 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ComLog.py,v $

import logging
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
    return logging.getLogger(name)
#    return __default_log

#def setLogger(name, logger):
#    __default_log=logger
#
def setLevel(debuglevel, name=""):
    logging.getLogger(name).setLevel(debuglevel)

def getLevel():
    __default_log.getEffectiveLevel()

def __testLogger(name):
    logger=getLogger(name)
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")

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

if __name__ == "__main__":
    main()

# $Log: ComLog.py,v $
# Revision 1.3  2007-03-09 08:45:38  marc
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
