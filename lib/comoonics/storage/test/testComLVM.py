'''
Created on Feb 26, 2010

@author: marc
'''
from comoonics import ComLog
from comoonics import ComSystem
from comoonics.storage.ComLVM import LogicalVolume, LinuxVolumeManager, PhysicalVolume, VolumeGroup
import logging
logging.basicConfig()
ComLog.setLevel(logging.DEBUG)
import unittest
ComSystem.setExecMode(ComSystem.SIMULATE)

class Test(unittest.TestCase):
    devicenames={"/dev/sda": [ LogicalVolume.LVMInvalidLVPathException ], 
                 "/dev/cciss/c0d0p1": [ [ "cciss", "c0d0p1" ] ], 
                 "/dev/mapper/abc-def": [ [ "abc", "def" ] ], 
                 "/dev/abc/def" : [ [ "abc", "def" ] ], 
                 "/dev/mapper/abc_def" : [ LogicalVolume.LVMInvalidLVPathException, None ],
                 "/dev/abc/def/geh" :  [ LogicalVolume.LVMInvalidLVPathException, None ]}

    def testsplitLVPath(self):
        ComSystem.setExecMode(ComSystem.SIMULATE)
        for device in self.devicenames.keys():
            print("device="+device)
            expresult=self.devicenames[device][0]
            try:
                result=list(LogicalVolume.splitLVPath(device))
                if expresult != LogicalVolume.LVMInvalidLVPathException:
                    result.sort()
                    expresult.sort()
                    print "Found: vgname: %s, lvname: %s" %(result[0], result[1])
                    self.assertEquals(result, expresult, "vgname: %s lvname: %s but returned vgname %s, lvname %s" %(result[0], result[1], expresult[0], expresult[1]))
                else:
                    self.fail("We would expect a %s but got a %s" %(expresult, result))
            except LogicalVolume.LVMInvalidLVPathException, e:
                print e.value
                self.assertEquals(e.__class__, expresult, "Expected exception %s but got %s" %(expresult, e.__class__))

    def testVgList(self):
        try:
            vgs=LinuxVolumeManager.vglist()
            for _vg in vgs:
                print "Volume group: "
                print _vg
                for lv in _vg.getLogicalVolumes():
                    print "Logical volume: ", lv

                for pv in _vg.getPhysicalVolumes():
                    print "Physical volume: ", pv
        except RuntimeError, re:
            self.assert_("Caught unexpected exception during vglist %s." %re)

    def testCreateLVMEnvironment(self):
        try:
            vgname="test_vg"
            lvname="test_lv"
            pvname="/dev/sda"
            print("Creating pv: %s" %pvname)
            _pv=PhysicalVolume(pvname)
            _pv.create()
            print("Creating vg: %s" %vgname)
            _vg=VolumeGroup(vgname, _pv)
            _vg.create()
            _vg.addPhysicalVolume(_pv)
            print("Creating lv: %s" %lvname)
            _lv=LogicalVolume(lvname, _vg)
            _lv.create()
            _vg.addLogicalVolume(_lv)
        
            print "Volumegroup %s: %s" %(vgname, _vg)
        
            print("Changing clustered")
            _vg.clustered()
            _vg.notclustered()
        
            print("Removing lv")
            _lv.remove()
            print("Removing vg")
            _vg.remove()
            print("Removing pv")
            _pv.remove()
        except Exception, e:
            import traceback
            traceback.print_exc()
            self.fail("Caught unexpected exception during lvm environment creation %s." %e)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()