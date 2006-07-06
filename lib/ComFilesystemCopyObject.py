""" Comoonics filesystem copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFilesystemCopyObject.py,v 1.5 2006-07-06 15:09:10 mark Exp $
#


__version__ = "$Revision: 1.5 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComFilesystemCopyObject.py,v $

from xml import xpath

from ComDevice import Device
import ComFileSystem
from ComFileSystem import FileSystem
from ComMountpoint import MountPoint
from ComCopyObject import CopyObjectJournaled
from ComExceptions import *         


class FilesystemCopyObject(CopyObjectJournaled):
    """ Base Class for all source and destination objects"""
    def __init__(self, element, doc):
        CopyObjectJournaled.__init__(self, element, doc)
        try:
            __device=xpath.Evaluate('device', element)[0]
            self.device=Device(__device, doc)
        except Exception:
            raise ComException("device for copyset not defined")
        try:    
            __fs=xpath.Evaluate('device/filesystem', element)[0]
            self.filesystem=ComFileSystem.getFileSystem(__fs, doc)
        except Exception:
            raise ComException("filesystem for copyset not defined")
        try:
            __mp=xpath.Evaluate('device/mountpoint', element)[0]
            self.mountpoint=MountPoint(__mp, doc)
        except Exception:
            raise ComException("mountpoint for copyset not defined")
        self.umountfs=False
        self.addToUndoMap(self.filesystem.__class__.__name__, "mount", "umountDir")
        
    def getFileSystem(self):
        return self.filesystem
    
    def getDevice(self):
        return self.device
    
    def getMountpoint(self):
        return self.mountpoint
    
    def setFileSystem(self, filesystem):
        __parent=self.filesystem.getElement().parentNode
        __newnode=filesystem.getElement().cloneNode(True)
        __oldnode=self.filesystem.getElement()
        self.filesystem.setElement(__newnode)
        __parent.replaceChild(__newnode, __oldnode)
        
    def prepareAsSource(self):   
        # Check for mounted
        if not self.device.isMounted(self.mountpoint):
            self.filesystem.mount(self.device, self.mountpoint)
            self.journal(self.filesystem, "mount", [self.mountpoint])
            #self.umountfs=True
        # scan filesystem options
        self.filesystem.scanOptions(self.device, self.mountpoint)
    
    def cleanupSource(self):
        self.replayJournal()
        self.commitJournal()
        #if self.umountfs:
        #    self.filesystem.umountDir(self.mountpoint)
        #    self.umountfs=False
    
    def cleanupDest(self):
        #self.filesystem.umountDir(self.mountpoint)
        self.replayJournal()
        self.commitJournal()
        
    def prepareAsDest(self):
        # - mkfs
        # TODO add some intelligent checks
        self.filesystem.formatDevice(self.device)
        self.filesystem.mount(self.device, self.mountpoint)
        self.journal(self.filesystem, "mount", [self.mountpoint])
        

# $Log: ComFilesystemCopyObject.py,v $
# Revision 1.5  2006-07-06 15:09:10  mark
# Device.isMounted(mountpoint)
#
# Revision 1.4  2006/07/06 11:53:11  mark
# added journal support
#
# Revision 1.3  2006/07/03 14:30:06  mark
# added undo
#
# Revision 1.2  2006/06/30 08:03:17  mark
# added ComMountPoint include
#
# Revision 1.1  2006/06/29 07:24:02  mark
# initial checkin
#