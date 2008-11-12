"""
Assistant helper for storage information
"""

# here is some internal information
# $Id: ComStorageAssistantHelper.py,v 1.2 2008-11-12 10:05:10 mark Exp $
#

__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/assistant/ComStorageAssistantHelper.py,v $

import re
from comoonics import ComSystem, ComLog, ComParted
from comoonics.assistant.ComAssistantHelper import AssistantHelper

from comoonics.ComLVM import *

__logStrLevel__="comoonics.assistant.ComAssistantHelper"


class StorageAssistantHelper(AssistantHelper):
    def scan(self):
        try: 
            if self.query == "rootdisk": 
                _dev=self.getRootDevice()
                ComLog.getLogger(__logStrLevel__).debug("detected rootdevice %s" %_dev)                
                return _dev
            if self.query == "rootpartition":
                return self.getRootPartition()
            if self.query == "bootdisk":
                return self.getBootDevice()
            if self.query == "livecd":
                return self.getLiveCDDevice()
        except Exception, e:
                ComLog.errorTraceLog()
                return
        
        
    def getRootDevice(self):
        _dev = self._scanRootDevice()
        ComLog.getLogger(__logStrLevel__).debug("detected rootdevice %s" %_dev)                
        if not _dev: 
            return
        _pv = self._getLVM_physicalVolume(_dev)
        if _pv:
            return [ self._normalizeDisk(_pv)[0] ]
        return [ self._normalizeDisk(_dev) [0] ]
    
    def getRootPartition(self):
        _dev = self._scanRootDevice()
        ComLog.getLogger(__logStrLevel__).debug("detected rootdevice %s" %_dev)                
        if not _dev: 
            return
        _pv = self._getLVM_physicalVolume(_dev)
        if _pv:
            return [ self._normalizeDisk(_pv)[1] ]
        return [ self._normalizeDisk(_dev) [1] ]
        
    
    def getBootDevice(self):
        _labels=["/boot", "boot", "/bootsr", "bootsr"]
        _devs=[]
        for _label in _labels:
            try: 
                _part = ComSystem.execLocalOutput("findfs LABEL=%s" %_label)
                ComLog.getLogger(__logStrLevel__).debug("detected disk %s" %_part)
                _device=self._normalizeDisk(_part[0])[0]
                ComLog.getLogger(__logStrLevel__).debug("normalized disk %s" %_device)
                _devs.append(_device)
            except Exception:
                pass
                #ComLog.errorTraceLog()
        return _devs
            
    def getLiveCDDevice(self):
        _devs=["/dev/cdrom"]
        for _dev in _devs:
            _cmd="isoinfo -d -i %s | grep COMOONICS" %_dev
            _rc, _rv, _err = ComSystem.execLocalGetResult(_cmd, err=True)
            if _rc == 0: return [_dev]
        return []
    
    def _normalizeDisk(self, name):
        ''' returns an array of the real disk device and partition '''
        #VERY NASTY implementation
        re_m=re.compile(r"/mapper/")
        re_md=re.compile(r"(^/dev/mapper/\w+?)(p*\d+)")
        re_d=re.compile(r"(^/dev/\w+?)(\d+)")
        if re_m.search(name):
            #mapper
            m=re_md.search(name)
            return m.group(1), m.group(2) 
        else:
            m=re_d.search(name)
            return m.group(1), m.group(2)
        return name, ""
        
            
    
    def _getLVM_physicalVolume(self, device):
        try:
            (vgname, lvname)=LogicalVolume.splitLVPath(device)
            _vg=VolumeGroup(vgname)
            _pv=LinuxVolumeManager.pvlist(_vg)
            ComLog.getLogger(__logStrLevel__).debug("detected physical volume %s" %_pv) 
            return _pv[0].getAttribute("name")
        except LogicalVolume.LVMInvalidLVPathException, e:
            ComLog.errorTraceLog()
            return
    
    def _scanRootDevice(self):
        regex=re.compile(r'^(\/.*?)\s+\/', re.MULTILINE)
        m=regex.search(open("/proc/mounts", "r").read())
        if not m: 
            return
        _dev = m.group(1) 
        return _dev
        