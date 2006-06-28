""" Comoonics bootloader copyset module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComBootloaderCopyset.py,v 1.1 2006-06-28 17:25:16 mark Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComBootloaderCopyset.py,v $

import xml.dom
import exceptions
from xml import xpath

from ComCopyset import *
from ComBootDisk import BootDisk
from ComExceptions import *
import ComSystem

class BootloaderCopyset(Copyset):
    def __init__(self, element, doc):
        Copyset.__init__(self, element, doc)
        
        try:
            __dest=xpath.Evaluate('destination/disk', element)[0]
            self.destination=BootDisk(__dest, doc)
        except Exception:
            raise ComException("destination for copyset not defined")
        
    def doCopy(self):
        self.destination.installBootloader()
    

# $Log: ComBootloaderCopyset.py,v $
# Revision 1.1  2006-06-28 17:25:16  mark
# initial checkin (stable)
#