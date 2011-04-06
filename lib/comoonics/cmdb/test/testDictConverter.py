'''
Created on 31.03.2011

@author: marc
'''
import unittest
from comoonics.cmdb.ComSoftwareCMDB import SoftwareCMDB
from comoonics.cmdb.Converter import DictConverter

class Test(unittest.TestCase):
    def setUp(self):
        self.software_cmdb=SoftwareCMDB(hostname="axqad107-1", user="cmdb", password="cmdb", database="software_cmdb", table="software_cmdb")
        self.packages=self.software_cmdb.getPackages(["lilr642", "lilr602"], "lilr601", None, 0, 0, ['name LIKE "%GFS-kernel%"'])
        self.differences=self.packages.differences()

    def tearDown(self):
        pass
    
    def testconvertcolnames(self):
        self.converter=DictConverter(self.differences)
        self.converter.convert()
        rescolnames=['name', 'architecture', 'version', 'subversion', 'lilr601', 'lilr642', 'lilr602']
        colnames=self.converter.columnnames
        self.assertEquals(colnames, rescolnames)
    
    def testconvert(self):
        self.converter=DictConverter(self.differences)
        self.converter.convert()
        rows=self.converter.getvalue()
        print ",\n".join(map(str, rows))
        result=[
                {'lilr601': 'installed', 'lilr602': 'not installed', 'name': 'GFS-kernel-debuginfo', 'subversion': '72.2.0.2', 'version': '2.6.9', 'architecture': 'x86_64', 'lilr642': 'not installed'},
                {'lilr601': 'not installed', 'lilr602': 'installed', 'name': 'GFS-kernel-debuginfo', 'subversion': '80.9.el4_7.5.hotfix.1', 'version': '2.6.9', 'architecture': 'x86_64', 'lilr642': 'not installed'},
                {'lilr601': 'not installed', 'lilr602': 'not installed', 'name': 'GFS-kernel-largesmp', 'subversion': '80.9.el4_7.1', 'version': '2.6.9', 'architecture': 'x86_64', 'lilr642': 'installed'},
                {'lilr601': 'installed', 'lilr602': 'installed', 'name': 'GFS-kernel-largesmp', 'subversion': '80.9.el4_7.5.hotfix.1', 'version': '2.6.9', 'architecture': 'x86_64', 'lilr642': 'not installed'}
                ]
        self.assertEquals(rows, result)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()