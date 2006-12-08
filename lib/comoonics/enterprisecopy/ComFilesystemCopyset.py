""" Comoonics filecopy copyset module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFilesystemCopyset.py,v 1.2 2006-12-08 09:39:51 mark Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComFilesystemCopyset.py,v $

import xml.dom
import exceptions
from xml import xpath

from ComCopyObject import CopyObject
from ComCopyset import *
from comoonics.ComDisk import Disk
from comoonics.ComExceptions import *
from comoonics import ComSystem
from comoonics import ComLog

from ComFilesystemCopyObject import FilesystemCopyObject
from ComArchiveCopyObject import ArchiveCopyObject

CMD_RSYNC="/usr/bin/rsync"

__logStrLevel__ = "FilesystemCopyset"
class FilesystemCopyset(Copyset):
    def __init__(self, element, doc):
        Copyset.__init__(self, element, doc)
        try:
            __source=xpath.Evaluate('source', element)[0]
            self.source=CopyObject(__source, doc)
        except Exception, e:
            ComLog.getLogger(__logStrLevel__).warning(e)
            raise ComException("source for copyset not defined")
        try:
            __dest=xpath.Evaluate('destination', element)[0]
            self.dest=CopyObject(__dest, doc)
        except Exception, e:
        #except None:
            print ("EXCEPTION: %s\n" %e)
            ComLog.getLogger(__logStrLevel__).warning(e)
            raise ComException("destination for copyset not defined")

    def doCopy(self):
        # do everything
        #stype=self.source.getAttribute("type")
        #dtype=self.dest.getAttribute("type")

        self.prepareSource()

        # Update MetaData
        self.dest.updateMetaData(self.source.getMetaData())

        self.prepareDest()

        # decide how to copy data
        self._copyData()

        self.postSource()
        self.postDest()

    def undoCopy(self):
        # simple undo we need to think about that again
        try:
            self.postSource()
        except Exception, e:
            ComLog.getLogger(__logStrLevel__).warning(e)
        try:
            self.postDest()
        except Exception, e:
            ComLog.getLogger(__logStrLevel__).warning(e)

    def prepareSource(self):
        #do things like fsck, mount
        # scan for fsconfig
        self.source.prepareAsSource()

    def postSource(self):
        self.source.cleanupSource()

    def postDest(self):
        self.dest.cleanupDest()

    def prepareDest(self):
        # do things like mkfs, mount
        self.dest.prepareAsDest()

#    def copyFsAttributes(self):
#        """ copy all Attributes from source to dest that are not defined
#        in dest
#        """
#        # save dest attributes
#        __attr = self.destination.getFileSystem().getElement().attributes
#        # copy all source fs info to dest
#        self.destination.setFileSystem(self.source.getFileSystem())
#        # restore saved attibutes from dest
#        self.destination.getFileSystem().setAttributes(__attr)

    def _getFSCopyCommand(self):
        __cmd=CMD_RSYNC
        __cmd+=" -aux --delete "
        __cmd+=self.source.getMountpoint().getAttribute("name")
        __cmd+="/ "
        __cmd+=self.dest.getMountpoint().getAttribute("name")
        __cmd+="/"
        return __cmd

    def _copyData(self):

        # 1. copy fs to fs
        if isinstance(self.source, FilesystemCopyObject):
            if isinstance(self.dest, FilesystemCopyObject):
                __cmd = self._getFSCopyCommand()
                __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
                ComLog.getLogger("Copyset").debug("doCopy: "  + __cmd +" "+ __ret)
                if __rc:
                    # TODO
                    # check for specific error codes
                    #raise ComException(__cmd + __ret)
                    ComLog.getLogger("Copyset").warning("doCopy: " + __ret)
                return __rc
        # 2. copy fs to archive
            if isinstance(self.dest, ArchiveCopyObject):
                try:
                    archive=self.dest.getDataArchive()
                    mountpoint=self.source.getMountpoint().getAttribute("name")
                    archive.createArchive("./", mountpoint)
                    return True
                #except Exception, e:
                except None, e:
                    ComLog.getLogger("Copyset").error(e)
                return False
        # 3. copy archive to fs
        if isinstance(self.source, ArchiveCopyObject):
            if isinstance(self.dest, FilesystemCopyObject):
                try:
                    archive=self.source.getDataArchive()
                    mountpoint=self.dest.getMountpoint().getAttribute("name")
                    archive.extractArchive(mountpoint)
                    return True
                except Exception, e:
                    ComLog.getLogger("Copyset").error(e)
                return False
        raise ComException("data copy % to % is not supported" \
                           % self.source.__name__, self.dest.__name__)

# $Log: ComFilesystemCopyset.py,v $
# Revision 1.2  2006-12-08 09:39:51  mark
# added support for generic CopyObject Framework
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.4  2006/07/06 08:59:07  mark
# Changed bahavior on rsync error codes see Bug #6
#
# Revision 1.3  2006/07/03 14:30:24  mark
# added undo
#
# Revision 1.2  2006/07/03 10:41:01  mark
# bug fix for rsync command
#
# Revision 1.1  2006/06/28 17:25:16  mark
# initial checkin (stable)
#