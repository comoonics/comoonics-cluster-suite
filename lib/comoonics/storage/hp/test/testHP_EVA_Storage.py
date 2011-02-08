'''
Created on Mar 3, 2010

@author: marc
'''
import unittest


class Test(unittest.TestCase):
    
    def setUp(self):
        from comoonics.storage.hp.ComHP_EVA_Storage import HP_EVA_Storage
        from comoonics import XmlTools
        from comoonics.storage.ComDisk import StorageDisk
        #mylogger.debug("xml: %s" %(match.group(1)))
        xml_dump="""
        <disk name="Virtual Disks/atix/sourcedisk">
            <properties>
                <property name="size" value="10"/>
                <property name="disk_group" value="146er"/>
            </properties>
        </disk>
"""
        doc=XmlTools.parseXMLString(xml_dump)
        self.disk=StorageDisk(doc.documentElement, doc)
        self.storage=HP_EVA_Storage(system="127.0.0.1/EVA5000", username="Administrator", password="Administrator", autoconnect=True, cmd="../ComHP_EVA_SSSU_Sim.py")
        xml_dump="""
        <disk name="Virtual Disks/atix/sourcedisk_snap">
            <mapping lun="1">
                <host name="server1"/>
            </mapping>
        </disk>
"""
        doc=XmlTools.parseXMLString(xml_dump)
        self.snapdisk=StorageDisk(doc.documentElement, doc)

    def testDiskProperties(self):
        results={"size": "10" , "disk_group": "146er" } 
        for property in self.disk.getProperties().iter():
            self.assertEquals(property.getAttribute("value"), results[property.getAttribute("name")], "disk property[%s]: %s != %s" %(property.getAttribute("name"), property.getAttribute("value"), results[property.getAttribute("name")]))
    
    def testAddDisk(self):
        try:
            self.storage.add(self.disk)
        except Exception, e:
            self.assert_("Caught exception %s during disk adding %s" %(e, self.disk))
    
    def testRemoveDisk(self):
        try:
            self.storage.add(self.disk)
            self.storage.delete(self.disk)
        except Exception, e:
            self.assert_("Caught exception %s during disk removing %s" %(e, self.disk))
    
    def testAddLuns(self):
        try:
            self.storage.map_luns(self.snapdisk)
        except Exception, e:
            self.assert_("Caught exception %s during disklun mapping %s" %(e, self.snapdisk))

    def testUnmapLuns(self):
        try:
            self.storage.map_luns(self.snapdisk)
            self.storage.unmap_luns(self.snapdisk)
        except Exception, e:
            self.assert_("Caught exception %s during disklun unmapping %s" %(e, self.snapdisk))

    def tearDown(self):
        self.storage.close()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()