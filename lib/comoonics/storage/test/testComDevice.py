'''
Created on Feb 26, 2010

@author: marc
'''
import unittest
from comoonics.XmlTools import parseXMLString
from comoonics.storage.ComDevice import Device
from comoonics.storage.ComMountpoint import MountPoint

class Test(unittest.TestCase):
    mountsfile="""
rootfs / rootfs rw 0 0
none /sys sysfs rw,nosuid,nodev,noexec,relatime 0 0
none /proc proc rw,nosuid,nodev,noexec,relatime 0 0
none /dev devtmpfs rw,relatime,size=3985412k,nr_inodes=996353,mode=755 0 0
none /dev/pts devpts rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000 0 0
fusectl /sys/fs/fuse/connections fusectl rw,relatime 0 0
/dev/mapper/mobilix--20-lv_root64bit / ext4 rw,relatime,errors=remount-ro,barrier=1,data=ordered 0 0
none /sys/kernel/debug debugfs rw,relatime 0 0
none /sys/kernel/security securityfs rw,relatime 0 0
none /dev/shm tmpfs rw,nosuid,nodev,relatime 0 0
none /var/run tmpfs rw,nosuid,relatime,mode=755 0 0
none /var/lock tmpfs rw,nosuid,nodev,noexec,relatime 0 0
/dev/mapper/mobilix--20-lv_tmp /tmp ext4 rw,relatime,barrier=1,data=ordered 0 0
/dev/mapper/mobilix--20-lv_data /data ext4 rw,relatime,barrier=1,data=ordered 0 0
nfsd /proc/fs/nfsd nfsd rw,relatime 0 0
binfmt_misc /proc/sys/fs/binfmt_misc binfmt_misc rw,nosuid,nodev,noexec,relatime 0 0
gvfs-fuse-daemon /data/home/marc/.gvfs fuse.gvfs-fuse-daemon rw,nosuid,nodev,relatime,user_id=500,group_id=100 0 0
/etc/auto.atix /atix autofs rw,relatime,fd=6,pgrp=22748,timeout=60,minproto=5,maxproto=5,indirect 0 0
nfs-server.gallien.atix:/mnt/methusalix/data/ATIX/projects /atix/projects nfs rw,relatime,vers=3,rsize=32768,wsize=32768,namlen=255,hard,proto=tcp,timeo=600,retrans=2,sec=sys,mountaddr=192.168.3.119,mountvers=3,mountport=736,mountproto=udp,local_lock=none,addr=192.168.3.119 0 0"""

    def setUp(self):
        import tempfile
        import os
        self.mountsfd, self.mountsfilename=tempfile.mkstemp()
        os.write(self.mountsfd, self.mountsfile)

    def tearDown(self):
        import os
        os.close(self.mountsfd)

    def testDevice1(self):
        devicexml=parseXMLString("""<disk name="/dev/mapper/mobilix--20-lv_tmp"/>""")
        device=Device(devicexml.documentElement, devicexml, mountsfile=self.mountsfilename)
        self.assertTrue(device.isMounted())

    def testDevice2(self):
        devicexml=parseXMLString("""<disk name="/dev/mapper/mobilix--20-lv_tmp2"/>""")
        device=Device(devicexml.documentElement, devicexml, mountsfile=self.mountsfilename)
        self.assertFalse(device.isMounted())

    def testMountpoint1(self):
        devicexml=parseXMLString("""<disk name="/dev/mapper/mobilix--20-lv_tmp"/>""")
        mountpointxml=parseXMLString("""<mountpoint name="/tmp"/>""")
        device=Device(devicexml.documentElement, devicexml, mountsfile=self.mountsfilename)
        mountpoint=MountPoint(mountpointxml.documentElement, mountpointxml)
        self.assertTrue(device.isMounted(mountpoint))

    def testMountpoint2(self):
        devicexml=parseXMLString("""<disk name="/dev/mapper/mobilix--20-lv_tmp"/>""")
        mountpointxml=parseXMLString("""<mountpoint name="/tmp2"/>""")
        mountpoint=MountPoint(mountpointxml.documentElement, mountpointxml)
        device=Device(devicexml.documentElement, devicexml, mountsfile=self.mountsfilename)
        self.assertFalse(device.isMounted(mountpoint))

    def testScanMountpoint1(self):
        devicexml=parseXMLString("""<disk name="/dev/mapper/mobilix--20-lv_tmp"/>""")
        device=Device(devicexml.documentElement, devicexml, mountsfile=self.mountsfilename)
        self.assertEquals(device.scanMountPoint(), ["/tmp", "ext4"])

    def testScanMountpoint2(self):
        devicexml=parseXMLString("""<disk name="/dev/mapper/mobilix--20-lv_tmp2"/>""")
        device=Device(devicexml.documentElement, devicexml, mountsfile=self.mountsfilename)
        self.assertEquals(device.scanMountPoint(), [None, None])
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()