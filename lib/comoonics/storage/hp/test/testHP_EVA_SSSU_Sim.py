'''
Created on Mar 2, 2010

@author: marc
'''
import unittest

from comoonics.storage.hp.ComHP_EVA_SSSU_Sim import returnHP_EVA_ObjectFromXML, HP_EVA_Storagecells

class Test(unittest.TestCase):
    def setUp(self):
        returnHP_EVA_ObjectFromXML("./system_dump.xml")
        returnHP_EVA_ObjectFromXML("./vdisk_dump.xml")
        returnHP_EVA_ObjectFromXML("./diskgroup_dump.xml")

    def testSimIds(self):
        ids=HP_EVA_Storagecells.ids()
        self.assertEquals(ids , [u'08000710B4080560D62E10000080000000001C00'], "Wrong ids %s but got 08000710B4080560D62E10000080000000001C00" %ids[0])

    def testSimNames(self):
        names=HP_EVA_Storagecells.names()
        self.assertEquals(names , [u'EVA5000'], "Wrong names %s but got EVA5000" %names[0])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()