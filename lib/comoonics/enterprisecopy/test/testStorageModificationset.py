'''
Created on Mar 3, 2010

@author: marc
'''
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        import sys
        cwd=sys.argv[0]
        self.cwd=cwd[:cwd.rfind("/")]

    def testStorageModificationSet1(self):
        xml_dump="""
    <modificationset type="storage" action="add" id="basestoragesystem" implementation="comoonics.storage.hp.ComHP_EVA_Storage" system="127.0.0.1/EVA5000" username="Administrator" password="Administrator" cmd="%s/hp/ComHP_EVA_SSSU_Sim.py">
        <disk name="Virtual Disks/atix/sourcedisk">
            <properties>
                <property name="size" value="10"/>
                <property name="disk_group" value="146er"/>
            </properties>
        </disk>
    </modificationset>
""" %(self.cwd)
        self.__testModificationsetFromXMLDump(xml_dump)
        
    def testStorageModificationSet2(self):
        xml_dump="""
    <modificationset type="storage" action="map_luns" id="basestoragesystem" implementation="comoonics.storage.hp.ComHP_EVA_Storage" system="127.0.0.1/EVA5000" username="Administrator" password="Administrator" cmd="%s/hp/ComHP_EVA_SSSU_Sim.py">
        <disk name="Virtual Disks/atix/sourcedisk">
            <mapping lun="0">
                <host name="server1"/>
            </mapping>
        </disk>
    </modificationset>""" %(self.cwd)
        self.__testModificationsetFromXMLDump(xml_dump)

    def __testModificationsetFromXMLDump(self, xml_dump):
        from xml.dom.ext.reader import Sax2
        from comoonics.enterprisecopy.ComStorageModificationset import StorageModificationset 
        reader=Sax2.Reader(validate=0)
        doc=reader.fromString(xml_dump)
        sms=StorageModificationset(doc.documentElement, doc)
        sms.doModifications()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()