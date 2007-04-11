"""Comoonics disk module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComDisk.py,v 1.14 2007-04-11 14:45:22 mark Exp $
#


__version__ = "$Revision: 1.14 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/Attic/ComDisk.py,v $

import os
import exceptions
import parted
import time
from xml.dom import Document, DOMImplementation

import ComSystem
from ComDataObject import DataObject
from ComExceptions import ComException
from comoonics import ComLog
import ComParted
from ComPartition import Partition
from comoonics.ComLVM import LogicalVolume, LinuxVolumeManager, VolumeGroup

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
    log=ComLog.getLogger("HostDisk")
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

    """ Disk represents a raw disk
        Possible constructors:
        __init__(self, element, doc=None)  type(element)=Node
        __init__(self, name, doc=None) type(name)==str
    """
    def __init__(self, *params):
        """ creates a Disk object
        """
        if len(params)==1:
            doc=DOMImplementation.createDocument(None, self.TAGNAME, None)
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
        return os.path.exists(self.getDeviceName())

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
        phelper=ComParted.PartedHelper()

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
        """ reads partition informatbbion from the disk and fills up DOM
        with new information
        """
        self.log.debug("initFromDisk()")

        phelper=ComParted.PartedHelper()
        #FIXME: create LabelResolver
        if self.refByLabel():
            pass
        if not self.exists():
            raise ComException("Device %s not found or no valid device!" % self.getDeviceName())

        dev=parted.PedDevice.get(self.getDeviceName())
        try:
            disk=parted.PedDisk.new(dev)
            partlist=phelper.get_primary_partitions(disk)
            for part in partlist:
                self.appendChild(Partition(part, self.getDocument()))
        except parted.error:
            self.log.debug("no partitions found")

    def restore(self):
        if hasattr(self, "lvm_activated") and self.lvm_activated:
            self.lvm_vg_deactivate()

    def createPartitions(self):
        """ creates new partition table """
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
            __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
            self.log.debug(__ret)
            __cmd=CMD_KPARTX + " -a " + self.getDeviceName()
            __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
            self.log.debug(__ret)
        #FIXME: crappy fix to give os some time to create devicefiles.
        time.sleep(10)


    def isDMMultipath(self):
        if not os.path.exists(CMD_DMSETUP):
            return False
        __cmd="%s table %s --target=multipath | grep multipath"  % (CMD_DMSETUP, self.getDeviceName())
        if ComSystem.execLocal(__cmd):
            return False
        return True


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
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        self.log.debug("savePartitionTable( " + filename + "):\n " + __ret)
        if __rc != 0:
            raise ComException(__cmd)

    def getPartitionTable(self):
        rc, rv = ComSystem.execLocalGetResult(self.getDumpStdout())
        if rc == 0:
            return rv
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
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        self.log.debug("restorePartitionTable( " + filename + "):\n " + __ret)
        if __rc != 0:
            raise ComException(__cmd)

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

def main():
    disk_dumps=[ """
        <disk name="Virtual Disks/atix/sourcedisk">
            <properties>
                <property name="size" value="10"/>
                <property name="disk_group" value="146er"/>
            </properties>
        </disk>
    """,
    """
        <disk name="Virtual Disks/atix/sourcedisk_snap">
            <mapping lun="1">
                <host name="server1"/>
            </mapping>
        </disk>
    """,
    """
        <disk name="/dev/VolGroup00/LogVol00"/>
    """]
    for disk_dump in disk_dumps:
        testDiskDump(disk_dump)

def testDiskDump(dump):
    print "Parsing dump..."
    print dump
    from xml.dom.ext.reader import Sax2
    from comoonics.ComDisk import Disk
    reader=Sax2.Reader(validate=0)
    doc=reader.fromString(dump)
    print "Creating disk..."
    disk=Disk(doc.documentElement, doc)
    print disk

if __name__ == '__main__':
    main()

# $Log: ComDisk.py,v $
# Revision 1.14  2007-04-11 14:45:22  mark
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
