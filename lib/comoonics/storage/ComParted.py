"""Comoonics parted module
here should be some more information about the module, that finds its way inot the onlinedoc
Thanks to Red Hat Anaconda development

"""

# here is some internal information
# $Id $
#

import parted
import math
import string

from comoonics.ComExceptions import ComException
from comoonics import ComLog

__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/ComParted.py,v $

class PartitioningError(ComException): pass

class PartedHelper:
    __logStrLevel__="PartedHelper"
    log=ComLog.getLogger(__logStrLevel__)

    """
    Utility class to work with pyparted
    """


    def __init__(self):
        pass

    # All from anaconda partedUtils.py

    def get_flags_as_string (self, part):
        """Retrieve a list of strings representing the flags on the partition."""
        strings=[]
        for flag in self.get_flags(part):
            strings.append(parted.partition_flag_get_name (flag))
        return strings

    def get_flags(self, part):
        flags=[]
        if not part.is_active ():
            return flags
        flag = parted.partition_flag_next (0)
        while flag:
            if part.get_flag (flag):
                flags.append(flag)
            flag = parted.partition_flag_next (flag)
        return flags

    def start_sector_to_cyl(self, device, sector):
        """Return the closest cylinder (round down) to sector on device."""
        return int(math.floor((float(sector)
                               / (device.heads * device.sectors)) + 1))

    def end_sector_to_cyl(self, device, sector):
        """Return the closest cylinder (round up) to sector on device."""
        maxcyl=device.cylinders
        _cyls=int(math.ceil(float((sector + 1))
                             / (device.heads * device.sectors)))
        if _cyls>maxcyl:
            _cyls=maxcyl
        self.log.debug("end_sector_to_cyl %u > %u? %s" %(_cyls, maxcyl, _cyls>maxcyl))
        return _cyls

    def start_cyl_to_sector(self, device, cyl):
        "Return the sector corresponding to cylinder as a starting cylinder."
        return long((cyl - 1) * (device.heads * device.sectors))

    def end_cyl_to_sector(self, device, cyl):
        "Return the sector corresponding to cylinder as a ending cylinder."
        return long(((cyl) * (device.heads * device.sectors)) - 1)

    def getPartSize(self, partition):
        """Return the size of partition in sectors."""
        return partition.geom.length

    def getPartSizeMB(self, partition):
        """Return the size of partition in megabytes."""
        return (partition.geom.length * partition.geom.dev.sector_size
                / 1024.0 / 1024.0)

    def getDeviceSizeMB(self, dev):
        """Return the size of dev in megabytes."""
        return (float(dev.heads * dev.cylinders * dev.sectors) / (1024 * 1024)
                * dev.sector_size)

    def get_partition_by_name(self, disks, partname):
        """Return the parted part object associated with partname.

        Arguments:
        disks -- Dictionary of diskname->PedDisk objects
        partname -- Name of partition to find

        Return:
        PedPartition object with name partname.  None if no such partition.
        """
        for diskname in disks.keys():
            disk = disks[diskname]
            part = disk.next_partition()
            while part:
                if self.get_partition_name(part) == partname:
                    return part

                part = disk.next_partition(part)

        return None

    def get_partition_name(self, partition):
        """Return the device name for the PedPartition partition."""
        if (partition.geom.dev.type == parted.DEVICE_DAC960
            or partition.geom.dev.type == parted.DEVICE_CPQARRAY):
            return "%sp%d" % (partition.geom.dev.path[5:],
                              partition.num)
        if (parted.__dict__.has_key("DEVICE_SX8") and
            partition.geom.dev.type == parted.DEVICE_SX8):
            return "%sp%d" % (partition.geom.dev.path[5:],
                              partition.num)

        return "%s%d" % (partition.geom.dev.path[5:],
                         partition.num)

    def get_partition_file_system_type(self, part):
        # not included because anaconda's fsset library is used.
        pass

    def set_partition_file_system_type(self, part, fstype):
        """Set partition type of part to PedFileSystemType implied by fstype."""
        # not included yet
        pass

    def get_partition_drive(self, partition):
        """Return the device name for disk that PedPartition partition is on."""
        return "%s" %(partition.geom.dev.path[5:])

    def get_max_logical_partitions(self, disk):
        if not disk.type.check_feature(parted.DISK_TYPE_EXTENDED):
            return 0
        dev = disk.dev.path[5:]
        for key in max_logical_partition_count.keys():
            if dev.startswith(key):
                return max_logical_partition_count[key]
        # FIXME: if we don't know about it, should we pretend it can't have
        # logicals?  probably safer to just use something reasonable
        return 11

    def map_foreign_to_fsname(self, type):
        """Return the partition type associated with the numeric type."""
        # not decided yet
        pass

    def filter_partitions(self, disk, func):
        rc = []
        part = disk.next_partition ()
        while part:
            if func(part):
                rc.append(part)
            part = disk.next_partition (part)

        return rc

    def get_all_partitions(self, disk):
        """Return a list of all PedPartition objects on disk."""
        func = lambda part: part.is_active()
        return self.filter_partitions(disk, func)

    def get_logical_partitions(self, disk):
        """Return a list of logical PedPartition objects on disk."""
        func = lambda part: (part.is_active()
                             and part.type & parted.PARTITION_LOGICAL)
        return self.filter_partitions(disk, func)

    def get_primary_partitions(self, disk):
        """Return a list of primary PedPartition objects on disk."""
        func = lambda part: part.type == parted.PARTITION_PRIMARY
        return self.filter_partitions(disk, func)

    def get_raid_partitions(self, disk):
        """Return a list of RAID-type PedPartition objects on disk."""
        func = lambda part: (part.is_active()
                             and part.get_flag(parted.PARTITION_RAID) == 1)
        return self.filter_partitions(disk, func)

    def get_lvm_partitions(self, disk):
        """Return a list of physical volume-type PedPartition objects on disk."""
        func = lambda part: (part.is_active()
                             and part.get_flag(parted.PARTITION_LVM) == 1)
        return self.filter_partitions(disk, func)

    def getDefaultDiskType(self):
        """Get the default partition table type for this architecture."""
        # not included because anacondas iutil package is used
        pass

    def add_partition(self, disk, type, size, flags):
        """Add a new partition to the device.
            size of 0 means rest of remaining disk space
        """

        part = disk.next_partition ()
        status = 0
        while part:
            if (part.type == parted.PARTITION_FREESPACE
                and part.geom.length >= size):
                if size == 0:
                    newp = disk.partition_new (type, None, part.geom.start,
                                           part.geom.end)
                else:
                    newp = disk.partition_new (type, None, part.geom.start,
                                           part.geom.start + size)
                for flag in flags:
                    newp.set_flag(flag, 1)
                constraint = disk.dev.constraint_any ()

                try:
                    disk.add_partition (newp, constraint)
                    status = 1
                    break
                except parted.error, msg:
                    raise PartitioningError, msg
            part = disk.next_partition (part)
        if not status:
            raise PartitioningError("Not enough free space on %s to create "
                                    "new partition" % (disk.dev.path))
        return newp

