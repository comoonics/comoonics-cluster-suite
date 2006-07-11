""" Comoonics EnterpriseCopy class


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id: ComEnterpriseCopy.py,v 1.2 2006-07-11 09:25:07 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComEnterpriseCopy.py,v $

import ComDataObject
import ComCopyset
import ComModificationset
import ComLog

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
        ComLog.getLogger(self.__logStrLevel__).debug("%s, %s" % (ComCopyset.Copyset.TAGNAME, self.getElement().tagName))
        ecopysets=self.getElement().getElementsByTagName(ComCopyset.Copyset.TAGNAME)
        for i in range(len(ecopysets)):
            cs=ComCopyset.getCopyset(ecopysets[i], doc)
            self.copysets.append(cs)
        emodsets=self.getElement().getElementsByTagName(ComModificationset.Modificationset.TAGNAME)
        for i in range(len(emodsets)):
            ms=ComModificationset.getModificationset(emodsets[i], doc)
            self.modificationsets.append(ms)
          
    def doCopysets(self, name=None):
        for copyset in self.copysets:
            if not name or name == "all" or name == copyset.getAttribute("name", None):
                ComLog.getLogger(self.__logStrLevel__).info("Executing copyset %s(%s:%s)" % (copyset.__class__.__name__, copyset.getAttribute("name", "unknown"), copyset.getAttribute("type")))
                copyset.doCopy()

    def undoCopysets(self, name=None):
        ComLog.getLogger(self.__logStrLevel__).debug("Copysets: %s " % self.copysets)
        self.copysets.reverse()
        for copyset in self.copysets:
            if not name or name == "all" or name == copyset.getAttribute("name", None):
                ComLog.getLogger(self.__logStrLevel__).info("Undoing copyset %s(%s:%s)" % (copyset.__class__.__name__, copyset.getAttribute("name", "unknown"), copyset.getAttribute("type")))
                copyset.undoCopy()

    def doModificationsets(self, name=None):
        for modset in self.modificationsets:
            if not name or name == "all" or name == modset.getAttribute("name", None):
                ComLog.getLogger(self.__logStrLevel__).info("Executing modificationset %s(%s:%s)" % (modset.__class__.__name__, modset.getAttribute("name", "unknown"), modset.getAttribute("type")))
                modset.doModifications()
          
    def undoModificationsets(self, name=None):
        self.modificationsets.reverse()
        for modset in self.modificationsets:
            if not name or name == "all" or name == modset.getAttribute("name", None):
                ComLog.getLogger(self.__logStrLevel__).info("Undoing modificationset %s(%s:%s)" % (modset.__class__.__name__, modset.getAttribute("name", "unknown"), modset.getAttribute("type")))
                modset.undoModifications()

#################################
# $Log: ComEnterpriseCopy.py,v $
# Revision 1.2  2006-07-11 09:25:07  marc
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
