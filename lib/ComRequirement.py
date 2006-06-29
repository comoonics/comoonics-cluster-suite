""" Comoonics copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id: ComRequirement.py,v 1.1 2006-06-29 12:20:28 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComRequirement.py,v $

from ComDataObject import DataObject

class ComRequirement(DataObject):
    """
    Requirement baseclass is responsible for resolving requirements needed for the copy or modificationsets.
    """
    
    """
    Static methods and objects/attributes
    """
    __logStrLevel__ = "LVMCopyObject"

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
# Revision 1.1  2006-06-29 12:20:28  marc
# initial revision
#