#
# nfs.py - nfs class
#
# Copyright 2005, 2006 IBM, Inc.,
# Copyright 2006  Red Hat, Inc.
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import os
import kudzu
from comoonics import ComLog
log=ComLog.getLogger("comoonics:installation:nfs")
try:
    from fsset import FileSystemType
    import flags
    import iutil
    import commands
    class nfsFileSystem(FileSystemType):
        def __init__(self):
            from flags import flags
            FileSystemType.__init__(self)
            self.partedFileSystemType=None
            self.formattable=1
            self.checked=1
            self.linuxnativefs=1
            if flags.cmdline.has_key("nfs") or flags.debug:
                self.supported = -1
            else:
                self.supported = 0
            self.name="nfs"
            self.packages=None
            self.maxSizeMB=16*1024*1024
            self.packages=[ "portmap" ]
        
        def formatDevice(self, entry, progress, chroot="/"):
            log.debug("nfsFileSystem: skipping nfs format")
        def mount(self, device, mountpoint, readOnly=0, bindMount=0, instroot=""):
            if not self.isMountable():
                return
            iutil.mkdirChain("%s/%s" %(instroot, mountpoint))
#            if flags.selinux:
#                log.info("Could not mount nfs filesystem with selinux context enabled.")
#                return
            log.info("Mounting nfs %s => %s" %(device, "%s/%s" %(instroot, mountpoint)))
            rc,out=commands.getstatusoutput("mount -t nfs -o nolock %s %s/%s" %(device, instroot, mountpoint))
            if rc==0:
                return 0
            else:
                return 1
            
    from partRequests import PartitionSpec, RequestSpec
    from constants import REQUEST_PREEXIST
    import fsset
    class nfsPartitionSpec(PartitionSpec):
        """ Object to define a pseudo-requests nfs partition.."""
        def __init__(self, fstype, size = None, mountpoint = None,
                     preexist = 1, migrate = None, grow = 0, maxSizeMB = None,
                     start = None, end = None, drive = None, primary = None,
                     format = None, multidrive = None, bytesPerInode = 4096,
                     fslabel = None):
            """Create a new PartitionSpec object.

            fstype is the fsset filesystem type (should always be nfs).
            size is the requested size (in megabytes).
            mountpoint is the mountpoint.
            grow is whether or not the partition is growable (always 0).
            maxSizeMB is the maximum size of the partition in megabytes (always None).
            start is the starting cylinder/sector (new/preexist) (always None).
            end is the ending cylinder/sector (new/preexist) (always None).
            drive is the drive the partition goes on (default None should be a pseudo NFSDisk).
            primary is whether or not the partition should be forced as primary (always None).
            format is whether or not the partition should be formatted (always No).
            preexist is whether this partition is preexisting (always Yes).
            migrate is whether or not the partition should be migrated (always No).
            multidrive specifies if this is a request that should be replicated
            across _all_ of the drives in drive (always No)
            bytesPerInode is the size of the inodes on the filesystem (ignored).
            fslabel is the label to give to the filesystem (ignored).
            """

            # if it's preexisting, the original fstype should be set
            if preexist == 1:
                origfs = fstype
            else:
                origfs = None
            RequestSpec.__init__(self, fstype = fstype, size = size,
                                 mountpoint = mountpoint, format = None,
                                 preexist = 1, migrate = None,
                                 origfstype = origfs, bytesPerInode = bytesPerInode,
                                 fslabel = fslabel)
            self.type = REQUEST_PREEXIST

            self.grow = 0
            self.maxSizeMB = maxSizeMB
            self.requestSize = size
            self.start = start
            self.end = end

            self.drive = drive
            self.primary = None
            self.multidrive = None

            # should be able to map this from the device =\
            self.currentDrive = None
            """Drive that this request will currently end up on."""        

        def getDevice(self, partitions):
            """Return a device to solidify."""
            self.dev = fsset.PartitionDevice(self.device,
                                             encryption=self.encryption)
            return self.dev

        def getActualSize(self, partitions, diskset):
            """Return the actual size allocated for the request in megabytes."""
            # FIXME: Not yet implemented will return 10000
            return 10000

        def doSizeSanityCheck(self):
            """Sanity check that the size of the partition is sane."""
            if not self.fstype:
                return None
            if not self.format:
                return None
            ret = RequestSpec.doSizeSanityCheck(self)
            if ret is not None:
                return ret

            if (self.size and self.maxSizeMB
                and (self.size > self.maxSizeMB)):
                return (_("The size of the requested partition (size = %s MB) "
                          "exceeds the maximum size of %s MB.")
                        % (self.size, self.maxSizeMB))

            if self.size and self.size < 0:
                return _("The size of the requested partition is "
                         "negative! (size = %s MB)") % (self.size)
            return None
 
    from fsset import Device
    class NFSDevice(Device):
        def __init__(self , device = "none", encryption=None):
            Device.__init__(self, device, encryption)
            # FIXME: Quickhack for size of 6GB should be made more generic later
            self.model="NFSExport"
            self.deviceOptions="nolock, _netdev"
    def getDeviceOptions(self):
        return ["nolock"]
    
    def getExport(self):
        return self.getDevice()
    def getLabel(self):
        return ""
       
except:
    pass

class NFSType(object):
    def __init__(self):
        pass
    def check_feature(self, feature):
        return False

class PsudoDisk(object):
    pass
class NFSDisk(PsudoDisk):
    def __init__(self, _export):
        self.export=_export
        self.dev=NFSDevice(self)
        self.type=NFSType()
        self.extended_partition=None
        self.max_primary_partition_count=0
    def next_partition(self):
        return []

from partedUtils import DiskSet
class PsudoDiskSet(DiskSet):
    pseudoDisks=list()
    def _removeDisk(self, drive, addSkip=True):
        if not isinstance(drive, PsudoDisk) and not (self.disks.has_key(drive) and isinstance(self.disks[drive], PsudoDisk)):
            DiskSet._removeDisk(self, drive, addSkip)
        
class NFSExport(object):
    def __init__(self, nfsserver, export="/"):
        self.nfsserver=nfsserver
        self.export=export
        
    def mount(self, path, mount_opts="defaults"):
        pass
    def getSize(self):
        """
        returns the size in MB. Up to know 0 for not implemented
        """
        return 0
    def __str__(self):
        return "%s:%s" %(self.nfsserver, self.export)

class nfs(object):
    def __init__(self):
        self.nfsexports=list()
        self.nfsstarted=True
        
    def shutdown(self):
        pass
    def startup(self):
        pass
    def addNFSExport(self, nfsserver, export):
        self.nfsexports.append(NFSExport(nfsserver, export))
    def writeKS(self, _file):
        pass
    def write(self, installPath):
        # We don't need to write anything somewhere
        pass
    def _sizeToStr(self, size):
        if size <= 0:
            return "UNKNOWN"
        else:
            return str(size)
    def createNFSExportsStore(self, drivestore, selected=True):
        for _export in self.nfsexports:
            drivestore.append_row((_export.__str__(), self._sizeToStr(_export.getSize()), _export.__class__.__name__), selected)
    def appendDiskSet(self, diskset):
        for _export in self.nfsexports:
            diskset._addDisk(_export.__str__(), NFSDisk(_export))
    def is_nfsexport(self, _str):
        """
        Returns true if the given string is a nfs-export.
        syntax: host|ip':'export
        """
        if isinstance(_str, NFSExport):
            return True
        import re
        _PATTERN="^[\w.-_]+:\S+$"
        return re.match(_PATTERN, _str)

def has_nfs():
    # make sure the module is loaded
    if not os.access("/sys/module/nfs", os.X_OK):
        return False
    return True
    
########################
# $Log: nfs.py,v $
# Revision 1.1  2008-08-05 13:10:41  marc
# - first checkin
#