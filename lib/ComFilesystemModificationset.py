""" Comoonics filesystem modificationset module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFilesystemModificationset.py,v 1.2 2006-06-30 12:42:22 mark Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComFilesystemModificationset.py,v $

import xml.dom
import exceptions
from xml import xpath
from xml.dom.ext import PrettyPrint
import os

from ComExceptions import *
from ComModificationset import Modificationset
from ComDevice import Device
import ComFileSystem
from ComFileSystem import FileSystem
from ComMountpoint import MountPoint
import ComLog

log=ComLog.getLogger("Modificationset")

class FilesystemModificationset(Modificationset):
    """ Base Class for all source and destination objects"""
    def __init__(self, element, doc):
        Modificationset.__init__(self, element, doc)
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
        self.modifications=xpath.Evaluate('device/modification', element)
        self.cwd = os.getcwd()
        log.debug("Filesystemodificationset CWD: " + self.cwd)
    
    def doPre(self):
        # mount Filesystem
        if not self.device.isMounted():
            self.filesystem.mount(self.device, self.mountpoint)
            self.umountfs=True
        os.chdir(self.mountpoint.getAttribute("name"))
        log.debug("CWD: " + os.getcwd())
        
    
    def doPost(self):
        os.chdir(self.cwd)
        #umount Filesystem
        if self.umountfs:
            self.filesystem.umountDir(self.mountpoint)
        log.debug("CWD: " + os.getcwd())
        
    def getModifications(self):
        return self.modifications

# $Log: ComFilesystemModificationset.py,v $
# Revision 1.2  2006-06-30 12:42:22  mark
# bug fixes
#
# Revision 1.1  2006/06/30 08:03:54  mark
# initial checkin
#
