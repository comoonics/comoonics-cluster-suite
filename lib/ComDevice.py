"""Comoonics disk module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComDevice.py,v 1.4 2006-06-28 17:23:19 mark Exp $
#


__version__ = "$Revision: 1.4 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComDevice.py,v $

import os
import exceptions

import ComSystem
from ComExceptions import *
from ComDisk import Disk
import ComUtils

class Device(Disk):
    def __init__(self, element, doc):
        Disk.__init__(self,element, doc)

    def isMounted(self):
        if self.scanMountPoint()[0] != "":
            return 1
        return 0

    def scanMountPoint(self):
        """ returns first mountpoint of device ang fstype if mounted
        raises ComException if its not mounted
        """
        if not os.path.isfile("/proc/mounts"):
            raise ComException("/proc/mounts not found.")

        [ i, o ]=os.popen2("cat /proc/mounts")
        lines=o.readlines()
        exp="^" + self.getDevicePath() + " (/.*?) .*"
        self.getLog().debug(exp)
        mp=ComUtils.grepInLines(lines, exp)
        if len(mp) == 0:
            return ["", ""]
        exp="^" + self.getDevicePath() + " " + mp[0] + " (.*?) .*"
        self.getLog().debug(exp)
        fs=ComUtils.grepInLines(lines, exp)
        if len(fs) == 0:
            return [None, None]
        return [mp[0], fs[0]]

        

# $Log: ComDevice.py,v $
# Revision 1.4  2006-06-28 17:23:19  mark
# modified to use DataObject
#
# Revision 1.3  2006/06/23 16:16:34  mark
# added mountpoint functions
#
# Revision 1.2  2006/06/23 12:01:24  mark
# moved Log to bottom
#
# Revision 1.1  2006/06/23 07:56:24  mark
# initial checkin (stable)
#
