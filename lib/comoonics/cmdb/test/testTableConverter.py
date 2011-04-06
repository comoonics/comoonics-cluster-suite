'''
Created on 31.03.2011

@author: marc
'''
import unittest
from comoonics.cmdb.ComSoftwareCMDB import SoftwareCMDB
from comoonics.cmdb.Converter import TableConverter

class Test(unittest.TestCase):
    def setUp(self):
        self.software_cmdb=SoftwareCMDB(hostname="axqad107-1", user="cmdb", password="cmdb", database="software_cmdb", table="software_cmdb")
        self.packages=self.software_cmdb.getPackages(["lilr642", "lilr602"], "lilr601", None, 0, 0, ['name LIKE "%GFS-kernel%"'])
        self.differences=self.packages.differences()

    def tearDown(self):
        pass
    
    def testconvertcolnames(self):
        self.converter=TableConverter(self.differences)
        self.converter.convert()
        rescolnames=['name', 'architecture', 'version', 'subversion', 'lilr601', 'lilr642', 'lilr602']
        colnames=self.converter.columnnames
        self.assertEquals(colnames, rescolnames)
    
    def testconvert(self):
        self.converter=TableConverter(self.differences)
        self.converter.convert()
        rows=self.converter.getvalue()
        #print self.converter.columnnames
        #print ",\n".join(map(str, rows))
        result=[['GFS-kernel-debuginfo', 'x86_64', '2.6.9', '72.2.0.2', 'installed', 'not installed', 'not installed'], 
                ['GFS-kernel-debuginfo', 'x86_64', '2.6.9', '80.9.el4_7.5.hotfix.1', 'not installed', 'not installed', 'installed'], 
                ['GFS-kernel-largesmp', 'x86_64', '2.6.9', '80.9.el4_7.1', 'not installed', 'installed', 'not installed'], 
                ['GFS-kernel-largesmp', 'x86_64', '2.6.9', '80.9.el4_7.5.hotfix.1', 'installed', 'not installed', 'installed']]
        self.assertEquals(rows, result)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()