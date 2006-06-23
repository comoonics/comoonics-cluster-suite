"""Comoonics filesystem module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFileSystem.py,v 1.1 2006-06-23 07:57:08 mark Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComFileSystem.py,v $
# $Log: ComFileSystem.py,v $
# Revision 1.1  2006-06-23 07:57:08  mark
# initial checkin (unstable)
#

import os
import exceptions
from Ft.Xml import *

import ComSystem
from ComExceptions import *
from ComDevice import Device

def getFileSystem(type):
    if type == "ext2":
        return ext2FileSystem()
    if type == "ext3":
        return ext3FileSystem()
    if type == "gfs":
        return gfsFileSystem()
    raise exceptions.NotImplementedError()

class FileSystem:
    def __init__(self):
        self.formattable=0
        self.checked = 0
        self.name = ""
        self.linuxnativefs = 0
        self.maxSizeMB = 8 * 1024 * 1024
        self.maxLabelChars = 16
        self.defaultOptions = "defaults"
        self.partedFileSystemType = None
        self.log=ComLog.getLogger("FileSystem");

    def setParameterXML(self, xmlfile):
        pass

    def mount(self, device, mountpoint, readOnly=0, bindMount=0):
        pass

    def umount(self, device, path):
        pass

    def getName(self, quoted = 0):
        pass

    def formatDevice(self, fsconfig):
        pass

    def labelDevice(self, fsconfig):
        pass

    def checkFs(self, fsconfig):
        pass

    def getLabel(self, fsconfig):
        pass

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


class extFileSystem(FileSystem):
    def __init__(self):
        FileSystem.__init__(self)
        self.partedFileSystemType = None
        self.formattable = 1
        self.checked = 1
        self.linuxnativefs = 1
        self.maxSizeMB = 8 * 1024 * 1024
        #self.packages = [ "e2fsprogs" ]
        self.CMD_E2LABEL="/usr/sbin/e2label"

    def labelDevice(self, label, fsconfig):
        __devicePath = fsconfig.getDevicePath()
        __cmd = self.CMD_E2LABEL + " " + __devicePath + " " + label
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        self.getLog().debug("labelDevice: \n" , __cmd, __ret) 
        if __rc != 0:
            raise ComException(__cmd + __ret)
        
    def formatDevice(self, fsconfig):
        __devicePath = fsconfig.getDevicePath()
        __cmd = self.getMkfsCmd() + " " + __devicePath 
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        self.getLog().debug("formatDevice: \n" , __cmd, __ret) 
        if __rc != 0:
            raise ComException(__cmd + __ret)


class ext2FileSystem(extFileSystem):
    def __init__(self):
        extFileSystem.__init__(self)
        self.name = "ext2"
        self.setMkfsCmd("/sbin/mkfs.ext2")
        #self.partedFileSystemType = parted.file_system_type_get("ext2")
        #self.migratetofs = ['ext3']


class ext3FileSystem(extFileSystem):
    def __init__(self):
        extFileSystem.__init__(self)
        self.name = "ext3"
        self.setMkfsCmd("/sbin/mkfs.ext3")


class gfsFileSystem(FileSystem):
    def __init__(self):
        FileSystem.__init__(self)
        self.partedFileSystemType = None
        self.formattable = 1
        self.checked = 1
        self.linuxnativefs = 1
        self.maxSizeMB = 8 * 1024 * 1024
        #self.packages = [ "e2fsprogs" ]
        self.setMkfsCmd("/sbin/gfs_mkfs")

    

    def formatDevice(self, fsconfig):
        __devicePath = fsconfig.getDevicePath()
        __cmd = self.getMkfsCmd() + self.getOptionsString(fsconfig) + __devicePath 
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        self.getLog().debug("formatDevice: \n" , __cmd, __ret) 
        if __rc != 0:
            raise ComException(__cmd + __ret)

    def getOptionsString(self, fsconfig):
        __opts=fsconfig.getFileSystemOptions()
        
        __optstr=" -j "
        __optstr+=__opts.getAttributeNS(EMPTY_NAMESPACE, 'journals')
        __optstr+=" -p "
        __optstr+=__opts.getAttributeNS(EMPTY_NAMESPACE, 'lockproto')
        __optstr+=" -t "
        __optstr+=__opts.getAttributeNS(EMPTY_NAMESPACE, 'clustername')
        __optstr+=":"
        __optstr+=__opts.getAttributeNS(EMPTY_NAMESPACE, 'locktable')
        __optstr+=" -b "
        __optstr+=__opts.getAttributeNS(EMPTY_NAMESPACE, 'bsize')
        __optstr+=" "
        return __optstr
            


class FileSystemConfig:
    def __init__(self, dom):
        self.doc=dom

    def getDevicePath(self):
        __attr=self.doc.xpath("*/destination/device/@path")
        return __attr[0].value

    def getFileSystemType(self):
        __attr=self.doc.xpath("*/destination/filesystem/@type")
        return __attr[0].value

    def getFileSystemOptions(self):
        __node=self.doc.xpath("*/destination/filesystem/fs_config")
        return __node[0]


        
