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
    class nfsFileSystem(FileSystemType):
        def __init__(self):
            FileSystemType.__init__(self)
            self.partedFileSystemType=None
            self.formattable=0
            self.checked=1
            self.linuxnativefs=1
            self.supported=-1
            self.name="nfs"
            self.packages=None
            self.maxSizeMB=16*1024*1024
        
        def formatDevice(self, entry, progress, chroot="/"):
            log.debug("nfsFileSystem: skipping nfs format")
except:
    pass

class NFSType(object):
    def __init__(self):
        pass
    def check_feature(self, feature):
        return False

class NFSDevice(object):
    def __init__(self, _disk):
        # FIXME: Quickhack for size of 6GB should be made more generic later
        self.heads=1024
        self.cylinders=1024
        self.sectors=6000
        self.sector_size=1
        self.model="NFSExport"


class PseudoDisk(object):
    pass
class NFSDisk(PseudoDisk):
    def __init__(self, _export):
        self.export=_export
        self.dev=NFSDevice(self)
        self.type=NFSType()
    def next_partition(self):
        return []

from partedUtils import DiskSet
class PseudoDiskSet(DiskSet):
    pseudoDisks=list()
    def _removeDisk(self, drive, addSkip=True):
        if not isinstance(drive, PseudoDisk):
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
    def addNFSExport(self, nfsserver, export="/"):
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