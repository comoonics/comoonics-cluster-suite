""" Comoonics filecopy copyset module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFilesystemCopyset.py,v 1.4 2006-07-06 08:59:07 mark Exp $
#


__version__ = "$Revision: 1.4 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComFilesystemCopyset.py,v $

import xml.dom
import exceptions
from xml import xpath

import ComCopyObject
from ComCopyset import *
from ComDisk import Disk
from ComExceptions import *
import ComSystem
import ComLog

CMD_RSYNC="/usr/bin/rsync"

__logStrLevel__ = "FilesystemCopyset"
class FilesystemCopyset(Copyset):
    def __init__(self, element, doc):
        Copyset.__init__(self, element, doc)
        try:
            __source=xpath.Evaluate('source', element)[0]
            self.source=ComCopyObject.getCopyObject(__source, doc)
        except Exception:
            raise ComException("source for copyset not defined")
        try:
            __dest=xpath.Evaluate('destination', element)[0]
            self.destination=ComCopyObject.getCopyObject(__dest, doc)
        except Exception:
            raise ComException("destination for copyset not defined")
        
    def doCopy(self):
        # do everything
        self.prepareSource()
        self.copyFsAttributes()
        self.prepareDest()
        __cmd = self.getCopyCommand()
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        ComLog.getLogger("Copyset").debug("doCopy: "  + __cmd +" "+ __ret) 
        self.postSource()
        self.postDest()
        if __rc:
            # TODO
            # check for specific error codes
            #raise ComException(__cmd + __ret)
            ComLog.getLogger("Copyset").warning("doCopy: " + __ret)
    
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
        self.destination.cleanupDest()
    
    def prepareDest(self):
        # do things like mkfs, mount
        self.destination.prepareAsDest()

    def copyFsAttributes(self):
        """ copy all Attributes from source to dest that are not defined
        in dest
        """
        # save dest attributes
        __attr = self.destination.getFileSystem().getElement().attributes
        # copy all source fs info to dest
        self.destination.setFileSystem(self.source.getFileSystem())
        # restore saved attibutes from dest
        self.destination.getFileSystem().setAttributes(__attr)

    def getCopyCommand(self):
        __cmd=CMD_RSYNC
        __cmd+=" -aux --delete "
        __cmd+=self.source.getMountpoint().getAttribute("name")
        __cmd+="/ "
        __cmd+=self.destination.getMountpoint().getAttribute("name")
        __cmd+="/"
        return __cmd

# $Log: ComFilesystemCopyset.py,v $
# Revision 1.4  2006-07-06 08:59:07  mark
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