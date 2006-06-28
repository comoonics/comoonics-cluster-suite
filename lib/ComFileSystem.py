"""Comoonics filesystem module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFileSystem.py,v 1.3 2006-06-28 17:24:42 mark Exp $
#


__version__ = "$Revision: 1.3 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComFileSystem.py,v $

import os
import exceptions
import xml.dom

import ComSystem
import ComUtils
from ComExceptions import *
from ComDevice import Device
from ComDataObject import *

log=ComLog.getLogger("ComFileSystem")


CMD_MKFS="/sbin/mkfs"
CMD_GFS_MKFS="/sbin/gfs_mkfs"
CMD_GFS_TOOL="/sbin/gfs_tool"
CMD_MOUNT="/bin/mount"
CMD_UMOUNT="/bin/umount"
CMD_E2LABEL="/sbin/e2label"

def getFileSystemofType(type):
    raise exceptions.NotImplementedError()

    if type == "ext2":
        return ext2FileSystem()
    if type == "ext3":
        return ext3FileSystem()
    if type == "gfs":
        return gfsFileSystem()
    raise exceptions.NotImplementedError()


def getFileSystem(element, doc):
    """returns a FileSystem object that fits to the description in doc"""
    __type=element.getAttribute("type")
    if __type == "ext2":
        return ext2FileSystem(element, doc)
    if __type == "ext3":
        return ext3FileSystem(element, doc)
    if __type == "gfs":
        return gfsFileSystem(element, doc)
    raise exceptions.NotImplementedError()
       


class FileSystem(DataObject):
    TAGNAME="filesystem"
    def __init__(self, element, doc):
        """ element: DOMElement
        """
        # super
        DataObject.__init__(self, element, doc)

        #Check for mount options
        #__mopt = element.getElementsByTagName(MountOptions.TAGNAME)
        #if len(__mopt):
        #    self.mountOptions=MountOptions(__mopt[0], doc)
        #else:
        #    __node=doc.createElement(MountOptions.TAGNAME)
        #    element.appendChild(__node)
        #    self.mountOptions=MountOptions(__node, doc)
        # FIXME Do we need all of them ?
        self.formattable=0
        self.checked = 0
        self.name = ""
        self.linuxnativefs = 0
        self.maxSizeMB = 8 * 1024 * 1024
        self.maxLabelChars = 16
        self.partedFileSystemType = None
 

    def mount(self, device, mountpoint):
        __cmd = CMD_MOUNT + " -t " + self.getAttribute("type")+ " " + mountpoint.getOptionsString() + \
                " " + device.getDevicePath() + " " + mountpoint.getAttribute("name")
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        log.debug("mount:" + __cmd + ": " + __ret) 
        if __rc != 0:
            raise ComException(__cmd + __ret)
        

    def umountDev(self, device):
        __cmd = CMD_UMOUNT + " " + device.getDevicePath() 
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        log.debug("umount:" + __cmd + ": " + __ret) 
        if __rc != 0:
            raise ComException(__cmd + __ret)


    def umountDir(self, mountpoint):
        __cmd = CMD_UMOUNT + " " + mountpoint.getAttribute("name")
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        log.debug("umount: " + __cmd + ": " + __ret) 
        if __rc != 0:
            raise ComException(__cmd + __ret)


    def getName(self):
        return self.type

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
    
    def scanOptions(self, device, mountpoint=None):
        pass
        


class extFileSystem(FileSystem):
    def __init__(self, element, doc):
        FileSystem.__init__(self, element, doc)
        self.partedFileSystemType = None
        self.formattable = 1
        self.checked = 1
        self.linuxnativefs = 1
        self.maxSizeMB = 8 * 1024 * 1024
  
    def labelDevice(self, label, device):
        __devicePath = device.getDevicePath()
        __cmd = CMD_E2LABEL + " " + __devicePath + " " + label
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        log.debug("labelDevice: " +  __cmd + ": " + __ret) 
        if __rc:
            raise ComException(__cmd + __ret)

    def getLabel(self, device):
        __cmd = CMD_E2LABEL + " " + __devicePath
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        log.debug("getLabel: " + __cmd + ": " + __ret) 
        if __rc: 
            raise ComException(__cmd + __ret)
        return __ret
        
    def formatDevice(self, device):
        __devicePath = device.getDevicePath()
        __cmd = self.getMkfsCmd() + " " + __devicePath 
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        log.debug("formatDevice: "  + __cmd + ": " + __ret) 
        if __rc != 0:
            raise ComException(__cmd + __ret)

    def findLabel(self, label):
        """ try to find Device with label
        returns Device
        """
        __cmd="/sbin/findfs LABEL=" + label
        __rc, __path = execLocalGetResult(__cmd)
        if not rc:
            raise ComException("device with label " + label + "not found")
        return ComDevice.Device(__path[0])
        

class ext2FileSystem(extFileSystem):
    def __init__(self,element, doc):
        extFileSystem.__init__(self,element, doc)
        self.name = "ext2"
        self.setMkfsCmd(CMD_MKFS + " -t ext2 ")
        #self.partedFileSystemType = parted.file_system_type_get("ext2")
        #self.migratetofs = ['ext3']


class ext3FileSystem(extFileSystem):
    def __init__(self,element, doc):
        extFileSystem.__init__(self,element, doc)
        self.name = "ext3"
        self.setMkfsCmd(CMD_MKFS + " -t ext3 ")


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
        self.setMkfsCmd(CMD_GFS_MKFS + " -O ")



    def formatDevice(self, device):
        __cmd = self.getMkfsCmd() + self.getOptionsString() + device.getDevicePath() 
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        #self.getLog().debug("formatDevice: \n" , __cmd + __ret) 
        if __rc != 0:
            raise ComException(__cmd + __ret)

    def getOptionsString(self):
        __optstr=" -j "
        __optstr+= self.getAttribute("journals")
        __optstr+=" -p "
        __optstr+= self.getAttribute("lockproto")
        __optstr+=" -t "
        __optstr+= self.getAttribute("clustername")
        __optstr+=":"
        __optstr+= self.getAttribute("locktable")
        __optstr+=" -b "
        __optstr+= self.getAttribute("bsize")
        __optstr+=" "
        return __optstr

                
    def scanOptions(self, device, mountpoint=None):
        """ Scans a mountded gfs and puts the meta information into the DOM
        raises ComException
        """
        
        if mountpoint:
            __mountpoint=mountpoint.getAttribute("name")
        else:
            __mountpoint, fstype = device.scanMountPoint()
        if not __mountpoint:
            raise ComException("device " + device.getDevicePath() + " is not mounted.")
        __cmd = CMD_GFS_TOOL + " getsb " + __mountpoint  
        __rc, __ret = ComSystem.execLocalGetResult(__cmd)
        if __rc != 0:
            raise ComException(__cmd + __ret)

        __bsize=ComUtils.grepInLines(__ret, "  sb_bsize = ([0-9]*)")[0]
        log.debug("scan Options bsize: " + __bsize)
        self.setAttribute("bsize", __bsize)

        __lockproto=ComUtils.grepInLines(__ret, "  sb_lockproto = (.*)")[0]
        log.debug("scan Options lockproto: " + __lockproto)
        self.setAttribute("lockproto",__lockproto)

        __locktable=ComUtils.grepInLines(__ret, "  sb_locktable = .*?:(.*)")[0]
        log.debug("scan Options locktable: " + __locktable)
        self.setAttribute("locktable", __locktable)

        __clustername=ComUtils.grepInLines(__ret, "  sb_locktable = (.*?):.*")[0]
        log.debug("scan Options clustername: " +__clustername)
        self.setAttribute("clustername", __clustername)

        __cmd = CMD_GFS_TOOL + " df " + __mountpoint
        __rc, __ret = ComSystem.execLocalGetResult(__cmd)
        if __rc != 0:
            raise ComException(__cmd + __ret)
        __journals=ComUtils.grepInLines(__ret, "  Journals = ([0-9]+)")[0]
        log.debug("scan Options Journals: " +__journals)
        self.setAttribute("journals", __journals)
                                           

        
class MountPoint(DataObject):
    TAGNAME="mountpoint"
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
        
            
# $Log: ComFileSystem.py,v $
# Revision 1.3  2006-06-28 17:24:42  mark
# bug fixes
#
# Revision 1.2  2006/06/27 12:10:37  mark
# backup checkin
#
# Revision 1.1  2006/06/23 07:57:08  mark
# initial checkin (unstable)
#
