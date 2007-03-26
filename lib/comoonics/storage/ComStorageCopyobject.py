"""
CopyObject implementation for Storage implementations.
"""

# here is some internal information
# $Id: ComStorageCopyobject.py,v 1.2 2007-03-26 08:12:22 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/Attic/ComStorageCopyobject.py,v $

from comoonics.enterprisecopy.ComCopyObject import CopyObjectJournaled
from comoonics.storage.ComStorage import Storage
from comoonics import ComLog
from comoonics.ComDisk import Disk

"""
Dictionary to hold all storageconnections keyed by connectionname. In order to achieve only one connection each
StorageObject.
"""

class StorageCopyObject(CopyObjectJournaled):
    __logStrLevel__="StorageCopyObject"
    def __new__(cls, *args, **kwds):
        return object.__new__(cls)
    def __init__(self, element, doc, storage):
        super(StorageCopyObject, self).__init__(element, doc)
        self.storage=storage
        self.addToUndoMap(self.storage.__class__.__name__, "add", "delete")
        self.addToUndoMap(self.storage.__class__.__name__, "add_clone", "delete_clone")
        self.addToUndoMap(self.storage.__class__.__name__, "add_snapshot", "delete_snapshot")
        self.addToUndoMap(self.storage.__class__.__name__, "map_luns", "unmap_luns")
        self.disk=Disk(self.getElement().getElementsByTagName("disk")[0], self.getDocument())

    def prepareAsSource(self):
        ''' prepare CopyObject as source '''
        self.storage.connect()

    def cleanupSource(self):
        ''' do source specific cleanup '''
        self.storage.close()

    def cleanupDest(self):
        ''' do destination specific cleanup '''
        self.storage.close()

    def prepareAsDest(self):
        ''' prepare CopyObject as destination '''
        self.storage.connect()

    def getMetaData(self):
        ''' returns the metadata element '''
        pass

    def updateMetaData(self, element):
        ''' updates meta data information '''
        pass

    def getDisk(self):
        """ returns the diskelement as Disk Object """
        return self.disk

    def doAction(self, action, sourcecopyobject):
        """ does what it is required to do """
        return self._action(action, sourcecopyobject)

    def _action(self, action, sourcecopyobject):
        methodname="%s_%s" %(action, self.getAttribute("type"))
        mylogger.debug("%s.undoAction(%s, %s, %s)" %(self.storage.getConnectionName(), action, self.getDisk(), sourcecopyobject))
        method=getattr(self.storage, methodname)
        returncode=method(self.getDisk(), sourcecopyobject.getDisk())
        if returncode:
            self.journal(self.storage, methodname, self.getDisk(), sourcecopyobject)
        return returncode

mylogger=ComLog.getLogger(StorageCopyObject.__logStrLevel__)


########################
# $Log: ComStorageCopyobject.py,v $
# Revision 1.2  2007-03-26 08:12:22  marc
# - added support for undoing and journaling
#
# Revision 1.1  2007/02/09 11:36:16  marc
# initial revision
#
