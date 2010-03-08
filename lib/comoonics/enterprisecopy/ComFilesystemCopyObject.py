""" Comoonics filesystem copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFilesystemCopyObject.py,v 1.11 2010-03-08 12:30:48 marc Exp $
#


__version__ = "$Revision: 1.11 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComFilesystemCopyObject.py,v $

from comoonics.storage.ComDevice import Device
from comoonics.storage import ComFileSystem
from comoonics.storage.ComMountpoint import MountPoint
from ComCopyObject import CopyObjectJournaled
from comoonics.ComExceptions import ComException
from comoonics import ComLog

class FilesystemCopyObject(CopyObjectJournaled):
    __logStrLevel__="FilesystemCopyObject"
    log=ComLog.getLogger(__logStrLevel__)

    # Base Class for all source and destination objects"""
    def __init__(self, element, doc):
        CopyObjectJournaled.__init__(self, element, doc)
        __device=None
        try:
            __device=element.getElementsByTagName("device")[0]
            self.device=Device(__device, doc)
        except Exception, e:
            ComLog.debugTraceLog(self.log)
            raise ComException("device for copyset not defined (%s)" %(e))
        try:
            __fs=__device.getElementsByTagName("filesystem")[0]
            self.filesystem=ComFileSystem.getFileSystem(__fs, doc)
        except Exception:
            raise ComException("filesystem for copyset not defined")
        try:
            __mp=__device.getElementsByTagName("mountpoint")[0]
            self.mountpoint=MountPoint(__mp, doc)
        except Exception:
            raise ComException("mountpoint for copyset not defined")
        FilesystemCopyObject.log.debug("__init__: fs: %s, device: %s" %(__device, __fs))
        self.umountfs=False
        self.addToUndoMap(self.filesystem.__class__.__name__, "mount", "umountDir")
        self.addToUndoMap(self.device.__class__.__name__, "lvm_vg_activate", "lvm_vg_deactivate")

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
        FilesystemCopyObject.log.debug("prepareAsSource: Name %s options: %s" %(self.device.getAttribute("name"), self.device.getAttribute("options", "")))
        for journal_command in self.device.resolveDeviceName():
            self.journal(self.device, journal_command)
        options=self.device.getAttribute("options", "")
        options=options.split(",")
        if options and "fsck" in options and not self.device.isMounted(self.mountpoint):
            self.filesystem.checkFs(self.device)
        if options and "skipmount" in options:
            FilesystemCopyObject.log.debug("prepareAsSource: skipping mount because specified")
        else:
            if not self.device.isMounted(self.mountpoint):
#                FilesystemCopyObject.log.debug("prepareAsSource: mounting %s, %s" %(self.device, self.mountpoint))
                self.filesystem.mount(self.device, self.mountpoint)
                self.journal(self.filesystem, "mount", [self.mountpoint])
            else:
                FilesystemCopyObject.log.debug("prepareAsSource: device is mounted, skipping")
            #self.umountfs=True
        # scan filesystem options
        self.filesystem.scanOptions(self.device, self.mountpoint)

    def prepareAsDest(self):
        # - mkfs
        # TODO add some intelligent checks
        FilesystemCopyObject.log.debug("prepareAsDest: Name %s options: %s" %(self, self.device.getAttribute("options", "")))
        for journal_command in self.device.resolveDeviceName():
            self.journal(self.device, journal_command)
#        if self.device.getAttribute("options", "") != "skipactivate" and not self.device.is_lvm_activated():
#            self.device.lvm_vg_activate()
#            self.journal(self.device, "lvm_vg_activate")
        self.filesystem.formatDevice(self.device)
        self.filesystem.mount(self.device, self.mountpoint)
        self.journal(self.filesystem, "mount", [self.mountpoint])

    def cleanupSource(self):
        self.log.debug("cleanupSource()")
        self.replayJournal()
        self.commitJournal()
        #if self.umountfs:
        #    self.filesystem.umountDir(self.mountpoint)
        #    self.umountfs=False

    def cleanupDest(self):
        self.log.debug("cleanupDest()")
        #self.filesystem.umountDir(self.mountpoint)
        self.replayJournal()
        self.commitJournal()

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
# Revision 1.11  2010-03-08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.10  2010/02/09 21:48:24  mark
# added .storage path in includes
#
# Revision 1.9  2007/10/16 15:26:24  marc
# - fixed BUG 27, break or warn when rsync error
#
# Revision 1.8  2007/09/13 09:35:55  marc
# - fixed Bug BZ#110
#   skipmount was wrongly checked
#
# Revision 1.7  2007/09/04 20:42:59  marc
# Fixed one part of BZ#101
#
# Revision 1.6.2.1  2007/09/04 20:41:19  marc
# Fixed one part of BZ#101
#
# Revision 1.6  2007/04/23 22:05:55  marc
# added fsck
#
# Revision 1.5  2007/04/04 12:51:30  marc
# MMG Backup Legato Integration:
# - moved prepareAsDest and added resolving
#
# Revision 1.4  2007/03/26 07:56:34  marc
# - added more logging
# - added support for resolveDeviceName (see ComDisk and ComDevice)
# - added support for activating a not activated LVM volume group
#
# Revision 1.3  2006/12/08 09:39:28  mark
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