'''
Created on Mar 2, 2010

@author: marc
'''
import unittest
from comoonics.storage.hp.ComHP_EVA_SSSU import HP_EVA_SSSU, HP_EVA_Object
class Test(unittest.TestCase):
    def setUp(self):
        log = file('/tmp/ComHP_EVA_SSSU.log','w')
        self.sssu=HP_EVA_SSSU("127.0.0.1", "Administrator", "Administrator", "EVA5000", True, "../ComHP_EVA_SSSU_Sim.py", log)

    def tearDown(self):
        self.sssu.disconnect()

    def testAddVDisk(self):
        try:
            self.sssu.cmd("add", ["vdisk", "myvdisk", "size=100"])
        except Exception, e:
            self.assert_("Caught exception %s during adding vdisk myvdisk." %e)

    def testLsVdisk(self):
        self.sssu.cmd("add", ["vdisk", "myvdisk", "size=100"])
        self.sssu.cmd("ls", "vdisk myvdisk")
        print "vdisk mydisk: %s" %(self.sssu.last_output)

    def testLsVdiskXml(self):
        self.sssu.cmd("add", ["vdisk", "myvdisk", "size=100"])
        self.sssu.cmd("ls", "vdisk myvdisk xml")
        if self.sssu.xml_output:
            print "vdisk mydisk as HP_EVA_Object:"
            vdisk=HP_EVA_Object.fromXML(self.sssu.xml_output)
            print vdisk
        else:
            print "no last xmloutput %s" %(self.sssu.xml_output)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()