"""Comoonics copyset module


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id: ComCopyset.py,v 1.1 2006-07-19 14:29:15 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComCopyset.py,v $

import exceptions

from comoonics.ComDataObject import DataObject
from comoonics.ComExceptions import ComException
from comoonics import ComLog
from comoonics.ComJournaled import JournaledObject

def getCopyset(element, doc):
    """ Factory function to create Copyset Objects"""
    __type=element.getAttribute("type")
    if __type == "partition":
        from ComPartitionCopyset import PartitionCopyset
        return PartitionCopyset(element, doc)
    if __type == "lvm":
        from ComLVMCopyset import LVMCopyset
        return LVMCopyset(element, doc)
    if __type == "filesystem":
        from ComFilesystemCopyset import FilesystemCopyset
        return FilesystemCopyset(element, doc)
    if __type == "bootloader":
        from ComBootloaderCopyset import BootloaderCopyset
        return BootloaderCopyset(element, doc)
    raise exceptions.NotImplementedError()


class Copyset(DataObject):
    __logStrLevel__ = "Copyset"
    TAGNAME = "copyset"
    def __init__(self, element, doc):
        DataObject.__init__(self, element, doc)
        
    def doCopy(self):
        """starts the copy process"""
        pass
    
    def undoCopy(self):
        """ Tries to undo the copy if implemented"""
        pass
    
    def getSource(self):
        """returns the Source Object"""
        pass
            
    def getDestination(self):
        """ returns the Destination Object"""    
        pass

class CopysetJournaled(Copyset, JournaledObject):
    """
    Derives anything from Copyset plus journals all actions.
    Internally CopysetJournaled has a map of undomethods and references to objects that methods should be executed upon.
    If undo is called the journal stack is executed from top to buttom (LIFO) order.
    """
    __logStrLevel__ = "CopysetJournaled"

    def __init__(self, element, doc):
        Copyset.__init__(self, element, doc)
        JournaledObject.__init__(self)
        self.__journal__=list()
        self.__undomap__=dict()

    def undoCopy(self):
        """
        just calls replayJournal
        """
        self.replayJournal()
        
# $Log: ComCopyset.py,v $
# Revision 1.1  2006-07-19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.4  2006/06/30 12:39:46  marc
# added TAGNAME
#
# Revision 1.3  2006/06/30 08:29:51  marc
# added undoCopy method to Copyset
# added CopysetJournaled
#
# Revision 1.2  2006/06/29 13:49:47  marc
# added LVM stuff.
#
# Revision 1.1  2006/06/28 17:25:16  mark
# initial checkin (stable)
#