""" Comoonics copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id: ComCopyObject.py,v 1.2 2006-06-29 13:52:49 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComCopyObject.py,v $

from ComDataObject import DataObject
from ComExceptions import ComException

class UnsupportedCopyObjectException(ComException): pass

def getCopyObject(element, doc):
    """ Factory function to create Copy Objects"""
    __type=element.getAttribute("type")
    if __type == "filesystem":
        from ComFilesystemCopyObject import FilesystemCopyObject
        return FilesystemCopyObject(element, doc)
    elif __type == "lvm":
        from ComLVMCopyObject import LVMCopyObject
        return LVMCopyObject(element, doc)
    else:
        raise UnsupportedCopyObjectException("Unsupported CopyObject type %s in element " % (__type, element.tagName))
         

class CopyObject(DataObject):
    """ Base Class for all source and destination objects"""
    __logStrLevel__ = "CopyObject"
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
# Revision 1.2  2006-06-29 13:52:49  marc
# added lvm stuff
#
# Revision 1.1  2006/06/28 17:25:16  mark
# initial checkin (stable)
#