"""
Class for logging to a generic database

"""
# here is some internal information
# $Id: testxmlconfigparser.py,v 1.1 2007-06-13 09:16:54 marc Exp $
#
import comoonics
from comoonics import XMLConfigParser
from comoonics import ComLog
import logging
import logging.config

def testLogger(logger):
    logger.info("Info")

def line(text):
    print "---------------------------%s-----------------------------------" %(text)

# Is needed because implicitly basicConfig is called when importing ComLog (To be changed???)
logging.shutdown()

line("testing standard logging")
logging.config.fileConfig("loggingconfig.ini")
loggers=(ComLog.getLogger(), ComLog.getLogger("atix"), ComLog.getLogger("atix.atix1"), ComLog.getLogger("atix.atix2"))

for logger in loggers:
    testLogger(logger)

logging.shutdown()
line("testing as XMLConfigParser logging")
comoonics.asConfigParser()
logging.config.fileConfig("loggingconfig.ini")

loggers=(ComLog.getLogger(), ComLog.getLogger("atix"), ComLog.getLogger("atix.atix1"), ComLog.getLogger("atix.atix2"))

for logger in loggers:
    testLogger(logger)
########################
# $Log: testxmlconfigparser.py,v $
# Revision 1.1  2007-06-13 09:16:54  marc
# obsolete??
#
