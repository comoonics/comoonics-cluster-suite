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
software_cmdb=SoftwareCMDB(hostname="generix4", user="hoi", password="Digital", database="hoi_config", table="software_cmdb")
result=software_cmdb._getDiffsFromSources(["lilr641", "lilr602"], "lilr601", None, 0, 0, ['name LIKE "%GFS-kernel%"'])
print result
result=software_cmdb._getDiffsFromSources(["lilr641", "lilr601", "lilr602"], None, None, 0, 0, ['name LIKE "%GFS-kernel%"'])
print result

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
