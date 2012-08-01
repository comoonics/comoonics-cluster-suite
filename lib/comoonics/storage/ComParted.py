"""Comoonics parted module
here should be some more information about the module, that finds its way inot the onlinedoc
Thanks to Red Hat Anaconda development

"""

# here is some internal information
# $Id $
#

import math

from comoonics.ComExceptions import ComException
from comoonics import ComLog

__version__ = "$Revision: 1.4 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/ComParted.py,v $

class PartitioningError(ComException): pass

class AbstractPartedHelper:
    __logStrLevel__="AbstractPartedHelper"
    log=ComLog.getLogger(__logStrLevel__)

    DEVICE_DAC960=3
    DEVICE_CPQARRAY=4
    DEVICE_SX8=None    

    def __init__(self):
        pass
    def isForVersion(self, version):
        return False
    
class PartedHelper2(AbstractPartedHelper):
    """PartedHelper2()
    Utility class to work with pyparted (version >= 2)
    """
    __logStrLevel__="AbstractPartedHelper"
    log=ComLog.getLogger(__logStrLevel__)

    def __init__(self):
        import parted
        import _ped
        if hasattr(parted, "DiskLabelException"):
            self.disklabelexception=parted.DiskLabelException
        elif hasattr(_ped, "DiskLabelException"):
            self.disklabelexception=_ped.DiskLabelException
        else:
            self.disklabelexception=Exception
            

    def start_sector_to_cyl(self, device, sector):
        """Return the closest cylinder (round down) to sector on device."""
        return device.startSectorToCylinder(sector)

    def end_sector_to_cyl(self, device, sector):
        """Return the closest cylinder (round up) to sector on device."""
        return device.endSectorToCylinder(sector)

    def start_cyl_to_sector(self, device, cyl):
        "Return the sector corresponding to cylinder as a starting cylinder."
        return device.startCylinderToSector(cyl)

    def end_cyl_to_sector(self, device, cyl):
        "Return the sector corresponding to cylinder as a ending cylinder."
        return device.endCylinderToSector(cyl)

    def initFromDisk(self, devicename):
        import parted
        partitions=list()
        dev=parted.getDevice(devicename)
        try:
            dev=parted.getDevice(devicename)
            disk=parted.Disk(dev)
            for part in disk.getPrimaryPartitions():
                partitions.append(part)
        except self.disklabelexception:
            self.log.debug("no partitions found")
        return partitions

    def createPartitions(self, devicename, partitions, samesize):
        """
        Create the given partitions on the device devicename.
        @param partitions: the partitions to be created
        @type partitions: comoonics.storage.ComPartitions.Partition 
        """
        import parted
        dev=parted.getDevice(devicename)
        try:
            disk=parted.Disk(dev)
            disk.deleteAllPartitions()
        except self.disklabelexception:
            disk=parted.freshDisk(dev, parted.disk.diskType["msdos"])
        for part in partitions:
            partedtype=part.getPartedType()
            size=part.getAttribute("size")
            flags=part.getFlags()
            size=self.getSectorSize(size, dev)
            partedflags=list()
            for flag in flags:
                partedflags.append(flag.getFlagPartedNum())
            self.log.debug("creating partition: size: %i" % size )
            self.add_partition(disk, partedtype, size, flags, samesize=samesize)

        disk.commit()

    def get_flags_as_string (self, part):
        return part.getFlagsAsString().split(",")

    def getPartName(self, partition):
        """ Return the partition name"""
        return partition.name

    def getPartNumber(self, partition):
        """ Return the partition number"""
        return partition.number

    def getPartType(self, partition):
        """ Return the partition type"""
        return partition.type
    
    def getPartSize(self, partition):
        """Return the size of partition in sectors."""
        return partition.geometry.length

    def getPartSizeMB(self, partition):
        """Return the size of partition in megabytes."""
        return partition.getSize("MB")

    def getDeviceSizeMB(self, devname):
        """Return the size of dev in megabytes."""
        import parted
        return parted.getDevice(devname).getSize("MB")

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
            for part in disk.partitions:
                if self.get_partition_name(part) == partname:
                    return part
        return None

    def get_partition_name(self, partition):
        """Return the device name for the PedPartition partition."""
        if (partition.geometry.device.type == self.DEVICE_DAC960
            or partition.geometry.device.type == self.DEVICE_CPQARRAY):
            return "%sp%d" % (partition.geometry.device.path[5:],
                              partition.number)
        return "%s%d" % (partition.geometry.device.path[5:],
                         partition.num)

    def get_all_partitions(self, disk):
        """Return a list of all PedPartition objects on disk."""
        return disk.partitions

    def get_logical_partitions(self, disk):
        """Return a list of logical PedPartition objects on disk."""
        return disk.getLogicalPartitions()

    def get_primary_partitions(self, disk):
        """Return a list of primary PedPartition objects on disk."""
        return disk.getPrimaryPartitions()

    def get_raid_partitions(self, disk):
        """Return a list of RAID-type PedPartition objects on disk."""
        return disk.getRaidPartitions()

    def get_lvm_partitions(self, disk):
        """Return a list of physical volume-type PedPartition objects on disk."""
        return disk.getLVMPartitions()

    def add_partition(self, disk, parttype, size, flags, samesize=False):
        """Add a new partition to the device.
            size of 0 means rest of remaining disk space
        """
        import parted
        newpart = None
        for part in disk.getFreeSpacePartitions():
            if (part.geometry.length >= size) or samesize:
                if size == 0:
                    maxgeometry=parted.Geometry(device=disk.device, start=part.geometry.start,
                                                end=part.geometry.end)
                else:
                    maxgeometry=parted.Geometry(device=disk.device, start=part.geometry.start,
                                                end=part.geometry.start+size)
                if samesize:
                    mingeometry=parted.Geometry(device=disk.device, start=part.geometry.start,
                                                end=part.geometry.end)
                else:
                    mingeometry=maxgeometry
                constraint=parted.Constraint(device=disk.device, minGeom=mingeometry, maxGeom=maxgeometry)
                try:
                    newpart=parted.Partition(disk=disk, type=parttype, geometry=mingeometry)
                    for flag in flags:
                        newpart.setFlag(flag)
                    disk.addPartition(newpart, constraint)
                    break
                except Exception, msg:
                    raise PartitioningError, msg
        if not newpart:
            raise PartitioningError("Not enough free space on %s to create "
                                    "new partition with size %u." % (disk.device.path, size))
        return newpart

    def getSectorSizeOptimum(self, size, dev):
        sectors=self.getSectorSize(size, dev)
        if sectors == 0: return 0
        # now round up
        cyls=self.end_sector_to_cyl(dev, sectors)
        sectors=self.end_cyl_to_sector(dev, cyls)
        return sectors

    def getSectorSize(self, size, dev):
        """ returns always size in sectors """
        import re
        # calculate new size
        # FIXME Round up to next cylinder
        # Test Megabyte e.g. size="200M"
        if type(size)==int or type(size)==long:
            return size
        res=re.search("([0-9]+)M", size)
        if res:
            sectors=int(res.group(1)) * 1024 * 1024 / dev.sectorSize
            self.log.debug("found size in Megabytes : %s -> %s sectors" % (res.group(1), sectors))
            return sectors

        # Test Gigabyte e.g. size="200G"
        res=re.search("([0-9]+)G", size)
        if res:
            sectors = int(res.group(1)) * 1024 * 1024 * 1024 / dev.sectorSize
            self.log.debug("found size in Gigabytes : %s -> %s sectors" %(res.group(1), sectors))
            return sectors

        # Test Percentage
        res=re.search("([0-9]+)%", size)
        if res:
            sectors=int(float(float(res.group(1)) / 100 * dev.heads * dev.cylinders * dev.sectors))
            self.log.debug("found size in %% : %s -> %s sectors" %( res.group(1), sectors))
            return sectors

        # Test REMAIN
        res=re.search("REMAIN", size)
        if res:
            self.log.debug("found size in Tag :REMAIN")
            return 0

        # Test sectors
        res=re.search("[0-9]+", size)
        if res:
            self.log.debug("found size in Tag :%s " % size)
            return int(size)

        raise ComException("size %s not supported" % size)

    def getPartedPartitionsFlags(self, flags):
        flagsnrs = []
        for flag in flags:
            flagsnrs.append(flag.getFlagPartedNum())
        return flags
    
    def isForVersion(self, version):
        return version >= 2

class PartedHelper1(AbstractPartedHelper):
    """PartedHelper1()
    Utility class to work with pyparted (version <2)
    """
    __logStrLevel__="PartedHelper1"
    log=ComLog.getLogger(__logStrLevel__)

    def __init__(self):
        # try to check which version is valid and fail if not needed
        pass

    # All from anaconda partedUtils.py
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

    def initFromDisk(self, devicename):
        import parted
        partitions=list()
        dev=parted.PedDevice.get(devicename)
        try:
            disk=parted.PedDisk.new(dev)
            partlist=self.get_primary_partitions(disk)
            for part in partlist:
                partitions.append(part)
        except parted.error:
            self.log.debug("no partitions found")
        return partitions

    def createPartitions(self, devicename, partitions, samesize):
        import parted
        #IDEA compare the partition configurations for update
        #1. delete all aprtitions

        # old way RHEL4/5
        dev=parted.PedDevice.get(devicename)
        disk=parted.PedDisk.new(dev)
        try:
            disk.delete_all()
        except parted.error:
            #FIXME use generic disk types
            disk=dev.disk_new_fresh(parted.disk_type_get("msdos"))

        # create new partitions
        for part in partitions:
            partedtype=part.getPartedType()
            if samesize:
                size=self.getSectorSize(part.getAttribute("size"), dev)
            else:
                size=self.getSectorSizeOptimum(part.getAttribute("size"), dev)
            flags=part.getFlags()
            partedflags=list()
            for flag in flags:
                partedflags.append(flag.getFlagPartedNum())
            self.log.debug("creating partition: size: %i" % size )
            self.add_partition(disk, partedtype, size, partedflags)

        disk.commit()

    def get_flags_as_string (self, part):
        """Retrieve a list of strings representing the flags on the partition."""
        import parted
        strings=[]
        for flag in self._get_flags(part):
            strings.append(parted.partition_flag_get_name(flag))
        return strings

    def _get_flags(self, part):
        import parted
        flags=[]
        if not part.is_active():
            return flags
        flag = parted.partition_flag_next(0)
        while flag:
            if part.get_flag (flag):
                flags.append(flag)
            flag = parted.partition_flag_next (flag)
        return flags

    def getPartName(self, partition):
        """ Return the partition name"""
        return partition.name

    def getPartType(self, partition):
        """ Return the partition type"""
        return partition.type

    def getPartNumber(self, partition):
        """ Return the partition devicename"""
        return partition.num

    def getPartSize(self, partition):
        """Return the size of partition in sectors."""
        return partition.geom.length

    def getPartSizeMB(self, partition):
        """Return the size of partition in megabytes."""
        return (self.getPartSize(partition) * partition.geom.dev.sector_size
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
        if (partition.geom.dev.type == self.DEVICE_DAC960
            or partition.geom.dev.type == self.DEVICE_CPQARRAY):
            return "%sp%d" % (partition.geom.dev.path[5:],
                              partition.num)
        #if (parted.__dict__.has_key("DEVICE_SX8") and
        #    partition.geom.dev.type == self.DEVICE_SX8):
        #    return "%sp%d" % (partition.geom.dev.path[5:],
        #                      partition.num)

        return "%s%d" % (partition.geom.dev.path[5:],
                         partition.num)

    def _filter_partitions(self, disk, func):
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
        return self._filter_partitions(disk, func)

    def get_logical_partitions(self, disk):
        """Return a list of logical PedPartition objects on disk."""
        from ComPartition import Partition
        func = lambda part: (part.is_active()
                             and part.type & Partition.PARTITION_TYPES["logical"])
        return self._filter_partitions(disk, func)

    def get_primary_partitions(self, disk):
        """Return a list of primary PedPartition objects on disk."""
        from ComPartition import Partition
        func = lambda part: part.type == Partition.PARTITION_TYPES["primary"]
        return self._filter_partitions(disk, func)

    def get_raid_partitions(self, disk):
        """Return a list of RAID-type PedPartition objects on disk."""
        from ComPartition import PartitionFlag
        func = lambda part: (part.is_active()
                             and part.get_flag(PartitionFlag.ALLFLAGS["raid"]) == 1)
        return self._filter_partitions(disk, func)

    def get_lvm_partitions(self, disk):
        """Return a list of physical volume-type PedPartition objects on disk."""
        from ComPartition import PartitionFlag
        func = lambda part: (part.is_active()
                             and part.get_flag(PartitionFlag.ALLFLAGS["lvm"]) == 1)
        return self._filter_partitions(disk, func)

    def getDefaultDiskType(self):
        """Get the default partition table type for this architecture."""
        # not included because anacondas iutil package is used
        pass

    def add_partition(self, disk, parttype, size, flags):
        """Add a new partition to the device.
            size of 0 means rest of remaining disk space
        """
        from ComPartition import Partition
        part = disk.next_partition ()
        status = 0
        while part:
            if (part.type == Partition.PARTITION_TYPES["freespace"]
                and part.geom.length >= size):
                if size == 0:
                    newp = disk.partition_new (parttype, None, part.geom.start,
                                           part.geom.end)
                else:
                    newp = disk.partition_new (parttype, None, part.geom.start,
                                           part.geom.start + size)
                for flag in flags:
                    newp.set_flag(flag, 1)
                constraint = disk.dev.constraint_any ()

                try:
                    disk.add_partition (newp, constraint)
                    status = 1
                    break
                except Exception, msg:
                    raise PartitioningError, msg
            part = disk.next_partition (part)
        if not status:
            raise PartitioningError("Not enough free space on %s to create "
                                    "new partition" % (disk.dev.path))
        return newp
    
    def getSectorSizeOptimum(self, size, dev):
        sectors=self.getSectorSize(size, dev)
        if sectors == 0: return 0
        # now round up
        cyls=self.end_sector_to_cyl(dev, sectors)
        sectors=self.end_cyl_to_sector(dev, cyls)
        return sectors

    def getSectorSize(self, size, dev):
        """ returns always size in sectors """
        import re
        # calculate new size
        # FIXME Round up to next cylinder
        # Test Megabyte e.g. size="200M"
        res=re.search("([0-9]+)M", size)
        if res:
            sectors=int(res.group(1)) * 1024 * 1024 / dev.sector_size
            self.log.debug("found size in Megabytes : %s -> %s sectors" % (res.group(1), sectors))
            return sectors

        # Test Gigabyte e.g. size="200G"
        res=re.search("([0-9]+)G", size)
        if res:
            sectors = int(res.group(1)) * 1024 * 1024 * 1024 / dev.sector_size
            self.log.debug("found size in Gigabytes : %s -> %s sectors" %(res.group(1), sectors))
            return sectors

        # Test Percentage
        res=re.search("([0-9]+)%", size)
        if res:
            sectors=int(float(float(res.group(1)) / 100 * dev.heads * dev.cylinders * dev.sectors))
            self.log.debug("found size in %% : %s -> %s sectors" %( res.group(1), sectors))
            return sectors

        # Test REMAIN
        res=re.search("REMAIN", size)
        if res:
            self.log.debug("found size in Tag :REMAIN")
            return 0

        # Test sectors
        res=re.search("[0-9]+", size)
        if res:
            self.log.debug("found size in Tag :%s " % size)
            return int(size)

        raise ComException("size %s not supported" % size)

    def getPartedPartitionsFlags(self, flags):
        flagsnrs = []
        for flag in flags:
            flagsnrs.append(flag.getFlagPartedNum())
        return flags

    def isForVersion(self, version):
        return float(version) < 2

partedHelpers=list()
try:
    partedHelpers.append(PartedHelper1())
except:
    pass
try:
    partedHelpers.append(PartedHelper2())
except:
    pass

def getPartedVersion():
    import parted
    try:
        return float(parted.version()['libparted'])
    except SystemError:
        from _ped import libparted_version
        return float(libparted_version())
    except:
        return 1

def getInstance():
    import parted
    
    for helper in partedHelpers:
        if helper.isForVersion(getPartedVersion()):
            return helper
