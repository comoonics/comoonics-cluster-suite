""" Comoonics Requirement class


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id: ComRequirement.py,v 1.1 2006-07-19 14:29:15 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComRequirement.py,v $

from comoonics.ComDataObject import DataObject
from comoonics.ComExceptions import ComException
from comoonics.ComJournaled import JournaledObject

class UnsupportedRequirementException(ComException): pass

def getRequirement(element, doc):
    """ Factory function to create Requirement"""
    __type=element.getAttribute("type")
    if __type == "archive":
        from ComArchiveRequirement import ArchiveRequirement
        return ArchiveRequirement(element, doc)
    else:
        raise UnsupportedRequirementException("Unsupported Requirement type %s in element " % (__type, element.tagName))

class Requirement(DataObject):
    """
    Requirement baseclass is responsible for resolving requirements needed for the copy or modificationsets.
    """
    
    """
    Static methods and objects/attributes
    """
    __logStrLevel__ = "Requirement"
    TAGNAME = "requirement"

    """
    Public methods
    """

    def __init__(self, element, doc):
        """
        Creates a new requirement instance
        """
        DataObject.__init__(self, element, doc)
    
    def doPre(self):
        """
        Does something previously
        """
        pass
    
    def do(self):
        """
        If need be does something
        """
        pass
    
    def doPost(self):
        """
        Does something afterwards
        """
        pass
    
    def doUndo(self):
        """
        Undos this requirement
        """
        pass

class RequirementJournaled(Requirement, JournaledObject):
    """
    Derives anything from Copyset plus journals all actions.
    Internally CopysetJournaled has a map of undomethods and references to objects that methods should be executed upon.
    If undo is called the journal stack is executed from top to buttom (LIFO) order.
    """
    __logStrLevel__ = "RequirementJournaled"

    def __init__(self, element, doc):
        Requirement.__init__(self, element, doc)
        JournaledObject.__init__(self)
        self.__journal__=list()
        self.__undomap__=dict()

    def undoCopy(self):
        """
        just calls replayJournal
        """
        self.replayJournal()

###################################
# $Log: ComRequirement.py,v $
# Revision 1.1  2006-07-19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.4  2006/06/30 12:40:29  marc
# added undo
#
# Revision 1.3  2006/06/29 13:37:15  marc
# *** empty log message ***
#
# Revision 1.2  2006/06/29 12:34:22  marc
# added Factory and changed classname.
#
# Revision 1.1  2006/06/29 12:20:28  marc
# initial revision
#