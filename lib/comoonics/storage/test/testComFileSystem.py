'''
Created on Mar 25, 2010

@author: marc
'''
import unittest
from comoonics import ComSystem

class BaseTestFileSystem(unittest.TestCase):
    xml=None
    filesystem=None
    device=None
    mountpoint=None
    commands=None
    simmethods=None
    name=""
    label="mylabel"

    def setUp(self):
        from comoonics import XmlTools
        import StringIO
        from comoonics.storage.ComDevice import Device
        from comoonics.storage.ComMountpoint import MountPoint
        from comoonics.storage.ComFileSystem import getFileSystem
        
        xmlfp=StringIO.StringIO(self.xml)
        doc=XmlTools.parseXMLFP(xmlfp)
        __device=doc.documentElement
        
        self.device=Device(__device, doc)
        __fs=__device.getElementsByTagName("filesystem")[0]
        self.filesystem=getFileSystem(__fs, doc)
        __mp=__device.getElementsByTagName("mountpoint")[0]
        self.mountpoint=MountPoint(__mp, doc)
        
    def _testMethod(self, method, execmode, *params):
        oldmode=ComSystem.getExecMode()
        ComSystem.clearSimCommands()
        ComSystem.setExecMode(execmode)
        try:
            method(*params)
        except Exception, e:
            import traceback
            traceback.print_exc()
            self.fail("Could not execute %s method on with parameters %s, Error: %s" %(method, params, e))
        if self.simmethods and ComSystem.isSimulate():
            errormethods=list()
            for simmethod in ComSystem.getSimCommands():
                matched=False
                for simmethod2 in self.simmethods:
                    if not matched and isinstance(simmethod2, basestring):
                        matched=simmethod == simmethod2
                    elif not matched:
                        # Must be re
                        matched=simmethod2.match(simmethod)
                if matched == False:
                    errormethods.append(simmethod)
            if len(errormethods) >0:
                bufsimmethods=list()
                for simmethod in self.simmethods:
                    if isinstance(simmethod, basestring):
                        bufsimmethods.append(simmethod)
                    else:
                        bufsimmethods.append(simmethod.pattern)
                self.fail("""The commands being executed are not to be found in the commands that must have been executed.
Commands that could not be matched are:
%s
Executed commands are: 
%s
Expected commands are:
%s
""" %("\n".join(errormethods), "\n".join(ComSystem.getSimCommands()), "\n".join(bufsimmethods)))
        ComSystem.setExecMode(oldmode)
    
    def testMount(self):
        self._testMethod(self.filesystem.mount, ComSystem.SIMULATE ,self.device, self.mountpoint)
        
    def testUmountDev(self):
        self._testMethod(self.filesystem.umountDev, ComSystem.SIMULATE, self.device)
        
    def testUmountDir(self):
        self._testMethod(self.filesystem.umountDir, ComSystem.SIMULATE, self.mountpoint)
        
    def testGetName(self):
        self.failUnlessEqual(self.filesystem.getName(), self.name, "The filesystem with name %s does not equal expected name %s" %(self.filesystem.getName(), self.name))

    def testFormatDevice(self):
        self._testMethod(self.filesystem.formatDevice, ComSystem.SIMULATE, self.device)
        
    def testLabelDevice(self):
        self._testMethod(self.filesystem.labelDevice, ComSystem.SIMULATE, self.device, self.label)
        
    def testCheckFs(self):
        self._testMethod(self.filesystem.checkFs, ComSystem.SIMULATE, self.device)
        
    def testGetLabel(self):
        self._testMethod(self.filesystem.getLabel, ComSystem.SIMULATE, self.device)

class TestGfsFileSystem(BaseTestFileSystem):
    def __init__(self, method="runTest"):
        self.xml="""
  <device id="sourcerootfs" name="/dev/vg_vmware_cluster_sr/lv_sharedroot">
    <filesystem type="gfs" journals="5" lockproto="lock_nolock" clustername="cluster1" locktable="locktable1" bsize="1024"/>
    <mountpoint name="/">
      <option value="lock_nolock" name="lockproto"/>
      <option value="hdfhgg" name="locktable"/>
    </mountpoint>
  </device>
"""
        self.simmethods=["mount -t gfs -o lockproto=lock_nolock,locktable=hdfhgg /dev/vg_vmware_cluster_sr/lv_sharedroot /", 
                         "umount /dev/vg_vmware_cluster_sr/lv_sharedroot", 
                         "umount /",
                         "gfs_mkfs -O  -j 5 -p lock_nolock -t cluster1:locktable1 -b 1024 /dev/vg_vmware_cluster_sr/lv_sharedroot", 
                         "gfs_fsck -y /dev/vg_vmware_cluster_sr/lv_sharedroot",
                         ]
        self.name="gfs"
        BaseTestFileSystem.__init__(self, method)
        
    def testGetLabel(self):
        pass

class TestGfs2FileSystem(BaseTestFileSystem):
    def __init__(self, method="runTest"):
        self.xml="""
  <device id="sourcerootfs" name="/dev/vg_vmware_cluster_sr/lv_sharedroot">
    <filesystem type="gfs2" journals="5" lockproto="lock_nolock" clustername="cluster1" locktable="locktable1" bsize="1024"/>
    <mountpoint name="/">
      <option value="lock_nolock" name="lockproto"/>
      <option value="hdfhgg" name="locktable"/>
    </mountpoint>
  </device>
"""
        self.simmethods=["mount -t gfs2 -o lockproto=lock_nolock,locktable=hdfhgg /dev/vg_vmware_cluster_sr/lv_sharedroot /", 
                         "umount /dev/vg_vmware_cluster_sr/lv_sharedroot", 
                         "umount /",
                         "mkfs.gfs2 -O  -j 5 -p lock_nolock -t cluster1:locktable1 -b 1024 /dev/vg_vmware_cluster_sr/lv_sharedroot", 
                         "fsck.gfs2 -y /dev/vg_vmware_cluster_sr/lv_sharedroot",
                         ]
        self.name="gfs"
        BaseTestFileSystem.__init__(self, method)
        
    def testGetLabel(self):
        pass

class TestExt2FileSystem(BaseTestFileSystem):
    def __init__(self, method="runTest"):
        import re
        self.xml="""
  <device id="sourcerootfs" name="/dev/vg_vmware_cluster_sr/lv_sharedroot">
    <filesystem type="ext2"/>
    <mountpoint name="/"/>
  </device>
"""
        self.simmethods=["mount -t ext2 -o defaults /dev/vg_vmware_cluster_sr/lv_sharedroot /", 
                         "umount /dev/vg_vmware_cluster_sr/lv_sharedroot", 
                         "umount /",
                         "mkfs -t ext2  /dev/vg_vmware_cluster_sr/lv_sharedroot",
                         "e2fsck -y /dev/vg_vmware_cluster_sr/lv_sharedroot",
                         "e2label /dev/vg_vmware_cluster_sr/lv_sharedroot mylabel",
                         "e2label /dev/vg_vmware_cluster_sr/lv_sharedroot"
                         ]
        self.name="ext2"
        BaseTestFileSystem.__init__(self, method)

class TestExt3FileSystem(BaseTestFileSystem):
    def __init__(self, method="runTest"):
        import re
        self.xml="""
  <device id="sourcerootfs" name="/dev/vg_vmware_cluster_sr/lv_sharedroot">
    <filesystem type="ext3"/>
    <mountpoint name="/"/>
  </device>
"""
        self.simmethods=["mount -t ext3 -o defaults /dev/vg_vmware_cluster_sr/lv_sharedroot /", 
                         "umount /dev/vg_vmware_cluster_sr/lv_sharedroot", 
                         "umount /",
                         "mkfs -t ext3  /dev/vg_vmware_cluster_sr/lv_sharedroot",
                         "e2fsck -y /dev/vg_vmware_cluster_sr/lv_sharedroot",
                         "e2label /dev/vg_vmware_cluster_sr/lv_sharedroot mylabel",
                         "e2label /dev/vg_vmware_cluster_sr/lv_sharedroot"
                         ]
        self.name="ext3"
        BaseTestFileSystem.__init__(self, method)

class TestOcfs2FileSystem(BaseTestFileSystem):
    def __init__(self, method="runTest"):
        import re
        self.xml="""
  <device id="sourcerootfs" name="/dev/vg_vmware_cluster_sr/lv_sharedroot">
    <filesystem type="ocfs2"/>
    <mountpoint name="/"/>
  </device>
"""
        self.simmethods=["mount -t ocfs2 -o defaults /dev/vg_vmware_cluster_sr/lv_sharedroot /", 
                         "umount /dev/vg_vmware_cluster_sr/lv_sharedroot", 
                         "umount /",
                         "yes | mkfs -t ocfs2 -F /dev/vg_vmware_cluster_sr/lv_sharedroot",
                         "ocfs2.fsck -y /dev/vg_vmware_cluster_sr/lv_sharedroot",
                         "tunefs.ocfs2 -L /dev/vg_vmware_cluster_sr/lv_sharedroot mylabel",
                         "tunefs.ocfs2 -L /dev/vg_vmware_cluster_sr/lv_sharedroot"
                         ]
        self.name="ocfs2"
        BaseTestFileSystem.__init__(self, method)

testclasses=[TestGfsFileSystem, TestExt2FileSystem, TestExt3FileSystem, TestOcfs2FileSystem]
testmethods=[ "testMount", "testUmountDev", "testUmountDir", "testGetName", "testFormatDevice", "testLabelDevice", "testCheckFs", "testGetLabel" ]
if __name__ == "__main__":
    oldmode=ComSystem.getExecMode()
    ComSystem.setExecMode(ComSystem.SIMULATE)
    #import sys;sys.argv = ['', 'Test.testName']
    suite=unittest.TestSuite()
    for testclass in testclasses:
        for testmethod in testmethods:
            suite.addTest(testclass(testmethod))

    runner=unittest.TextTestRunner()
    runner.run(suite)
    ComSystem.setExecMode(oldmode)