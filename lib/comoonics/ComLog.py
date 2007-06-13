"""Comoonics Logging module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComLog.py,v 1.8 2007-06-13 13:06:50 marc Exp $
#

__version__ = "$Revision: 1.8 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ComLog.py,v $

import logging
import sys
import logging.handlers
import string
import traceback
import os.path

#from comoonics.db.ComDBLogger import DBLogger

#global __default_log
_classregistry={}

#__default_log=logging.getLogger()
#__default_log.setLevel(logging.DEBUG)

def registerHandler(name, _class):
    #global _classregistry
    _classregistry[name]=_class

def getRegisteredHandler(name):
    #global _classregistry
    return _classregistry[name]

def getLogger(name=None):
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

#def getLevel():
#    __default_log.getEffectiveLevel()

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
    if logger.getEffectiveLevel() <= level:
#        pass
        from StringIO import StringIO
        buf=StringIO()
        traceback.print_exc(None, buf)
        logger.log(level, buf.getvalue())

def fileConfig(fname, defaults=None, _vars=None):
    """
    Read the logging configuration from a ConfigParser-format file.

    This can be called several times from an application, allowing an end user
    the ability to select from various pre-canned configurations (if the
    developer provides a mechanism to present the choices and load the chosen
    configuration).
    In versions of ConfigParser which have the readfp method [typically
    shipped in 2.x versions of Python], you can pass in a file-like object
    rather than a filename, in which case the file-like object will be read
    using readfp.

    Derived from python 2.4.4 but extended with _vars so that additional classes from
    other sides can be loaded. Just give _vars as dict with name->class.
    Also this method support xml config files (see XMLConfigParser) if fname ends with
    extension xml.
    """
    #global _classregistry
    #print os.path.splitext(fname)
    from xml.dom import Node
    if isinstance(fname, Node) or os.path.splitext(fname)[1] == ".xml":
        from XMLConfigParser import ConfigParser
    else:
        from ConfigParser import ConfigParser

    logging.shutdown()
    cp = ConfigParser(defaults)
    if hasattr(cp, 'readfp') and hasattr(fname, 'readline'):
        cp.readfp(fname)
    else:
        cp.read(fname)
    #first, do the formatters...
    flist = cp.get("formatters", "keys")
    if len(flist):
        flist = string.split(flist, ",")
        formatters = {}
        for form in flist:
            sectname = "formatter_%s" % form
            opts = cp.options(sectname)
            if "format" in opts:
                fs = cp.get(sectname, "format", 1)
            else:
                fs = None
            if "datefmt" in opts:
                dfs = cp.get(sectname, "datefmt", 1)
            else:
                dfs = None
            f = logging.Formatter(fs, dfs)
            formatters[form] = f
    #next, do the handlers...
    #critical section...
    logging._acquireLock()
    try:
        try:
            #first, lose the existing handlers...
            logging._handlers.clear()
            #now set up the new ones...
            hlist = cp.get("handlers", "keys")
            _mylogger.debug("handlers: %s" %hlist)
            if len(hlist):
                hlist = string.split(hlist, ",")
                handlers = {}
                fixups = [] #for inter-handler references
                for hand in hlist:
                    try:
                        hand=hand.strip()
                        sectname = "handler_%s" % hand
                        klass = cp.get(sectname, "class")
                        opts = cp.options(sectname)
                        if "formatter" in opts:
                            fmt = cp.get(sectname, "formatter")
                        else:
                            fmt = ""
                        if not _vars:
                            _vars=vars(logging)
                        else:
                            _vars.update(vars(logging))
                        _vars.update(_classregistry)

                        klass=eval(klass, _vars)
                        args = cp.get(sectname, "args")
                        #_mylogger.debug("comoonics.ComLog.fileConfig(_classregistry: %s)" %_classregistry)
                        #_mylogger.debug("comoonics.ComLog.fileConfig(_vars: %s)" %_vars.keys())
                        args = eval(args, _vars)
                        h = apply(klass, args)
                        if "level" in opts:
                            level = cp.get(sectname, "level")
                            h.setLevel(logging._levelNames[level])
                        if len(fmt):
                            h.setFormatter(formatters[fmt])
                        #temporary hack for FileHandler and MemoryHandler.
                        if klass == logging.handlers.MemoryHandler:
                            if "target" in opts:
                                target = cp.get(sectname,"target")
                            else:
                                target = ""
                            if len(target): #the target handler may not be loaded yet, so keep for later...
                                fixups.append((h, target))
                        _mylogger.debug("handlers[%s]=%s" %(hand, h))
                        handlers[hand] = h
                    except:     #if an error occurs when instantiating a handler, too bad
                        _mylogger.exception("Could not create handler: %s" %klass)
                        #this could happen e.g. because of lack of privileges
                #now all handlers are loaded, fixup inter-handler references...
                for fixup in fixups:
                    h = fixup[0]
                    t = fixup[1]
                    h.setTarget(handlers[t])
            #at last, the loggers...first the root...
            llist = cp.get("loggers", "keys")
            llist = string.split(llist, ",")
            llist.remove("root")
            sectname = "logger_root"
            root = logging.root
            log = root
            opts = cp.options(sectname)
            if "level" in opts:
                level = cp.get(sectname, "level")
                log.setLevel(logging._levelNames[level])
            for h in root.handlers[:]:
                root.removeHandler(h)
            hlist = cp.get(sectname, "handlers")
            if len(hlist):
                hlist = string.split(hlist, ",")
                for hand in hlist:
                    hand=hand.strip()
                    log.addHandler(handlers[hand])
            #and now the others...
            #we don't want to lose the existing loggers,
            #since other threads may have pointers to them.
            #existing is set to contain all existing loggers,
            #and as we go through the new configuration we
            #remove any which are configured. At the end,
            #what's left in existing is the set of loggers
            #which were in the previous configuration but
            #which are not in the new configuration.
            existing = root.manager.loggerDict.keys()
            #now set up the new ones...
            for log in llist:
                sectname = "logger_%s" % log
                qn = cp.get(sectname, "qualname")
                opts = cp.options(sectname)
                if "propagate" in opts:
                    propagate = cp.getint(sectname, "propagate")
                else:
                    propagate = 1
                logger = logging.getLogger(qn)
                if qn in existing:
                    existing.remove(qn)
                if "level" in opts:
                    level = cp.get(sectname, "level")
                    logger.setLevel(logging._levelNames[level])
                for h in logger.handlers[:]:
                    logger.removeHandler(h)
                logger.propagate = propagate
                logger.disabled = 0
                hlist = cp.get(sectname, "handlers")
                if len(hlist):
                    hlist = string.split(hlist, ",")
                    for hand in hlist:
                        hand=hand.strip()
                        logger.addHandler(handlers[hand])
            #Disable any old loggers. There's no point deleting
            #them as other threads may continue to hold references
            #and by disabling them, you stop them doing any logging.
            for log in existing:
                root.manager.loggerDict[log].disabled = 1
        except:
            ei = sys.exc_info()
            traceback.print_exception(ei[0], ei[1], ei[2], None, sys.stderr)
            del ei
    finally:
        logging._releaseLock()

# Implicitly try to import DBLogger and let it register
try:
    import comoonics.db.ComDBLogger
except:
    pass

def __testLogger(name, logger):
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
    print "-------------------------- %s --------------------------------------" %(text)

def main():
    _mylogger.setLevel(logging.DEBUG)
    import comoonics.db.ComDBLogger
    registerHandler("DBLogger", comoonics.db.ComDBLogger.DBLogger)
    _filenames=("../../test/loggingconfig.ini", "../../test/loggingconfig.xml")
    getLogger().info("Testing ComLog:")
    loggers={"test1": logging.DEBUG,
             "test2": logging.INFO,
             "test3": logging.WARNING}
    for loggername in loggers.keys():
        __line("%s level: %s" %(loggername, logging.getLevelName(loggers[loggername])))
        setLevel(loggers[loggername], loggername)
        __testLogger(loggername, getLogger(loggername))

    __line("mylogger without level")
    __testLogger("mylogger", getLogger("mylogger"))
    cp=None

    __line("ComLog._classregistry: %s" %_classregistry)
    for _filename in _filenames:
        logging.shutdown()
        __line("Testing configfile %s" %_filename)
        fileConfig(_filename, None, )
        rootlogger=getLogger()
        __testLogger("root", rootlogger)
        for _lname in rootlogger.manager.loggerDict.keys():
            __testLogger(_lname, logging.getLogger(_lname))

_mylogger=logging.getLogger("comoonics.ComLog")
logging.basicConfig()
if __name__ == "__main__":
    main()

# $Log: ComLog.py,v $
# Revision 1.8  2007-06-13 13:06:50  marc
# - bugfix in logTraceLog
#
# Revision 1.7  2007/06/13 09:11:46  marc
# - added fileConfig to support logging config via XML
#
# Revision 1.6  2007/03/26 08:31:13  marc
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
