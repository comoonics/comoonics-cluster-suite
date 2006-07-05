""" Comoonics partition copyset module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComPartitionCopyset.py,v 1.4 2006-07-05 12:30:02 mark Exp $
#


__version__ = "$Revision: 1.4 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComPartitionCopyset.py,v $

import os
import xml.dom
import exceptions
from xml import xpath

from ComCopyset import *
from ComDisk import Disk
from ComExceptions import *
import ComSystem

class PartitionCopyset(CopysetJournaled):
    def __init__(self, element, doc):
        CopysetJournaled.__init__(self, element, doc)
        try:
            __source=xpath.Evaluate('source/disk', element)[0]
            self.source=Disk(__source, doc)
        except Exception:
            raise ComException("source for copyset not defined")
        try:
            __dest=xpath.Evaluate('destination/disk', element)[0]
            self.destination=Disk(__dest, doc)
        except Exception:
            raise ComException("destination for copyset not defined")
        self.addToUndoMap(self.source.__class__.__name__, "savePartitionTable", "restorePartitionTable")
        self.addToUndoMap(self.source.__class__.__name__, "noPartitionTable", "deletePartitionTable")
        
    def doCopy(self):
        __tmp=os.tempnam("/tmp")
        if self.destination.hasPartitionTable():
            self.destination.savePartitionTable(__tmp)
            self.journal(self.destination, "savePartitionTable", __tmp)
        else:
            self.journal(self.destination, "noPartitionTable")
        if self.source.hasPartitionTable():
            __cmd = self.source.getDumpStdout() 
            __cmd += " | "
            __cmd += self.destination.getRestoreStdin(True)
            __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
            ComLog.getLogger("Copyset").debug(__cmd + ": " + __ret)
            if __rc != 0:
                raise ComException(__cmd + __ret)
        else:
            if not self.destination.deletePartitionTable():
                raise ComException("Partition table on device %s coud not be deleted", 
                                   self.destination.getDeviceName())
    
        

# $Log: ComPartitionCopyset.py,v $
# Revision 1.4  2006-07-05 12:30:02  mark
# added --force to partition copy
#
# Revision 1.3  2006/07/03 14:32:38  mark
# added undo
#
# Revision 1.2  2006/07/03 09:28:17  mark
# added support for empty partition tables
#
# Revision 1.1  2006/06/28 17:25:16  mark
# initial checkin (stable)
#