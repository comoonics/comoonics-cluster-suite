""" Comoonics filesystem copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFilesystemCopyObject.py,v 1.3 2006-12-08 09:39:28 mark Exp $
#


__version__ = "$Revision: 1.3 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComFilesystemCopyObject.py,v $

from xml import xpath

from comoonics.ComDevice import Device
from comoonics import ComFileSystem
from comoonics.ComFileSystem import FileSystem
from comoonics.ComMountpoint import MountPoint
from ComCopyObject import CopyObjectJournaled
from comoonics.ComExceptions import *


class FilesystemCopyObject(CopyObjectJournaled):
    __logStrLevel__="FilesystemCopyObject"

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
        self.setFileSystemElement(filesystem.getElement())

    def setFileSystemElement(self, element):
        __parent=self.filesystem.getElement().parentNode
        __newnode=element.cloneNode(True)
        __oldnode=self.filesystem.getElement()
        self.filesystem.setElement(__newnode)
        # only replace attributes
        try:
            __parent.replaceChild(__newnode, __oldnode)
        except Exception, e:
            ComLog.getLogger(FilesystemCopyObject.__logStrLevel__).warning(e)

    def prepareAsSource(self):
        # Check for mounted
#        ComLog.getLogger(self.__logStrLevel__).debug("Name %s options: %s" %(self, self.device.getAttribute("options", "")))
        if self.device.getAttribute("options", "") != "skipmount" and not self.device.isMounted(self.mountpoint):
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

    def getMetaData(self):
        ''' returns the metadata element '''
        return self.device.getElement()


    def updateMetaData(self, element):
        ''' updates meta data information '''
        """ copy all Attributes from source to dest that are not defined
        in dest
        """
        # get filesystem element
        try:
            __sfilesystem=element.getElementsByTagName("filesystem")[0]
        except Exception:
            raise ComException("filesystem for metadata not defined")

        # save dest attributes
        __attr = self.getFileSystem().getElement().attributes
        # copy all source fs info to dest
        self.setFileSystemElement(__sfilesystem)
        # restore saved attibutes from dest
        self.getFileSystem().setAttributes(__attr)

# $Log: ComFilesystemCopyObject.py,v $
# Revision 1.3  2006-12-08 09:39:28  mark
# added support for generic CopyObject Framework (Archiv)
#
# Revision 1.2  2006/10/19 10:02:05  marc
# added skipmount
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.5  2006/07/06 15:09:10  mark
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