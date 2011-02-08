'''
Created on Feb 26, 2010

@author: marc
'''
import unittest


class Test(unittest.TestCase):
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

    def _testDiskDump(self, dump):
        try:
            from comoonics.storage.ComDisk import StorageDisk
            from comoonics import XmlTools
            doc=XmlTools.parseXMLString(dump)
            StorageDisk(doc.documentElement, doc)
        except:
            self.fail("Could not create Disk for dump %s" %dump)

    def testDiskDumps(self):
        for disk_dump in self.disk_dumps:
            self._testDiskDump(disk_dump)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()