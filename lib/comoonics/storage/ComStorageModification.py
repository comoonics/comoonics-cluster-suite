"""
Comoonics storage modification module

"""
# here is some internal information
# $Id: ComStorageModification.py,v 1.1 2007-02-09 11:36:16 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/Attic/ComStorageModification.py,v $

from comoonics.enterprisecopy.ComModification import Modification
from comoonics.ComDisk import Disk
from comoonics import ComLog

class StorageModification(Modification):
    __logStrLevel__= "StorageModification"
    def __init__(self, element, doc, *args, **kwds):
        super(StorageModification, self)
        self.disk=Disk(element, doc)
        self.action=self.storage=None
        if kwds:
            for kwd in kwds:
                self.__setattr__(kwd, kwds[kwd])

    def doModification(self):
        if not self.action:
            return
        else:
            """ does what it is required to do """
            methodname="%s" %(self.action)
            mylogger.debug("%s.doAction(%s, %s)" %(self.storage.getConnectionName(), self.action, self.disk))
            method=getattr(self.storage, methodname)
            return method(self.disk)

mylogger=ComLog.getLogger(StorageModification.__logStrLevel__)

# $Log: ComStorageModification.py,v $
# Revision 1.1  2007-02-09 11:36:16  marc
# initial revision
#