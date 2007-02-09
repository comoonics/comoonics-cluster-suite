""" Comoonics EnterpriseCopy class


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id: ComEnterpriseCopy.py,v 1.2 2007-02-09 12:25:22 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComEnterpriseCopy.py,v $

from xml.dom import Node
from comoonics import ComDataObject
from comoonics import ComLog
import ComCopyset
import ComModificationset

def getEnterpriseCopy(element, doc):
    """ Factory function to create the EnterpriseCopy Objects"""
    return EnterpriseCopy(element, doc)

class EnterpriseCopy(ComDataObject.DataObject):
    """
    Class that does the enterprisecopy. Runs through every copyset and modificationset and executes them.
    """
    TAGNAME = "enterprisecopy"
    __logStrLevel__ = "EnterpriseCopy"

    def __init__(self, element, doc):
        ComDataObject.DataObject.__init__(self, element, doc)

        self.copysets=list()
        self.modificationsets=list()
        self.allsets=list()
        self.donesets=list()
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

    def doAllsets(self, name=None):
        for set in self.allsets:
            if isinstance(set, ComCopyset.Copyset) and (not name or name == "all" or (set.hasAttribute("name") and name == set.getAttribute("name", None))):
                ComLog.getLogger(self.__logStrLevel__).info("Executing copyset %s(%s:%s)" % (set.__class__.__name__, set.getAttribute("name", "unknown"), set.getAttribute("type")))
                set.doCopy()
                self.donesets.append(set)
            elif isinstance(set, ComModificationset.Modificationset) and (not name or name == "all" or (set.hasAttribute("name") and name == set.getAttribute("name", None))):
                ComLog.getLogger(self.__logStrLevel__).info("Executing copyset %s(%s:%s)" % (set.__class__.__name__, set.getAttribute("name", "unknown"), set.getAttribute("type")))
                set.doModifications()
                self.donesets.append(set)

    def undo(self, name=None):
        self.undoDonesets(name)

    def undoDonesets(self, name=None):
        ComLog.getLogger(self.__logStrLevel__).debug("Allsets: %s " % self.allsets)
        self.donesets.reverse()
        for set in self.donesets:
            if isinstance(set, ComCopyset.Copyset) and (not name or name == "all" or (set.hasAttribute("name") and name == set.getAttribute("name", None))):
                ComLog.getLogger(self.__logStrLevel__).info("Executing copyset %s(%s:%s)" % (set.__class__.__name__, set.getAttribute("name", "unknown"), set.getAttribute("type")))
                set.undoCopy()
            elif isinstance(set, ComModificationset.Modificationset) and (not name or name == "all" or (set.hasAttribute("name") and name == set.getAttribute("name", None))):
                ComLog.getLogger(self.__logStrLevel__).info("Executing copyset %s(%s:%s)" % (set.__class__.__name__, set.getAttribute("name", "unknown"), set.getAttribute("type")))
                set.undoModifications()

    def undoAllsets(self, name=None):
        ComLog.getLogger(self.__logStrLevel__).debug("Allsets: %s " % self.allsets)
        self.allsets.reverse()
        for set in self.allsets:
            if isinstance(set, ComCopyset.Copyset) and (not name or name == "all" or (set.hasAttribute("name") and name == set.getAttribute("name", None))):
                ComLog.getLogger(self.__logStrLevel__).info("Executing copyset %s(%s:%s)" % (set.__class__.__name__, set.getAttribute("name", "unknown"), set.getAttribute("type")))
                set.undoCopy()
            elif isinstance(set, ComModificationset.Modificationset) and (not name or name == "all" or (set.hasAttribute("name") and name == set.getAttribute("name", None))):
                ComLog.getLogger(self.__logStrLevel__).info("Executing copyset %s(%s:%s)" % (set.__class__.__name__, set.getAttribute("name", "unknown"), set.getAttribute("type")))
                set.undoModifications()

    def doCopysets(self, name=None):
        for copyset in self.copysets:
            if not name or name == "all" or (copyset.hasAttribute("name") and name == copyset.getAttribute("name", None)):
                ComLog.getLogger(self.__logStrLevel__).info("Executing copyset %s(%s:%s)" % (copyset.__class__.__name__, copyset.getAttribute("name", "unknown"), copyset.getAttribute("type")))
                copyset.doCopy()
                self.donesets.append(set)

    def undoCopysets(self, name=None):
        ComLog.getLogger(self.__logStrLevel__).debug("Copysets: %s " % self.copysets)
        self.copysets.reverse()
        for copyset in self.copysets:
            if not name or name == "all" or (copyset.hasAttribute("name") and name == copyset.getAttribute("name", None)):
                ComLog.getLogger(self.__logStrLevel__).info("Undoing copyset %s(%s:%s)" % (copyset.__class__.__name__, copyset.getAttribute("name", "unknown"), copyset.getAttribute("type")))
                copyset.undoCopy()

    def doModificationsets(self, name=None):
        for modset in self.modificationsets:
            if not name or name == "all" or (modset.hasAttribute("name") and name == modset.getAttribute("name", "")):
                ComLog.getLogger(self.__logStrLevel__).info("Executing modificationset %s(%s:%s)" % (modset.__class__.__name__, modset.getAttribute("name", "unknown"), modset.getAttribute("type")))
                modset.doModifications()
                self.donesets.append(set)

    def undoModificationsets(self, name=None):
        self.modificationsets.reverse()
        for modset in self.modificationsets:
            if not name or name == "all" or (modset.hasAttribute("name") and name == modset.getAttribute("name", None)):
                ComLog.getLogger(self.__logStrLevel__).info("Undoing modificationset %s(%s:%s)" % (modset.__class__.__name__, modset.getAttribute("name", "unknown"), modset.getAttribute("type")))
                modset.undoModifications()

mylogger=ComLog.getLogger(EnterpriseCopy.__logStrLevel__)

#################################
# $Log: ComEnterpriseCopy.py,v $
# Revision 1.2  2007-02-09 12:25:22  marc
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
