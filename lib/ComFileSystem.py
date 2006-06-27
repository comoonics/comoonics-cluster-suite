"""Comoonics filesystem module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFileSystem.py,v 1.2 2006-06-27 12:10:37 mark Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComFileSystem.py,v $
# $Log: ComFileSystem.py,v $
# Revision 1.2  2006-06-27 12:10:37  mark
# backup checkin
#
# Revision 1.1  2006/06/23 07:57:08  mark
# initial checkin (unstable)
#

import os
import exceptions
import xml.dom

import ComSystem
import ComUtils
from ComExceptions import *
from ComDevice import Device
from ComDataObject import *

log=ComLog.getLogger("ComFileSystem")

def getFileSystemofType(type):
    raise exceptions.NotImplementedError()

    if type == "ext2":
        return ext2FileSystem()
    if type == "ext3":
        return ext3FileSystem()
    if type == "gfs":
        return gfsFileSystem()
    raise exceptions.NotImplementedError()


def getFileSystem(element):
    """returns a FileSystem object that fits to the description in doc"""
    __type=element.getAttribute("type")
    if __type == "ext2":
        return ext2FileSystem(element)
    if __type == "ext3":
        return ext3FileSystem(element)
    if __type == "gfs":
        return gfsFileSystem(element)
    raise exceptions.NotImplementedError()
       


class FileSystem(DataObject):
    def __init__(self, element, doc):
        """ element: DOMElement
        """
        # super
        DataObject.__init__(self,element, doc)
        # Check for mount options
        __mopt = element.getElementsByTagName("mount_options")
        if len(__mopt):
            self.mountOptions=MountOptions(__mopt[0], doc)
        else:
            __node=doc.createElement("mount_options")
            element.appendChild(__node)
            self.mountOptions=MountOptions(__node, doc)
        # FIXME Do we need all of them ?
        self.formattable=0
        self.checked = 0
        self.name = ""
        self.linuxnativefs = 0
        self.maxSizeMB = 8 * 1024 * 1024
        self.maxLabelChars = 16
        self.partedFileSystemType = None
        self.log=ComLog.getLogger("FileSystem");
        self.xmlpath="*/filesystem/fs_config"


    def mount(self, device, mountpoint, readOnly=0, bindMount=0):
        __cmd = "/bin/mount -t " + self.mountOptions.getOptionsString()
        self.log.debug(__cmd)
        

    def umount(self, device, path):
        pass

    def getName(self, quoted = 0):
        pass

    def formatDevice(self, device):
        pass

    def labelDevice(self, device):
        pass

    def checkFs(self, device):
        pass

    def getLabel(self, device):
        pass

    def getBlockSize(self):
        __attr=self.getElement().xpath(self.xmlpath+"/@bsize")
        return __attr[0].value

    def isFormattable(self):
        return self.formattable

    def getMaxSizeMB(self):
        return self.maxSizeMB

    def setMkfsCmd(self, cmd):
        self.cmd_mkfs=cmd

    def getMkfsCmd(self):
        return self.cmd_mkfs

    def getLog(self):
        return self.log

    def scanDevice(self, device):
        """ scans the filesystem on device 
        device: ComDevice.Device
        """
        pass

        


class extFileSystem(FileSystem):
    def __init__(self, element, doc):
        FileSystem.__init__(self, element, doc)
        self.partedFileSystemType = None
        self.formattable = 1
        self.checked = 1
        self.linuxnativefs = 1
        self.maxSizeMB = 8 * 1024 * 1024
        #self.packages = [ "e2fsprogs" ]
        self.CMD_E2LABEL="/usr/sbin/e2label"

    def labelDevice(self, label, device):
        __devicePath = device.getDevicePath()
        __cmd = self.CMD_E2LABEL + " " + __devicePath + " " + label
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        self.getLog().debug("labelDevice: \n" , __cmd, __ret) 
        if __rc != 0:
            raise ComException(__cmd + __ret)
        
    def formatDevice(self, device):
        __devicePath = device.getDevicePath()
        __cmd = self.getMkfsCmd() + " " + __devicePath 
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        self.getLog().debug("formatDevice: \n" , __cmd, __ret) 
        if __rc != 0:
            raise ComException(__cmd + __ret)


class ext2FileSystem(extFileSystem):
    def __init__(self,element, doc):
        extFileSystem.__init__(self,element, doc)
        self.name = "ext2"
        self.setMkfsCmd("/sbin/mkfs.ext2")
        #self.partedFileSystemType = parted.file_system_type_get("ext2")
        #self.migratetofs = ['ext3']


class ext3FileSystem(extFileSystem):
    def __init__(self,element, doc):
        extFileSystem.__init__(self,element, doc)
        self.name = "ext3"
        self.setMkfsCmd("/sbin/mkfs.ext3")


class gfsFileSystem(FileSystem):
    def __init__(self, element, doc):
        FileSystem.__init__(self, element, doc )
        self.partedFileSystemType = None
        self.formattable = 1
        self.checked = 1
        self.linuxnativefs = 1
        self.maxSizeMB = 8 * 1024 * 1024
        #self.packages = [ "e2fsprogs" ]
        self.name="gfs"
        self.setMkfsCmd("/sbin/gfs_mkfs")
        self.GFS_TOOL_CMD="/sbin/gfs_tool"


    def formatDevice(self, device):
        __cmd = self.getMkfsCmd() + self.getOptionsString() + device.getDevicePath() 
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        self.getLog().debug("formatDevice: \n" , __cmd, __ret) 
        if __rc != 0:
            raise ComException(__cmd + __ret)

    def getOptionsString(self):
        __optstr=" -j "
        __optstr+= self.journals
        __optstr+=" -p "
        __optstr+= self.lockproto
        __optstr+=" -t "
        __optstr+= self.clustername
        __optstr+=":"
        __optstr+= self.locktable
        __optstr+=" -b "
        __optstr+= self.bsize
        __optstr+=" "
        return __optstr

                
    def scanOptions(self, device=None):
        if not device:
            device=Device(self.getElement().parentNode.getAttribute("path"))
        __mountpoint, fstype = device.getMountPoint()
        if __mountpoint == "":
            raise ComException("device " + device.getDevicePath() + " is not mounted.")
        __cmd = self.GFS_TOOL_CMD + " getsb " + __mountpoint  
        __rc, __ret = ComSystem.execLocalGetResult(__cmd)
        if __rc != 0:
            raise ComException(__cmd + __ret)

        __bsize=ComUtils.grepInLines(__ret, "  sb_bsize = ([0-9]*)")[0]
        self.getLog().debug("scan Options bsize: " + __bsize)
        self.bsize=__bsize

        __lockproto=ComUtils.grepInLines(__ret, "  sb_lockproto = (.*)")[0]
        self.getLog().debug("scan Options lockproto: " + __lockproto)
        self.lockproto=__lockproto

        __locktable=ComUtils.grepInLines(__ret, "  sb_locktable = .*?:(.*)")[0]
        self.getLog().debug("scan Options locktable: " + __locktable)
        self.locktable=__locktable

        __clustername=ComUtils.grepInLines(__ret, "  sb_locktable = (.*?):.*")[0]
        self.getLog().debug("scan Options clustername: " +__clustername)
        self.clustername=__clustername

        __cmd = self.GFS_TOOL_CMD + " df " + __mountpoint
        __rc, __ret = ComSystem.execLocalGetResult(__cmd)
        if __rc != 0:
            raise ComException(__cmd + __ret)
        __journals=ComUtils.grepInLines(__ret, "  Journals = ([0-9]+)")[0]
        self.getLog().debug("scan Options Journals: " +__journals)
        self.journals=__journals
                                           

        
class MountOptions(DataObject):
    def __init__(self, element, doc):
        DataObject.__init__(self, element, doc)

    def getOptionsString(self):
        __opts="-o "
        __attr=self.getElement().getElementsByTagName("option")
        if not (__attr.length):
            return __opts + "defaults"
        for i in range(__attr.length): 
            __opts+=__attr.item(i).getAttribute("name")
            if __attr.item(i).hasAttribute("value"):
                __opts+="="
                __opts+=__attr.item(i).getAttribute("value")
            if i+1 < __attr.length:
                __opts+=","
        return __opts
        
            
