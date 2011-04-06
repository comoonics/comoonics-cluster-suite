'''
Created on 25.03.2011

@author: marc
'''
import unittest
from comoonics.tools.poptparse import PersistentOptionParser, make_option
import os.path

class TestPersistentOptionParser(unittest.TestCase):


    def setUp(self):
        options=[ make_option("--param1", action="store", type="string", default="default1"),
                  make_option("--param2", action="store_true", default=False),
                  make_option("--param3", action="store", type="int", default=False),
                  make_option("--param4", action="store", type="float", default=False),
                  make_option("--param5", action="store", type="string", default=False),
                  make_option("--param6", action="store", type="string", default="default6")]
                 
        self.parser=PersistentOptionParser(usage="testapp [options]", option_list=options, prog="testapp")
        self.parser.setLocalDefaultsFilename(os.path.join(os.path.dirname(__file__), "testapp-local.cfg"))
        self.parser.setGlobalDefaultsFilename(os.path.join(os.path.dirname(__file__), "testapp.cfg"))

    def tearDown(self):
        pass

    def testParam1(self):
        options, args=self.parser.parse_args([])
#        print options.param1
        self.assertEquals(options.param1, "defautparam1 overwritten")
        
    def testParam2(self):
        options, args=self.parser.parse_args([])
#        print options.param2
        self.assertEquals(options.param2, True)
        
    def testParam3(self):
        options, args=self.parser.parse_args([])
#        print options.param3
        self.assertEquals(options.param3, 4)
        
    def testParam4(self):
        options, args=self.parser.parse_args([])
#        print options.param4
        self.assertEquals(options.param4, 4.0)
        
    def testParam5(self):
        options, args=self.parser.parse_args([])
#        print options.param5
        self.assertEquals(options.param5, "testdir/test123")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()