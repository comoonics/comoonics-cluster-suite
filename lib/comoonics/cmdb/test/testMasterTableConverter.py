'''
Created on 31.03.2011

@author: marc
'''
import unittest
from comoonics.cmdb.ComSoftwareCMDB import SoftwareCMDB
from comoonics.cmdb.Converter import TableMasterConverter

class Test(unittest.TestCase):
    def setUp(self):
        self.software_cmdb=SoftwareCMDB(hostname="axqad107-1", user="cmdb", password="cmdb", database="software_cmdb", table="software_cmdb")
        self.packages=self.software_cmdb.getPackages(["lilr642", "lilr602"], "lilr601", None, 0, 0, ['name LIKE "%GFS-kernel%"'])
        self.differences=self.packages.differences()

    def tearDown(self):
        pass

    def testconvertcolnames(self):
        self.converter=TableMasterConverter(self.differences, "lilr601")
        self.converter.convert()
        rows=self.converter.columnnames
        expectedresult=['source: name', 'name', 'architecture', 'master: version', 'master: subversion', 'source: version', 'source: subversion']
        self.assertEquals(rows, expectedresult)

    def testconvert(self):
        self.converter=TableMasterConverter(self.differences, "lilr601")
        self.converter.convert()
        rows=self.converter.getvalue()
        result=[['lilr642', 'GFS-kernel-debuginfo', 'x86_64', '2.6.9', '72.2.0.2', 'not installed', 'not installed'], ['lilr602', 'GFS-kernel-debuginfo', 'x86_64', '2.6.9', '72.2.0.2', 'not installed', 'not installed'], ['lilr602', 'GFS-kernel-debuginfo', 'x86_64', 'not installed', 'not installed', '2.6.9', '80.9.el4_7.5.hotfix.1'], ['lilr642', 'GFS-kernel-largesmp', 'x86_64', 'not installed', 'not installed', '2.6.9', '80.9.el4_7.1'], ['lilr642', 'GFS-kernel-largesmp', 'x86_64', '2.6.9', '80.9.el4_7.5.hotfix.1', 'not installed', 'not installed']]
        self.assertEquals(rows, result)
        #print self.converter.columnnames
        #print ",\n".join(map(str, rows))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()