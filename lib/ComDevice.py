"""Comoonics disk module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComDevice.py,v 1.1 2006-06-23 07:56:24 mark Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComDevice.py,v $
# $Log: ComDevice.py,v $
# Revision 1.1  2006-06-23 07:56:24  mark
# initial checkin (stable)
#

import os
import exceptions

import ComSystem
from ComExceptions import *
from ComDisk import Disk

class Device(Disk):
    def __init__(self, device):
        Disk.__init__(self,device)
