"""Comoonics disk module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComDisk.py,v 1.10 2011-02-17 09:06:58 marc Exp $
#


__version__ = "$Revision: 1.10 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/ComDisk.py,v $

import os
import exceptions
import xml.dom
import time

from comoonics import ComSystem
from comoonics.ComDataObject import DataObject
from comoonics.ComExceptions import ComException
from comoonics import ComLog
from ComPartition import Partition
from ComLVM import LogicalVolume, VolumeGroup

CMD_SFDISK = "/sbin/sfdisk"
CMD_DD="/bin/dd"
CMD_DMSETUP = "/sbin/dmsetup"
CMD_KPARTX = "/sbin/kpartx"
OPTS_KPARTX = "-p p"

class Disk(DataObject):
    def __init__(self, element, doc=None):
        """ default Constructur """
        super(Disk, self).__init__(element, doc)

class StorageDisk(Disk):
    MAPPING_TAG_NAME="mapping"
    HOST_TAG_NAME="host"
    """ Disk represents a disk on a storage system """
    def __init__(self, element, doc=None):
        """ default constructur called by __new__ """
        super(StorageDisk, self).__init__(element, doc)
    def getHostNames(self, lun):
        """ returns all hostnames as list for the given lun """
        mappings=self.getElement().getElementsByTagName(self.MAPPING_TAG_NAME)
        if type(lun)==int:
            lun="%u" %(lun)
        hosts=list()
        for mapping in mappings:
            if mapping.getAttribute("lun")==lun:
                ehosts=mapping.getElementsByTagName(self.HOST_TAG_NAME)
                for ehost in ehosts:
                    hosts.append(ehost.getAttribute("name"))
        return hosts

    def getLuns(self):
        """ returns all defined luns in this disk """
        luns=list()
        mappings=self.getElement().getElementsByTagName(self.MAPPING_TAG_NAME)
        for mapping in mappings:
            luns.append(mapping.getAttribute("lun"))
        return luns

class HostDisk(Disk):
    log=ComLog.getLogger("comoonics.ComDisk.HostDisk")
    LABEL_PREFIX="LABEL="
    TAGNAME="disk"
    class DeviceNameResolver(object):
        key=None
        def getKey(self):
            return self.key
        def resolve(self, value):
            pass

    class DeviceNameResolverError(ComException):
        pass
    resolver=dict()

    def __init__(self, *params):
        """ Disk represents a raw disk
            Possible constructors:
            __init__(self, element, doc=None)  type(element)=Node
            __init__(self, name, doc=None) type(name)==str
        """
        if len(params)==1:
            doc=xml.dom.getDOMImplementation().createDocument(None, self.TAGNAME, None)
        elif len(params)==2:
            doc=params[1]
        else:
            raise exceptions.TypeError("""Wrong number of arguments to constructor of HostDisk.
   Either __init__(self, element, doc=None) or
          __init__(self, name, doc=None) are supported.""")

        if isinstance(params[0], basestring):
            element=doc.createElement(self.TAGNAME)
            element.setAttribute("name", params[0])
        else:
            element=params[0]
        super(HostDisk, self).__init__(element, doc)
        self.log.debug("__init__")
        self.devicename=None
        self.stabilizedfile="/proc/partitions"
        self.stabilizedtype="hash"
        self.stabilizedgood=2

    def is_lvm(self):
        return hasattr(self, "volumegroup") and hasattr(self, "logicalvolume")

    def is_lvm_activated(self):
        return self.is_lvm() and self.logicalvolume.isActivated()

    def lvm_vg_activate(self):
        self.volumegroup.activate()

    def lvm_vg_deactivate(self):
        self.volumegroup.deactivate()

    def getLog(self):
        return self.log

    def exists(self):
        return ComSystem.execMethod(os.path.exists, self.getDeviceName())

    def sameSize(self):
        """ 
        """
        return self.getAttributeBoolean("samesize", False)

    def getDeviceName(self):
        """ returns the Disks device name (e.g. /dev/sda) """
        if hasattr(self, "devicename") and self.devicename != None:
            return self.devicename
        else:
            return self.getAttribute("name")

    def getDevicePath(self):
        return self.getDeviceName()

    def getSize(self):
        """ returns the size of the disk in sectors"""
        pass

    def refByLabel(self):
        """
        is disk referenced by Label? returns True or False
        Format <disk name="LABEL=..."/>
        """
        return self.getDeviceName()[:len(self.LABEL_PREFIX)]==self.LABEL_PREFIX

    def resolveDeviceNameByKeyValue(self, key, value):
        """
        resolves a device name by searching for a method to resolve it by key and the resolve via value as
        Parameter
        """
        if self.resolver.has_key(key):
            name=self.resolver[key].resolve(value)
            if name and name != "":
                self.devicename=name
            else:
                raise HostDisk.DeviceNameResolverError("Could not resolve device \"%s\" for type \"%s\"" %(value, key))
        else:
            raise HostDisk.DeviceNameResolverError("Could not find resolver for device referrenced by %s=%s" %(key, value))

    def resolveDeviceName(self):
        """
        resolves the given devicenames and returns a list of executed commands.
        """
        journal_cmds=list()
        if len(self.getDeviceName().split("="))==2:
            (key, value)=self.getDeviceName().split("=")[:2]
            self.resolveDeviceNameByKeyValue(key, value)
        if LogicalVolume.isValidLVPath(self.getDeviceName()):
            self.initLVM()
            self.lvm_activated=False
            if self.getAttribute("options", "") != "skipactivate" and not self.is_lvm_activated():
                self.lvm_vg_activate()
                self.lvm_activated=True
                journal_cmds.append("lvm_vg_activate")
        return journal_cmds

    def initLVM(self):
        (vgname, lvname)=LogicalVolume.splitLVPath(self.getDeviceName())
        self.volumegroup=VolumeGroup(vgname, self.getDocument())
        self.logicalvolume=LogicalVolume(lvname, self.volumegroup, self.getDocument())
        self.volumegroup.init_from_disk()
        self.logicalvolume.init_from_disk()

    def initFromDisk(self):
        """ reads partition information from the disk and fills up DOM
        with new information
        """
        HostDisk.log.debug("initFromDisk()")

        #FIXME: create LabelResolver
        if self.refByLabel():
            pass
        if not self.exists():
            raise ComException("Device %s not found or no valid device!" % self.getDeviceName())
        import ComParted

        phelper=ComParted.getInstance()
        for partition in phelper.initFromDisk(self.getDeviceName()):
            self.appendChild(Partition(partition, self.getDocument()))
            
    def restore(self):
        if hasattr(self, "lvm_activated") and self.lvm_activated:
            self.lvm_vg_deactivate()

    def createPartitions(self):
        """ creates new partition table """
        if not self.exists():
            raise ComException("Device %s not found" % self.getDeviceName())
        import ComParted

        phelper=ComParted.getInstance()
        phelper.createPartitions(self.getDeviceName(), self.getAllPartitions(), self.sameSize())
        self.stabilize()

    def stabilize(self):
        self.commit()

        #dev.sync()
        #dev.close()

        # run partx if the device is a multipath device
        self.log.debug("ComHostDisk: checking for multipath devices")
        if self.isDMMultipath():
            self.log.debug("Device %s is a dm_multipath device, adding partitions" %self.getDeviceName())
            __cmd=CMD_KPARTX + " " + OPTS_KPARTX +" -d " + self.getDeviceName()
            try:
                __ret = ComSystem.execLocalOutput(__cmd, True, "")
                self.log.debug(__ret)
                __cmd=CMD_KPARTX + " " + OPTS_KPARTX + " -a " + self.getDeviceName()
                __ret = ComSystem.execLocalOutput(__cmd, True, "")
                self.log.debug(__ret)
                #FIXME: crappy fix to give os some time to create devicefiles.
                time.sleep(10)
            except ComSystem.ExecLocalException, ele:
                ComLog.debugTraceLog(self.log)
                self.log.debug("Could not execute %s. Error %s" %(ele.cmd, ele))

    def isDMMultipath(self):
        if not os.path.exists(CMD_DMSETUP):
            return False
        __cmd="%s table %s --target=multipath 2>/dev/null | grep multipath &>/dev/null"  % (CMD_DMSETUP, self.getDeviceName())
        try:
            ComSystem.execLocalOutput(__cmd, True, "")
            return True
        except ComSystem.ExecLocalException: 
            return False

    def getAllPartitions(self):
        parts=[]
        for elem in self.element.getElementsByTagName(Partition.TAGNAME):
            parts.append(Partition(elem, self.document))
        return parts


    def savePartitionTable(self, filename):
        """ saves the Disks partition table in sfdisk format to <filename>
        Throws ComException on error
        """
        __cmd = self.getDumpStdout() + " > " + filename
        __ret = ComSystem.execLocalOutput(__cmd, True, "saved partition table")
        self.log.debug("savePartitionTable( " + filename + "):\n " + __ret)

    def getPartitionTable(self):
        try:
            rv = ComSystem.execLocalOutput(self.getDumpStdout(), True, "getPartitionTable")
            return rv
        except ComSystem.ExecLocalException:
            return list()

    def getDumpStdout(self):
        """ returns the command string for dumping partition information
        see sfdisk -d
        """
        return CMD_SFDISK + " -d " + self.getDeviceName()

    def hasPartitionTable(self):
        """ checks wether the disk has a partition table or not """
        #__cmd = CMD_SFDISK + " -Vq " + self.getDeviceName() + " >/dev/null 2>&1"
        #if ComSystem.execLocal(__cmd):
        #    return False
        #return True
        __cmd = CMD_SFDISK + " -l " + self.getDeviceName()
        rc, std, err = ComSystem.execLocalGetResult(__cmd, True)
        if rc!=0:
            return False
        if (" ".join(err).upper().find("ERROR")) > 0:
            return False
        return True



    def deletePartitionTable(self):
        """ deletes the partition table """
        __cmd = CMD_DD + " if=/dev/zero of=" + self.getDeviceName() + " bs=512 count=2 >/dev/null 2>&1"
        if ComSystem.execLocal(__cmd):
            return False
        return self.rereadPartitionTable()

    def rereadPartitionTable(self):
        """ rereads the partition table of a disk """
        __cmd = CMD_SFDISK + " -R " + self.getDeviceName() + " >/dev/null 2>&1"
        if ComSystem.execLocal(__cmd):
            self.commit()
            return False
        else:
            self.commit()
            return True

    def restorePartitionTable(self, filename):
        """ writes partition table stored in <filename> to Disk.
        Note, that the format has to be sfdisk stdin compatible
        see sfdisk -d
        Throws ComException on error
        """
        __cmd = self.getRestoreStdin(True) + " < " + filename
        __out = ComSystem.execLocalOutput(__cmd, True, "")
        self.log.debug("restorePartitionTable( " + filename + "):\n " + __out)
        self.commit()

    def getRestoreStdin(self, force=False):
        """ returns command string to restore a partition table
        config from sfdisk stdin
        see sfdisk < config
        """
        __cmd = [CMD_SFDISK]
        if force:
            __cmd.append("--force")
        __cmd.append(self.getDeviceName())
        return " ".join(__cmd)

    def commit(self):
        """ Method that waits for synchronized commits on underlying devices
        """
        try:
            from comoonics.tools import stabilized
            stabilized.stabilized(file=self.stabilizedfile, type=self.stabilizedtype, good=self.stabilizedgood)
        except ImportError:
            warnings.warn("Could not import a stabilization functionality to synchronized changed disk devices with depending kernel. You might think of installing comoonics-storage-py.")

# Initing the resolvers
try:
    from comoonics.scsi.ComSCSIResolver import SCSIWWIDResolver, FCTransportResolver
    res=SCSIWWIDResolver()
    HostDisk.resolver[res.getKey()]=res
    res=FCTransportResolver()
    HostDisk.resolver[res.getKey()]=res
except ImportError:
    import warnings
    warnings.warn("Could not import SCSIWWIDResolver and FCTransportResolver. Limited functionality for HostDisks might be available.")
