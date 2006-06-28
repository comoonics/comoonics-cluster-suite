"""Comoonics copyset module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComCopyset.py,v 1.1 2006-06-28 17:25:16 mark Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComCopyset.py,v $

import exceptions

from ComDataObject import DataObject

def getCopyset(element, doc):
    """ Factory function to create Copyset Objects"""
    __type=element.getAttribute("type")
    if __type == "partition":
        from ComPartitionCopyset import PartitionCopyset
        return PartitionCopyset(element, doc)
    if __type == "lvm":
        return LvmCopyset(element, doc)
    if __type == "filesystem":
        from ComFilesystemCopyset import FilesystemCopyset
        return FilesystemCopyset(element, doc)
    if __type == "bootloader":
        from ComBootloaderCopyset import BootloaderCopyset
        return BootloaderCopyset(element, doc)
    raise exceptions.NotImplementedError()


class Copyset(DataObject):
    def __init__(self, element, doc):
        DataObject.__init__(self, element, doc)
        
    def doCopy(self):
        """starts the copy process"""
        pass
    
    def getSource(self):
        """returns the Source Object"""
        pass
            
    def getDestination(self):
        """ returns the Destination Object"""    
        pass
    
# $Log: ComCopyset.py,v $
# Revision 1.1  2006-06-28 17:25:16  mark
# initial checkin (stable)
#