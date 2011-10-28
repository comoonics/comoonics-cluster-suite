"""Comoonics disk module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComDevice.py,v 1.5 2011-02-15 14:54:52 marc Exp $
#


__version__ = "$Revision: 1.5 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/ComDevice.py,v $

import os

from ComDisk import HostDisk

class Device(HostDisk):
    TAGNAME="device"
    def __init__(self, element, doc, mountsfile="/proc/mounts"):
        HostDisk.__init__(self,element, doc)
        self.mountsfile=mountsfile

    def isMounted(self, mountpoint=None):
        """
        returns True if this device is already mounted.
        If mountpoint is also given, the mountpoint will be taken into account
        otherwise the devicename
        @param mountpoint: the mountpoint as DataObject
        @return: True or False. True if device is already mounted otherwise False
        """
        for line in self.getMountList():
            if not line or line == "":
                continue
            lineattrs=line.split(" ")
            # split the device if mountpoint is not set and give over to matchDevice 
            if lineattrs and len(lineattrs) > 1 and mountpoint and self.isMyMountpoint(lineattrs[1], mountpoint.getAttribute("name"), lineattrs[0]):
                return True
            elif not mountpoint and self.isMyDevice(lineattrs[0]):
                return True
        return False

    def isMyDevice(self, devicepath):
        """
        Returns True if the underlying device is the same device as the given one. For this os.path.samefile will be used.
        @param L{String}devicepath: The path to the device as string.
        @return: True or False. True if the given devicename is the same device as the underlying one.
        """
        if os.path.exists(self.getDevicePath()):
            return os.path.exists(devicepath) and os.path.samefile(devicepath, self.getDevicePath())
        else:
            return devicepath==self.getDevicePath()

    def isMyMountpoint(self, mountpoint1, mountpoint2, devicepath):
        """
        Returns true if the devicepath is the same as the underlying device and if the given mountpoint is the same file as the other one given
        and if both mountpoints exist physically.
        @param mountpoint1: string path to the first mountpoint
        @param mountpoint2: string path to the second mountpoint
        @param devicepath: the devicepath to be compared with the underlying one. 
        @return: True or False. True if either the devicepath exists or the mountpoints are of the same file. 
        """
        return self.isMyDevice(devicepath) and os.path.exists(mountpoint1) and os.path.exists(mountpoint2) and os.path.samefile(mountpoint1, mountpoint2)

    def scanMountPoint(self):
        """ returns first mountpoint of device and fstype if mounted
        returns None if not mounted
        """
        for line in self.getMountList():
            if not line or line == "":
                continue
            lineattrs=line.split(" ")
            if lineattrs and self.isMyDevice(lineattrs[0]):
                if lineattrs[1] and lineattrs[2]:
                    return [lineattrs[1], lineattrs[2]]
        return [None, None]

    """
    private methods
    """

    def getMountList(self):
        return file(self.mountsfile)

# $Log: ComDevice.py,v $
# Revision 1.5  2011-02-15 14:54:52  marc
# - changes for ecbase rebase to comoonics.ecbase package
#
# Revision 1.4  2011/02/08 13:05:56  marc
# - getMountList
#   - extended to use subprocess for python > 2.4
#
# Revision 1.3  2010/03/08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.2  2010/02/09 21:48:51  mark
# added .storage path in includes
#
# Revision 1.1  2009/09/28 15:13:36  marc
# moved from comoonics here
#
# Revision 1.3  2007/04/04 12:47:39  marc
# MMG Backup Legato Integration:
# -added Tagname
#
# Revision 1.2  2007/02/09 11:29:15  marc
# changed Disk to HostDisk
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.7  2006/07/06 15:10:32  mark
# added isMounted(mounpoint) resolves Bug #8
#
# Revision 1.6  2006/07/03 10:40:06  mark
# some bugfixes
#
# Revision 1.5  2006/06/29 08:16:56  mark
# bug fixes
#
# Revision 1.4  2006/06/28 17:23:19  mark
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
