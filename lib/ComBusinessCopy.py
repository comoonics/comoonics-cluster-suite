""" Comoonics BusinessCopy class


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id: ComBusinessCopy.py,v 1.2 2006-07-03 12:47:07 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComBusinessCopy.py,v $

import ComDataObject
import ComCopyset
import ComModificationset
import ComLog

def getBusinessCopy(element, doc):
    """ Factory function to create the BusinessCopy Objects"""
    return BusinessCopy(element, doc)

class BusinessCopy(ComDataObject.DataObject):
    """
    Class that does the businesscopy. Runs through every copyset and modificationset and executes them.
    """
    TAGNAME = "businesscopy"
    __logStrLevel__ = "BusinessCopy"

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
          
    def doCopysets(self):
        for copyset in self.copysets:
            copyset.doCopy()

    def undoCopysets(self):
        ComLog.getLogger(self.__logStrLevel__).debug("Copysets: %s " % self.copysets)
        self.copysets.reverse()
        for copyset in self.copysets:
            copyset.undoCopy()

    def doModificationsets(self):
        for modset in self.modificationsets:
            modset.doModifications()
          
    def undoModificationsets(self):
        self.modificationsets.reverse()
        for modset in self.modificationsets:
            modset.undoModifications()

#################################
# $Log: ComBusinessCopy.py,v $
# Revision 1.2  2006-07-03 12:47:07  marc
# added logging.
# change run through modifications
#
# Revision 1.1  2006/06/30 13:57:24  marc
# initial revision
#
