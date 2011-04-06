'''
Created on 31.03.2011

@author: marc
'''
import unittest
from comoonics.cmdb.ComSoftwareCMDB import SoftwareCMDB
from comoonics.cmdb.Converter import getConverter

class Test(unittest.TestCase):
    def setUp(self):
        self.software_cmdb=SoftwareCMDB(hostname="axqad107-1", user="cmdb", password="cmdb", database="software_cmdb", table="software_cmdb")
        self.packages=self.software_cmdb.getPackages(["lilr642", "lilr602"], "lilr601", None, 0, 0, ['name LIKE "%GFS-kernel%"'])
        self.differences=self.packages.differences()

    def tearDown(self):
        pass
    
    def testconvertcolnames(self):
        self.converter=getConverter("coladdmasterdiffs/dict")(self.differences, "lilr601")
        self.converter.convert()
        rescolnames=['source: name', 'name', 'architecture', 'master: version', 'master: subversion', 'source: version', 'source: subversion', "id"]
        colnames=self.converter.columnnames
        self.assertEquals(colnames, rescolnames)
    
    def testconvert(self):
        self.converter=getConverter("coladdmasterdiffs/dict")(self.differences, "lilr601")
        self.converter.convert()
        rows=self.converter.getvalue()
        print ",\n".join(map(str, rows))
        result=[{'master: subversion': '72.2.0.2', 'name': 'GFS-kernel-debuginfo', 'source: subversion': 'not installed', 'source: name': 'lilr642', 'architecture': 'x86_64', 'source: version': 'not installed', 'id': 'id1', 'master: version': '2.6.9'},
{'master: subversion': '72.2.0.2', 'name': 'GFS-kernel-debuginfo', 'source: subversion': 'not installed', 'source: name': 'lilr602', 'architecture': 'x86_64', 'source: version': 'not installed', 'id': 'id2', 'master: version': '2.6.9'},
{'master: subversion': 'not installed', 'name': 'GFS-kernel-debuginfo', 'architecture': 'x86_64', 'source: name': 'lilr602', 'source: subversion': '80.9.el4_7.5.hotfix.1', 'source: version': '2.6.9', 'id': 'id1', 'master: version': 'not installed'},
{'master: subversion': 'not installed', 'name': 'GFS-kernel-largesmp', 'architecture': 'x86_64', 'source: name': 'lilr642', 'source: subversion': '80.9.el4_7.1', 'source: version': '2.6.9', 'id': 'id2', 'master: version': 'not installed'},
{'master: subversion': '80.9.el4_7.5.hotfix.1', 'name': 'GFS-kernel-largesmp', 'source: subversion': 'not installed', 'source: name': 'lilr642', 'architecture': 'x86_64', 'source: version': 'not installed', 'id': 'id1', 'master: version': '2.6.9'}
                ]
        self.assertEquals(rows, result)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()