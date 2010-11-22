'''
Created on Mar 3, 2010

@author: marc
'''
import unittest


class Test(unittest.TestCase):


    def testName(self):
        import sys
        cwd=sys.argv[0]
        cwd=cwd[:cwd.rfind("/")]
        xml_dump="""
    <copyset name="snapdisk" type="storage" action="add" implementation="comoonics.storage.hp.ComHP_EVA_Storage" system="127.0.0.1/EVA5000" username="Administrator" password="Administrator" cmd="%s/hp/ComHP_EVA_SSSU_Sim.py">
        <source type="volume"><disk name="Virtual Disks/atix/sourcedisk/ACTIVE"/></source>
        <destination type="snapshot">
            <disk name="sourcedisk_snap">
                <properties>
                    <!-- Fully or demand -->
                    <property name="ALLOCATION_POLICY" value="Fully"/>
                    <!-- vraid0, vraid1, vraid5 -->
                    <property name="Redundancy" value="VRaid0"/>
                </properties>
            </disk>
        </destination>
    </copyset>
""" %(cwd)
        self.__testCopysetFromXMLDump(xml_dump)

    def __testCopysetFromXMLDump(self, xml_dump):
        import comoonics.XmlTools
        from comoonics.enterprisecopy.ComStorageCopyset import StorageCopyset
        #mylogger.debug("xml: %s" %(match.group(1)))
        doc=comoonics.XmlTools.parseXMLString(xml_dump)
        scs=StorageCopyset(doc.documentElement, doc)
        scs.doCopy()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()