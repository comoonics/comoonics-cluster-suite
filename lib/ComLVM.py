"""Comoonics lvm module


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComLVM.py,v $

import os
from exceptions import RuntimeError

import ComSystem
from ComDataObject import DataObject

class LinuxVolumeManager(DataObject):
    '''
    Baseclass for all LVM Objects. Shares attributes and methods for all subclasses
    '''
    
    __lvmDevicePresent__=0
    __logStrLevel__ = "LVM"
    
    def __init__(self,element):
        DataObject.__init__(self,element)
        self.has_lvm()

    def has_lvm(self):
        if not (os.access("/usr/sbin/lvm", os.X_OK) or
            os.access("/sbin/lvm", os.X_OK)):
            return
    
        f = open("/proc/devices", "r")
        lines = f.readlines()
        f.close()

        for line in lines:
            try:
                (dev, name) = line[:-1].split(' ', 2)
            except:
                continue
            if name == "device-mapper":
                __lvmDevicePresent__ = 1
                break
        
        if __lvmDevicePresent__ == 0:
            raise RuntimeError("LVM Functionality does not seam to be available")
        return 1
        
class VolumeGroup(LinuxVolumeManager):
    '''  
    Representation of the Linux Volumen Manager Volume Group 
    '''
    
    TAGNAME_LV='logical_volume'
    TAGNAME_PV='physical_volume'
    
    def __init__(self, element):
        DataObject.__init__(self,element)
        
    def getLogicalVolumes(self):
        lvs=list()
        for lv_element in self.getElement().getElementsByTagName(self.TAGNAME_LV):
            lvs.append(LogicalVolume(lv_element))
        return lvs

    def getPhysicalVolumes(self):
        pvs=list()
        for pv_element in self.getElement().getElementsByTagName(self.TAGNAME_PV):
            pvs.append(LogicalVolume(pv_element))
        return pvs

    def vgscan(self):
        """Runs vgscan."""
        
        self.has_lvm()
        
        (rc, rv) = ComSystem.execLocalGetResult('lvm vgscan -v')
        if rc:
            raise RuntimeError("running vgscan failed: "+ str(rc)+", ",rv)

    def vgactivate(self):
        """
        Activate volume groups by running vgchange -ay.
        """

        self.has_lvm()
        (rc, rv) = ComSystem.execLocalGetResult('lvm vgchange -ay '+self.name)
    
        if rc:
            raise RuntimeError("running vgchange of "+self.name+" failed: "+str(rc)+", ",rv)

        # now make the device nodes
        (rc, rv) = ComSystem.execLocalGetResult('lvm mknodes '+self.name)
        if rc:
            raise RuntimeError("running vgmknodes failed: "+rc+", "+rv)

    def vgdeactivate(self):
        """
        Deactivate volume groups by running vgchange -an.
        """

        self.has_lvm()
        (rc, rv) = ComSystem.execLocalGetResult('lvm vgchange -an '+self.name)
    
        if rc:
            raise RuntimeError("running vgchange of "+self.name+" failed: "+str(rc)+", ",rv)
           
class LogicalVolume(LinuxVolumeManager):
    '''
    Representation of the Linux Volume Manager Logical Volume
    '''
    
    def __init__(self, element):
        DataObject.__init__(self, element)

class PhyisicalVolume(LinuxVolumeManager):
    '''
    Representation of the Linux Volume Manager Physical Volume
    '''
    
    def __init__(self, element):
        DataObject.__init__(self, element)

# $Log: ComLVM.py,v $
# Revision 1.1  2006-06-26 19:12:48  marc
# initial revision
#