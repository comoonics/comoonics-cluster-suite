"""Comoonics Logging module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComLog.py,v 1.17 2011-02-15 15:00:24 marc Exp $
#
# @(#)$File$
#
# Copyright (c) 2001 ATIX GmbH, 2007 ATIX AG.
# Einsteinstrasse 10, 85716 Unterschleissheim, Germany
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__version__ = "$Revision: 1.17 $"
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
def setLevel(debuglevel, name=None):
    logging.getLogger(name).setLevel(debuglevel)

def getLevel(name=None):
    logging.getLogger(name).getEffectiveLevel()

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
        from comoonics.tools.XMLConfigParser import ConfigParser
    else:
        from ConfigParser import ConfigParser

    logging.shutdown()
    cp = ConfigParser(defaults)
    if hasattr(cp, 'readfp') and hasattr(fname, 'readline'):
        cp.readfp(fname)
    else:
        cp.read(fname)
    #first, do the formatters...
    if cp.has_section("formatters"):
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
            del logging._handlerList[:]
            #now set up the new ones...
            hlist = cp.get("handlers", "keys")
            _mylogger.debug("handlers: %s, %u" %(hlist, len(hlist)))
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
                        import warnings
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
            # MARC: I don't understand the following two lines why disabling the loggers if they might be used
            #       or referenced again and are disabled then.
            #for log in existing:
            #    root.manager.loggerDict[log].disabled = 1
        except:
            ei = sys.exc_info()
            traceback.print_exception(ei[0], ei[1], ei[2], None, sys.stderr)
            del ei
    finally:
        logging._releaseLock()

_mylogger=logging.getLogger("comoonics.ComLog")

# $Log: ComLog.py,v $
# Revision 1.17  2011-02-15 15:00:24  marc
# - import for XMLConfigParser from comoonics.tools
#
# Revision 1.16  2010/11/21 21:48:19  marc
# - fixed bug 391
#   - moved to upstream XmlTools implementation
#
# Revision 1.15  2009/07/22 08:37:40  marc
# fedora compliant
#
# Revision 1.14  2009/06/10 15:19:56  marc
# removed basicConfig.
# should be called in other programs.
#
# Revision 1.13  2008/02/27 10:42:28  marc
# - change in testing
#
# Revision 1.12  2007/07/31 15:14:20  marc
# - added getLevel
#
# Revision 1.11  2007/06/19 15:11:20  marc
# removed importing of DBLogger
#
# Revision 1.10  2007/06/15 19:00:26  marc
# - more testing
# - uncommented disabling of old loggers.
#
# Revision 1.9  2007/06/13 15:24:31  marc
# - fixed minor bug in setLevel default should be None as logger not empty string.
#
# Revision 1.8  2007/06/13 13:06:50  marc
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
