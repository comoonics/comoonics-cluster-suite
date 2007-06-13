"""

Init this package

"""

import comoonics.ComLog
import ComDBLogger
comoonics.ComLog.registerHandler("DBLogger", ComDBLogger.DBLogger)

########
# $Log: __init__.py,v $
# Revision 1.2  2007-06-13 09:03:52  marc
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