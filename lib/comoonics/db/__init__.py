"""

Init this package

"""

from comoonics import ComLog
from ComDBLogger import DBLogger
from ComDBObject import DBObject, NoDataFoundForObjectException, loadDBObjectsRegistry, setDBObjectsRegistry, registerDBObjectProperties, getDBObjectProperties, hasDBObjectProperties
from ComDBJobs import DBJobs, DBJob, DBAction, DBJob2Action, registerActionObject, JobException
ComLog.registerHandler("DBLogger", DBLogger)

########
# $Log: __init__.py,v $
# Revision 1.4  2008-02-28 14:19:09  marc
# - added autoimports.
# - added the dbobject and dbjobs
#
# Revision 1.3  2007/06/19 15:10:07  marc
# fixed importing
#
# Revision 1.2  2007/06/13 09:03:52  marc
# - using new ComLog api
# - default importing of ComDBLogger and registering at ComLog
#
# Revision 1.1  2007/04/02 11:21:23  marc
# For Hilti RPM Control:
# - initial revision
#
# Revision 1.1  2007/03/05 16:10:30  marc
# first rpm version
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#