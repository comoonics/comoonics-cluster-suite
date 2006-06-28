""" Comoonics copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComCopyObject.py,v 1.1 2006-06-28 17:25:16 mark Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComCopyObject.py,v $

from ComDataObject import DataObject

def getCopyObject(element, doc):
    """ Factory function to create Copy Objects"""
    __type=element.getAttribute("type")
    if __type == "filesystem":
        from ComFilesystemCopyObject import FilesystemCopyObject
        return FilesystemCopyObject(element, doc)
 
        

class CopyObject(DataObject):
    """ Base Class for all source and destination objects"""
    def __init__(self, element, doc):
        DataObject.__init__(self, element, doc)
        
    def prepareAsSource(self):
        pass
    
    def cleanupSource(self):
        pass
    
    def cleanupDest(self):
        pass
    
    def prepareAsDest(self):
        pass
        

# $Log: ComCopyObject.py,v $
# Revision 1.1  2006-06-28 17:25:16  mark
# initial checkin (stable)
#