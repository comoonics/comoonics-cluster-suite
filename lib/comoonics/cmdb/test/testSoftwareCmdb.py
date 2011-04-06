'''
Created on Dec 10, 2010

@author: marc
'''
def formatRow(_row, _colnames):
    orderedrow=list()
    for colname in _colnames:
        orderedrow.append(str(_row[colname]))
    return ', '.join(orderedrow)

def formatColNames(_row):
    return ', '.join(_row)

from comoonics.cmdb.ComSoftwareCMDB import SoftwareCMDB
import logging
logging.basicConfig()
from comoonics import ComLog
ComLog.setLevel(logging.DEBUG)
import unittest
from comoonics.cmdb.ComSoftwareCMDB import Package, Packages
Package.DEFAULT_HASHLEVEL=4

class Test(unittest.TestCase):

    def setUp(self):
        self.software_cmdb=SoftwareCMDB(hostname="axqad107-1", user="cmdb", password="cmdb", database="software_cmdb", table="software_cmdb")

    def testgetPackages(self):
        result=self.software_cmdb.getPackages(["lilr642", "lilr602"], "lilr601", None, 0, 0, ['name LIKE "%GFS-kernel%"'])
        expectedresult=Packages(
                                Package(name="GFS-kernel-largesmp", architecture="x86_64", version="2.6.9", subversion="80.9.el4_7.1", sources=['lilr642'], allsources=['lilr601', 'lilr642', 'lilr602'], hashlevel=4),
                                Package(name="GFS-kernel-debuginfo", architecture="x86_64", version="2.6.9", subversion="80.9.el4_7.5.hotfix.1", sources=['lilr602'], allsources=['lilr601', 'lilr642', 'lilr602'], hashlevel=4),
                                Package(name="GFS-kernel-largesmp", architecture="x86_64", version="2.6.9", subversion="80.9.el4_7.20", sources=['lilr601', 'lilr642', 'lilr602'], allsources=['lilr601', 'lilr642', 'lilr602'], hashlevel=4),
                                Package(name="GFS-kernel-debuginfo", architecture="x86_64", version="2.6.9", subversion="72.2.0.2", sources=['lilr601'], allsources=['lilr601', 'lilr642', 'lilr602'], hashlevel=4),
                                Package(name="GFS-kernel-largesmp", architecture="x86_64", version="2.6.9", subversion="80.9.el4_7.5.hotfix.1", sources=['lilr601', 'lilr602'], allsources=['lilr601', 'lilr642', 'lilr602'], hashlevel=4)
                                )
        print repr(result)
        self.assertEquals(result, expectedresult)
        
    def testgetDifferencesMaster(self):
        expectedresult=Packages(
                                Package(name="GFS-kernel-largesmp", architecture="x86_64", version="2.6.9", subversion="80.9.el4_7.1", sources=['lilr642'], allsources=['lilr601', 'lilr642', 'lilr602'], hashlevel=4),
                                Package(name="GFS-kernel-debuginfo", architecture="x86_64", version="2.6.9", subversion="80.9.el4_7.5.hotfix.1", sources=['lilr602'], allsources=['lilr601', 'lilr642', 'lilr602'], hashlevel=4),
                                Package(name="GFS-kernel-debuginfo", architecture="x86_64", version="2.6.9", subversion="72.2.0.2", sources=['lilr601'], allsources=['lilr601', 'lilr642', 'lilr602'], hashlevel=4),
                                Package(name="GFS-kernel-largesmp", architecture="x86_64", version="2.6.9", subversion="80.9.el4_7.5.hotfix.1", sources=['lilr601', 'lilr602'], allsources=['lilr601', 'lilr642', 'lilr602'], hashlevel=4)
                                )
        result=self.software_cmdb.getPackages(["lilr642", "lilr602"], "lilr601", None, 0, 0, ['name LIKE "%GFS-kernel%"'])
        result=result.differences()
        print repr(result)
        self.assertEquals(result, expectedresult)
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGetName']
    unittest.main()
    
#result=software_cmdb._getDiffsFromSources(["lilr602"], "lilr601", None, 0, 0, ['name LIKE "%bash%"'])
#print result
#result=software_cmdb._getDiffsFromSources(["lilr641", "lilr601", "lilr602"], None, None, 0, 0, ['name LIKE "%GFS-kernel%"'])
#print result

#colnames=software_cmdb.getColnamesForMaster()
#vrs=software_cmdb.getDiffsFromSourcesByMaster(["lilr641", "lilr602", "lilr621"], "lilr601", colnames, 0, 0, ['name="bash"'])
#print vrs
#row=vrs.fetch_row(1,1)
#select=None
#if not colnames:
#    colnames=row[0].keys()
#if not select:
#    select=colnames
#print formatColNames(select)
#while row:
#    print formatRow(row[0], select)
#    row=vrs.fetch_row(1,1)
#colnames=software_cmdb.getColnamesForMaster(True)
#vrs=software_cmdb.getDiffsFromSourcesByMaster(["lilr641", "lilr602", "lilr621"], "lilr601", colnames, 0, 0, ['name LIKE "%kernel%"'], None, True, True, True)
#print vrs
#row=vrs.fetch_row(1,1)
#select=None
#if not colnames:
#    colnames=row[0].keys()
#if not select:
#    select=colnames
#print formatColNames(select)
#while row:
#    print row
#    print formatRow(row[0], select)
#    row=vrs.fetch_row(1,1)
