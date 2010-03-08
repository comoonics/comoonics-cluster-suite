"""

Init this package

"""

from ComEMCLegatoBackupHandler import EMCLegatoBackupHandler
from exceptions import ImportError
from comoonics.storage.ComArchive import ArchiveHandlerFactory
ArchiveHandlerFactory.registerArchiveHandler(EMCLegatoBackupHandler)

#print ArchiveHandlerFactory

########
# $Log: __init__.py,v $
# Revision 1.2  2010-03-08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.1  2007/03/26 07:48:58  marc
# initial revision
#
# Revision 1.1  2007/03/05 16:10:30  marc
# first rpm version
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#