""" Comoonics partition copyset module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComPartitionCopyset.py,v 1.2 2006-07-03 09:28:17 mark Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComPartitionCopyset.py,v $

import xml.dom
import exceptions
from xml import xpath

from ComCopyset import *
from ComDisk import Disk
from ComExceptions import *
import ComSystem

class PartitionCopyset(Copyset):
    def __init__(self, element, doc):
        Copyset.__init__(self, element, doc)
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
        
    def doCopy(self):
        if self.source.hasPartitionTable():
            __cmd = self.source.getDumpStdout() 
            __cmd += " | "
            __cmd += self.destination.getRestoreStdin()
            __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
            ComLog.getLogger("Copyset").debug(__cmd + ": " + __ret)
            if __rc != 0:
                raise ComException(__cmd + __ret)
        else:
            if not self.destination.deletePartitionTable():
                raise ComException("Partition table on device %s coud not be deleted", 
                                   self.destination.getDeviceName())
    

# $Log: ComPartitionCopyset.py,v $
# Revision 1.2  2006-07-03 09:28:17  mark
# added support for empty partition tables
#
# Revision 1.1  2006/06/28 17:25:16  mark
# initial checkin (stable)
#