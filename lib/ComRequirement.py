""" Comoonics Requirement class


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id: ComRequirement.py,v 1.3 2006-06-29 13:37:15 marc Exp $
#


__version__ = "$Revision: 1.3 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComRequirement.py,v $

from ComDataObject import DataObject
from ComExceptions import ComException

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

###################################
# $Log: ComRequirement.py,v $
# Revision 1.3  2006-06-29 13:37:15  marc
# *** empty log message ***
#
# Revision 1.2  2006/06/29 12:34:22  marc
# added Factory and changed classname.
#
# Revision 1.1  2006/06/29 12:20:28  marc
# initial revision
#