'''
Created on 17.03.2011

@author: marc
'''
import unittest
from comoonics import ComSystem
import logging

class Test(unittest.TestCase):
    def setUp(self):
        import tempfile
        import os
        from comoonics.tools.ComSystemInformation import SystemInformation
        from comoonics.tools.ComSysreport import Sysreport
        self.tmpdir=tempfile.mkdtemp()
        print("tmpdir: %s" %self.tmpdir)

        self.systeminformation=SystemInformation()
        self.sysreportdir="."
        print "sysreportdir: %s, cwd: %s" %(self.sysreportdir, os.path.realpath(os.path.curdir))
        self.sysreport=Sysreport(self.systeminformation, self.tmpdir, None, self.sysreportdir)

    def testName(self):
        tests2execute=[u'sysreport-linux-base', u'sysreport-linux-network', u'sysreport-linux-network-enhanced', u'sysreport-linux-boot', u'sysreport-linux-proc', u'sysreport-linux-logs', u'sysreport-linux-filesystem']
        result=self.sysreport.getSetNames()
        self.assertEquals(tests2execute, result, "Tests2execute should be %s but is %s." %(tests2execute, result))

    def testDoSets1(self):
        self.__testDoSet('sysreport-linux-base')
        
    def __testDoSet(self, name):
        try:
            self.sysreport.doSets([name])
        except Exception, e:
#            import traceback
#            trace=traceback.format_exc()
            self.fail("Could not execute sysreport modificationset %s, error: %s" %(name, e))
            
if __name__ == "__main__":
    logging.basicConfig()
    ComSystem.__EXEC_REALLY_DO=""
#    ComLog.setLevel(logging.DEBUG)
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()