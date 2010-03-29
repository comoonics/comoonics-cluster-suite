""" Comoonics EnterpriseCopy class


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id: ComEnterpriseCopy.py,v 1.12 2010-03-29 14:10:25 marc Exp $
#


__version__ = "$Revision: 1.12 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComEnterpriseCopy.py,v $

import re
import logging
from xml.dom import Node
from comoonics import ComDataObject
from comoonics import ComLog
import ComCopyset
import ComModificationset
from comoonics.ComExceptions import ComException

class CouldNotFindSet(ComException):
    _set="Set"
    def __str__(self):
        return "Could not find %s with name %s." %(self._set, self.value)
class CouldNotFindCopyset(CouldNotFindSet):
    _set="Copyset"
class CouldNotFindModset(CouldNotFindSet):
    _set="Modificationset"

def getEnterpriseCopy(element, doc):
    """ Factory function to create the EnterpriseCopy Objects"""
    return EnterpriseCopy(element, doc)

class EnterpriseCopy(ComDataObject.DataObject):
    """
    Class that does the enterprisecopy. Runs through every copyset and modificationset and executes them.
    """
    TAGNAME = "enterprisecopy"
    __logStrLevel__ = "comoonics.enterprisecopy.ComEnterpriseCopy"
    #__logStrLevel__ = "comoonics"
    #__logStrLevel__ = "comoonics.enterprisecopy"
    _logger=logging.getLogger(__logStrLevel__)

    def __init__(self, element, doc):
        ComDataObject.DataObject.__init__(self, element, doc)

        self.copysets=list()
        self.modificationsets=list()
        self.allsets=list()
        self.donesets=list()
        self.currentset=None
        elogging=self.getElement().getElementsByTagName("logging")
        #ComLog.getLogger().info("logger.effectivelevel: %s/%u" %(logging.getLevelName(self._logger.getEffectiveLevel()),self._logger.getEffectiveLevel()))
        if len(elogging)>0:
            ComLog.fileConfig(elogging[0])
        self._logger.disabled=0
        for child in self.getElement().childNodes:
            if child.nodeType == Node.ELEMENT_NODE and child.tagName ==  ComCopyset.Copyset.TAGNAME:
                cs=ComCopyset.getCopyset(child, doc)
                self.copysets.append(cs)
                self.allsets.append(cs)
            elif child.nodeType == Node.ELEMENT_NODE and child.tagName == ComModificationset.Modificationset.TAGNAME:
                ms=ComModificationset.getModificationset(child, doc)
                self.modificationsets.append(ms)
                self.allsets.append(ms)
#            else:
#                mylogger.debug("Ignoring child %s, %s" %(child.nodeName, child))

        #ComLog.getLogger(self.__logStrLevel__).debug("%s, %s" % (ComCopyset.Copyset.TAGNAME, self.getElement().tagName))
        #ecopysets=self.getElement().getElementsByTagName(ComCopyset.Copyset.TAGNAME)
        #for i in range(len(ecopysets)):
        #    cs=ComCopyset.getCopyset(ecopysets[i], doc)
        #    self.copysets.append(cs)
        #emodsets=self.getElement().getElementsByTagName(ComModificationset.Modificationset.TAGNAME)
        #for i in range(len(emodsets)):
        #    ms=ComModificationset.getModificationset(emodsets[i], doc)
        #    self.modificationsets.append(ms)

    def getCurrentSet(self):
        """ Returns the last set being executed """
        return self.currentset

    def doAllsets(self, sets=None):
        _found=False
        for set in self.allsets:
            if sets and type(sets)==list:
                for _name in sets:
                    if _name == set.getAttribute("name", "") or re.match(_name, set.getAttribute("name", "")):
                        self.currentset=set
            elif isinstance(sets, basestring):
                _name=sets
                if _name == set.getAttribute("name", "") or re.match(_name, set.getAttribute("name", "")) or _name=="all":
                    self.currentset=set
            elif not sets:
                self.currentset=set

            if self.currentset and isinstance(self.currentset, ComCopyset.Copyset):
                _found=True
                self._logger.info("Executing copyset %s(%s:%s)" % (set.__class__.__name__, set.getAttribute("name", "unknown"), set.getAttribute("type")))
                self.donesets.append(self.currentset)
                self.currentset.doPre()
                self.currentset.doCopy()
                self.currentset.doPost()
            elif self.currentset and isinstance(self.currentset, ComModificationset.Modificationset):
                _found=True
                self._logger.info("Executing copyset %s(%s:%s)" % (set.__class__.__name__, set.getAttribute("name", "unknown"), set.getAttribute("type")))
                self.donesets.append(set)
                self.currentset.doPre()
                self.currentset.doModifications()
                self.currentset.doPost()
            self.currentset=None
        if not self.currentset and not _found:
            raise CouldNotFindCopyset(sets)


    def undo(self, names=None):
        if len(self.donesets)>0:
            self.undoDonesets(names)

    def undoDonesets(self, names=None):
        if not names:
            names=[ "all" ]
        self._logger.debug("name: %s, donesets: sets: %s " %(names, self.donesets))
        self.donesets.reverse()
        for set in self.donesets:
            self.currentset=set
            for name in names:
                if isinstance(set, ComCopyset.Copyset) and (not name or name == "all" or (set.hasAttribute("name") and name == set.getAttribute("name", None))):
                    self._logger.info("Undoing copyset %s(%s:%s)" % (set.__class__.__name__, set.getAttribute("name", "unknown"), set.getAttribute("type")))
                    set.undoRequirements()
                    set.undoCopy()
                elif isinstance(set, ComModificationset.Modificationset) and (not name or name == "all" or (set.hasAttribute("name") and name == set.getAttribute("name", None))):
                    self._logger.info("Undoing Modificationset %s(%s:%s)" % (set.__class__.__name__, set.getAttribute("name", "unknown"), set.getAttribute("type")))
                    set.undoRequirements()
                    set.undoModifications()

    def undoAllsets(self, names=None):
        if not names:
            names=[ "all" ]
        self._logger.debug("name: %s, allsets: %s " %(names, self.allsets))
        self.allsets.reverse()
        for set in self.allsets:
            self.currentset=set
            for name in names:
                if isinstance(set, ComCopyset.Copyset) and (not name or name == "all" or (set.hasAttribute("name") and name == set.getAttribute("name", None))):
                    self._logger.info("Undoing copyset %s(%s:%s)" % (set.__class__.__name__, set.getAttribute("name", "unknown"), set.getAttribute("type")))
                    set.undoRequirements()
                    set.undoCopy()
                elif isinstance(set, ComModificationset.Modificationset) and (not name or name == "all" or (set.hasAttribute("name") and name == set.getAttribute("name", None))):
                    self._logger.info("Undoing modificationset %s(%s:%s)" % (set.__class__.__name__, set.getAttribute("name", "unknown"), set.getAttribute("type")))
                    set.undoRequirements()
                    set.undoModifications()

    def doCopysets(self, names=None):
        _found=False
        for copyset in self.copysets:
            self.currentset=copyset
            for name in names:
                if not name or name == "all" or (copyset.hasAttribute("name") and name == copyset.getAttribute("name", None)):
                    self._logger.info("Executing copyset %s(%s:%s)" % (copyset.__class__.__name__, copyset.getAttribute("name", "unknown"), copyset.getAttribute("type")))
                    _found=True
                    self.donesets.append(copyset)
                    copyset.doPre()
                    copyset.doCopy()
                    copyset.doPost()
        if not _found:
            raise CouldNotFindCopyset(name)


    def undoCopysets(self, names=None):
        self._logger.debug("name %s, copysets: %s " %(names, self.copysets))
        self.copysets.reverse()
        for copyset in self.copysets:
            self.currentset=copyset
            for name in names:
                if not name or name == "all" or (copyset.hasAttribute("name") and name == copyset.getAttribute("name", None)):
                    self._logger.info("Undoing copyset %s(%s:%s)" % (copyset.__class__.__name__, copyset.getAttribute("name", "unknown"), copyset.getAttribute("type")))
                    copyset.undoRequirements()
                    copyset.undoCopy()

    def doModificationsets(self, names=None):
        _found=False
        for modset in self.modificationsets:
            self.currentset=modset
            for name in names:
                if not name or name == "all" or (modset.hasAttribute("name") and name == modset.getAttribute("name", "")):
                    self._logger.info("Executing modificationset %s(%s:%s)" % (modset.__class__.__name__, modset.getAttribute("name", "unknown"), modset.getAttribute("type")))
                    _found=True
                    self.donesets.append(modset)
                    modset.doPre()
                    modset.doModifications()
                    modset.doPost()
        if not _found:
            raise CouldNotFindModset(name)

    def undoModificationsets(self, names=None):
        self._logger.debug("name %s, modificationsets: %s " %(names, self.modificationsets))
        self.modificationsets.reverse()
        for modset in self.modificationsets:
            self.currentset=modset
            for name in names:
                if not name or name == "all" or (modset.hasAttribute("name") and name == modset.getAttribute("name", None)):
                    self._logger.info("Undoing modificationset %s(%s:%s)" % (modset.__class__.__name__, modset.getAttribute("name", "unknown"), modset.getAttribute("type")))
                    modset.undoRequirements()
                    modset.undoModifications()

#################################
# $Log: ComEnterpriseCopy.py,v $
# Revision 1.12  2010-03-29 14:10:25  marc
# - fixed bug in undo methods when no names have been given.
#
# Revision 1.11  2010/03/08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.10  2010/02/07 20:30:36  marc
# - support for only selected sets.
#
# Revision 1.9  2007/07/31 15:15:29  marc
# - removed unneeded logging
#
# Revision 1.8  2007/06/19 12:50:25  marc
# - fixed the loglevel
#
# Revision 1.7  2007/06/15 19:04:17  marc
# - better logging
# - doAllsets with set as parameter cool stuff
#
# Revision 1.6  2007/06/13 13:21:30  marc
# - raising error if given modset/copyset could not be found
#
# Revision 1.5  2007/06/13 09:05:45  marc
# - using new ComLog api
# - default importing of ComDBLogger and registering at ComLog
#
# Revision 1.4  2007/03/26 07:54:31  marc
# - bugfixes in outputting the right strings
# - calling doPre and doPost for each Copyset and Modificationset (Requirements)
#
# Revision 1.3  2007/02/27 15:53:58  mark
# minor bugfixes
#
# Revision 1.2  2007/02/09 12:25:22  marc
# copy and modsets can now be executed in userdefined order.
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.3  2006/07/18 12:12:33  marc
# bugfix in selecting a modification/copyset
#
# Revision 1.2  2006/07/11 09:25:07  marc
# added support for command selected copysets and modificationsets
#
# Revision 1.1  2006/07/07 08:41:27  marc
# Business is now Enterprise sonst aendert sich nix.
#
# Revision 1.4  2006/07/05 13:06:34  marc
# support names on every tag.
#
# Revision 1.3  2006/07/04 11:00:41  marc
# be a little more verbose
#
# Revision 1.2  2006/07/03 12:47:07  marc
# added logging.
# change run through modifications
#
# Revision 1.1  2006/06/30 13:57:24  marc
# initial revision
#
