"""Comoonics disk module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComDisk.py,v 1.6 2010-04-23 10:58:37 marc Exp $
#


__version__ = "$Revision: 1.6 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/ComDisk.py,v $

import os
import exceptions
import time
import xml.dom

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

class Disk(DataObject):
    """ Abstract Disk Baseclass that creates a disk a StorageDisk or HostDisk on demand """
    def __new__(cls, *args, **kwds):
        if cls==Disk:
            cls=StorageDisk
            element=args[0]
            name=element.getAttribute("name")
            if name.startswith("/"):
                cls=HostDisk
        return object.__new__(cls, *args, **kwds)
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
        try:
            self.initFromDiskParted()
        except ImportError:
            self.initFromDiskPartedCmd()
            
    def initFromDiskPartedCmd(self):
        if self.refByLabel():
            pass        

    def initFromDiskParted(self):
        import parted
        import ComParted

        phelper=ComParted.PartedHelper()
        dev=parted.PedDevice.get(self.getDeviceName())
        try:
            disk=parted.PedDisk.new(dev)
            partlist=phelper.get_primary_partitions(disk)
            for part in partlist:
                self.appendChild(Partition(part, self.getDocument()))
        except parted.error:
            HostDisk.log.debug("no partitions found")

    def restore(self):
        if hasattr(self, "lvm_activated") and self.lvm_activated:
            self.lvm_vg_deactivate()

    def createPartitions(self):
        """ creates new partition table """
        try:
            self.createPartitionsParted()
        except ImportError:
            self.createPartitionsPartedCmd()

    def createPartitionsPartedCmd(self):
        pass

    def createPartitionsParted(self):
        import parted
        import ComParted
        if not self.exists():
            raise ComException("Device %s not found" % self.getDeviceName())

        phelper=ComParted.PartedHelper()
        #IDEA compare the partition configurations for update
        #1. delete all aprtitions
        dev=parted.PedDevice.get(self.getDeviceName())

        try:
            disk=parted.PedDisk.new(dev)
            disk.delete_all()
        except parted.error:
            #FIXME use generic disk types
            disk=dev.disk_new_fresh(parted.disk_type_get("msdos"))

        # create new partitions
        for com_part in self.getAllPartitions():
            type=com_part.getPartedType()
            size=com_part.getPartedSizeOptimum(dev)
            flags=com_part.getPartedFlags()
            self.log.debug("creating partition: size: %i" % size )
            phelper.add_partition(disk, type, size, flags)

        disk.commit()

        #dev.sync()
        #dev.close()

        # run partx if the device is a multipath device
        self.log.debug("ComHostDisk: checking for multipath devices")
        if self.isDMMultipath():
            self.log.debug("Device %s is a dm_multipath device, adding partitions" %self.getDeviceName())
            __cmd=CMD_KPARTX + " -d " + self.getDeviceName()
            try:
                __ret = ComSystem.execLocalOutput(__cmd, True, "")
                self.log.debug(__ret)
                __cmd=CMD_KPARTX + " -a " + self.getDeviceName()
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
            return False
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

# $Log: ComDisk.py,v $
# Revision 1.6  2010-04-23 10:58:37  marc
# - rewrote execution parts to be better readable and more consistent
#
# Revision 1.5  2010/04/13 13:27:08  marc
# - made to be simulated if need be
#
# Revision 1.4  2010/03/08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.3  2010/02/09 21:48:51  mark
# added .storage path in includes
#
# Revision 1.2  2010/02/07 20:31:23  marc
# - seperated parted functionality
# - new imports
#
# Revision 1.1  2009/09/28 15:13:36  marc
# moved from comoonics here
#
# Revision 1.18  2007/09/13 14:16:21  marc
# - fixed Bug BZ#111, where partitions where not created when devicemapper in use
#
# Revision 1.17  2007/09/13 09:30:48  marc
# - logging
#
# Revision 1.16  2007/08/23 07:58:16  marc
#  - redirected output of dm_setup (#BZ 69) 2nd
#
# Revision 1.15  2007/07/31 15:16:22  marc
# - redirected output of dm_setup (#BZ 69)
#
# Revision 1.14  2007/04/11 14:45:22  mark
# added FIXME
#
# Revision 1.13  2007/04/04 12:48:44  marc
# MMG Backup Legato Integration:
# - small Bugfixed for LVM handling
# - added constructur with just a name instead of element
#
# Revision 1.12  2007/04/02 11:46:45  marc
# MMG Backup Legato Integration:
# - Journaling for vg_activation
#
# Revision 1.11  2007/03/26 08:27:03  marc
# - added more logging
# - added DeviceNameResolving
# - added resolvers for DeviceNameResolving
# - added lvm awareness (will autoactivate a non activated volume group)
#
# Revision 1.10  2007/03/14 15:07:15  mark
# workaround for bug bz#36
#
# Revision 1.9  2007/03/14 14:20:18  marc
# bugfix for constructor
#
# Revision 1.8  2007/02/27 15:55:15  mark
# added support for dm_multipath
#
# Revision 1.7  2007/02/12 15:43:12  marc
# removed some cvs things.
#
# Revision 1.6  2007/02/09 12:28:49  marc
# defined two implementations of disk
# - HostDisk (for disks in servers)
# - StorageDisks (for virtual disks on storagedevices)
#
# Revision 1.5  2006/12/14 09:12:53  mark
# bug fix
#
# Revision 1.4  2006/12/08 09:46:16  mark
# added full xml support.
# included parted libraries.
# added initFromDisk()
# added createPartitions()
#
# Revision 1.3  2006/09/11 16:47:48  mark
# modified hasPartitionTable to support gnbd devices
#
# Revision 1.2  2006/07/20 10:24:42  mark
# added getPartitionTable method
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.8  2006/07/05 12:29:34  mark
# added sfdisk --force option
#
# Revision 1.7  2006/07/03 13:02:51  mark
# moved devicefile check in exists() methos
#
# Revision 1.6  2006/07/03 09:27:12  mark
# added some methods for partition management
# added device check in constructor
#
# Revision 1.5  2006/06/29 08:17:16  mark
# added some comments
#
# Revision 1.4  2006/06/28 17:23:46  mark
# modified to use DataObject
#
# Revision 1.3  2006/06/23 16:17:16  mark
# removed devicefile check because there is a bug
#
# Revision 1.2  2006/06/23 11:58:32  mark
# moved Log to bottom
#
# Revision 1.1  2006/06/23 07:56:24  mark
# initial checkin (stable)
#
