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
        self.sysreportdir=os.path.dirname(__file__)
        print "sysreportdir: %s, cwd: %s" %(self.sysreportdir, os.path.realpath(os.path.curdir))
        self.sysreport=Sysreport(self.systeminformation, self.tmpdir, None, self.sysreportdir)

    def testName(self):
        possibletests2execute=[u'sysreport-redhat-base', u'sysreport-redhat-rhn', u'sysreport-redhat-selinux', u'sysreport-rpm', u'sysreport-linux-base', u'sysreport-linux-network', u'sysreport-linux-network-enhanced', u'sysreport-linux-boot', u'sysreport-linux-proc', u'sysreport-linux-logs', u'sysreport-linux-filesystem']
        tests2execute=self.sysreport.getSetNames()
        found=0
        for test2execute in tests2execute:
            if test2execute not in possibletests2execute:
                self.fail("Test %s in not in possibletests2execute %s." %(test2execute, possibletests2execute))
            else:
                found+=1
        if found < len(tests2execute):
            self.fail("Could not find all tests in possibletests. %s != %s" %(tests2execute, possibletests2execute))

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