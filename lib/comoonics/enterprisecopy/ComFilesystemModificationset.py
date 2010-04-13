""" Comoonics filesystem modificationset module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFilesystemModificationset.py,v 1.8 2010-04-13 13:25:35 marc Exp $
#


__version__ = "$Revision: 1.8 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComFilesystemModificationset.py,v $


from comoonics.ComExceptions import ComException
from ComModificationset import ModificationsetJournaled
from comoonics.storage.ComDevice import Device
from comoonics.storage import ComFileSystem
from comoonics.storage.ComMountpoint import MountPoint
from comoonics import ComLog, ComSystem

__logStrLevel__ = "comoonics.enterprisecopy.ComFilesystemModificationset.FilesystemModificationset"
log=ComLog.getLogger(__logStrLevel__)

class FilesystemModificationset(ModificationsetJournaled):
    """ Base Class for all source and destination objects"""
    def __init__(self, element, doc):
        import os
        ModificationsetJournaled.__init__(self, element, doc)
        __device=None
        try:
            __device=element.getElementsByTagName('device')[0]
            self.device=Device(__device, doc)
            __device=self.device.getElement()
        except Exception, e:
            ComLog.debugTraceLog(ComLog.getLogger(__logStrLevel__))
            raise ComException("Device for modificationset \"%s\" not defined. Error: %s." %(self.getAttribute("name", "unknown"), e))
        try:
            __fs=__device.getElementsByTagName('filesystem')[0]
            self.filesystem=ComFileSystem.getFileSystem(__fs, doc)
        except Exception, e:
            ComLog.debugTraceLog(ComLog.getLogger(__logStrLevel__))
            raise ComException("Filesystem for modificationset \"%s\" not defined. Error: %s." %(self.getAttribute("name", "unknown"), e))
        try:
            __mp=__device.getElementsByTagName('mountpoint')[0]
            self.mountpoint=MountPoint(__mp, doc)
        except Exception, e:
            ComLog.debugTraceLog(ComLog.getLogger(__logStrLevel__))
            raise ComException("Mountpoint for modificationset %s not defined" %(self.getAttribute("name", "unknown"), e))
        self.umountfs=False
        self.createModificationsList(__device.getElementsByTagName('modification'), doc)
        self.cwd = os.getcwd()
        log.debug("Modifications: %u" % len(self.modifications))
        log.debug("Filesystemodificationset CWD: " + self.cwd)
        self.addToUndoMap(self.filesystem.__class__.__name__, "mount", "umountDir")
        self.addToUndoMap(os.__name__, "chdir", "chdir")
        self.addToUndoMap(self.device.__class__.__name__, "lvm_vg_activate", "lvm_vg_deactivate")

    def doPre(self):
        import os
        # mount Filesystem
        for journal_command in self.device.resolveDeviceName():
            self.journal(self.device, journal_command)
        if not self.device.isMounted(self.mountpoint):
            self.filesystem.mount(self.device, self.mountpoint)
            self.journal(self.filesystem, "mount", [self.mountpoint])
        __cwd=os.getcwd()
        ComSystem.execMethod(os.chdir, self.mountpoint.getAttribute("name"))
        self.journal(os, "chdir", __cwd)
        log.debug("doPre() CWD: " + os.getcwd())
        super(FilesystemModificationset, self).doPre()

    def doPost(self):
        import os
        super(FilesystemModificationset, self).doPost()
        self.replayJournal()
        self.commitJournal()
        #os.chdir(self.cwd)
        #umount Filesystem
        #if self.umountfs:
        #    self.filesystem.umountDir(self.mountpoint)
        log.debug("doPost() CWD: " + os.getcwd())

    def getModifications(self):
        return self.modifications

# $Log: ComFilesystemModificationset.py,v $
# Revision 1.8  2010-04-13 13:25:35  marc
# - made to be simulated if need be
#
# Revision 1.7  2010/03/29 14:12:30  marc
# - fixed bug with referenced elements (refid)
# - extended error detection in constructor
#
# Revision 1.6  2010/03/08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.5  2010/02/09 21:48:24  mark
# added .storage path in includes
#
# Revision 1.4  2007/07/25 11:10:23  marc
# - better errormessages
# - loglevel
#
# Revision 1.3  2007/04/10 15:36:24  marc
# changed order for executing the requirements after mounting
#
# Revision 1.2  2007/03/26 07:58:49  marc
# - fixed a undo bug with chdir
# - calling parent methods for doPre/doPost (Requirements)
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.6  2006/07/06 15:09:33  mark
# Device.isMounted(mountpoint)
#
# Revision 1.5  2006/07/06 12:39:41  mark
# added journal support
#
# Revision 1.4  2006/07/03 12:47:44  marc
# more debugging.
#
# Revision 1.3  2006/07/03 08:28:46  marc
# updated to latest changes in baseclass
#
# Revision 1.2  2006/06/30 12:42:22  mark
# bug fixes
#
# Revision 1.1  2006/06/30 08:03:54  mark
# initial checkin
#
