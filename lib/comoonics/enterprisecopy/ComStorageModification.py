"""
Comoonics storage modification module

"""
# here is some internal information
# $Id: ComStorageModification.py,v 1.2 2011-02-08 13:04:19 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComStorageModification.py,v $

from comoonics.enterprisecopy.ComModification import ModificationJournaled
from comoonics.storage.ComDisk import StorageDisk
from comoonics import ComLog

class StorageModification(ModificationJournaled):
    __logStrLevel__= "StorageModification"
    def __init__(self, element, doc, *args, **kwds):
        super(StorageModification, self).__init__(element, doc)
        self.disk=StorageDisk(element, doc)
        self.action=self.storage=None
        if kwds:
            for kwd in kwds:
                self.__setattr__(kwd, kwds[kwd])
        if hasattr(self, "storage"):
            self.addToUndoMap(self.storage.__class__.__name__, "add", "delete")
            self.addToUndoMap(self.storage.__class__.__name__, "add_clone", "delete_clone")
            self.addToUndoMap(self.storage.__class__.__name__, "add_snapshot", "delete_snapshot")
            self.addToUndoMap(self.storage.__class__.__name__, "map_luns", "unmap_luns")

    def doModification(self):
        if not self.action:
            return
        else:
            """ does what it is required to do """
            methodname="%s" %(self.action)
            mylogger.debug("%s.doModification(%s, %s)" %(self.storage.getConnectionName(), self.action, self.disk))
            method=getattr(self.storage, methodname)
            returncode=method(self.disk)
            if returncode:
                self.journal(self.storage, methodname, self.disk)

mylogger=ComLog.getLogger(StorageModification.__logStrLevel__)

# $Log: ComStorageModification.py,v $
# Revision 1.2  2011-02-08 13:04:19  marc
# - removed unnecessary factory constructur for StorageDisk
#
# Revision 1.1  2010/03/08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.2  2007/03/26 08:14:10  marc
# - added support for undoing and journaling
#
# Revision 1.1  2007/02/09 11:36:16  marc
# initial revision
#