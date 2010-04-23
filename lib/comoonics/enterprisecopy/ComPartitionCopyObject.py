""" Comoonics partition copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComPartitionCopyObject.py,v 1.11 2010-04-23 10:55:27 marc Exp $
#


__version__ = "$Revision: 1.11 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComPartitionCopyObject.py,v $

import os

from ComCopyObject import CopyObjectJournaled

from comoonics.storage.ComDisk import HostDisk
from comoonics.ComExceptions import ComException
from comoonics import ComLog


class PartitionCopyObject(CopyObjectJournaled):
    __logStrLevel__="comoonics.enterprisecopy.PartitionCopyObject"
    logger=ComLog.getLogger(__logStrLevel__)

    def __init__(self, element, doc):
        CopyObjectJournaled.__init__(self, element, doc)
        try:
            __disk=element.getElementsByTagName('disk')[0]
            self.disk=HostDisk(__disk, doc)
        except Exception:
            raise ComException("disk for copyset not defined")

        self.addToUndoMap(self.disk.__class__.__name__, "savePartitionTable", "restorePartitionTable")
        self.addToUndoMap(self.disk.__class__.__name__, "noPartitionTable", "deletePartitionTable")
        # We need to have the tempfile globlally available because of it deleteing itself when not
        # referenced anymore.
        import tempfile
        self.__tmp=tempfile.NamedTemporaryFile()


    def prepareAsSource(self):
        for journal_command in self.disk.resolveDeviceName():
            self.journal(self.disk, journal_command)
        self.disk.initFromDisk()

    def prepareAsDest(self):
        for journal_command in self.disk.resolveDeviceName():
            self.journal(self.disk, journal_command)

    def cleanupSource(self):
        self.commitJournal()

    def cleanupDest(self):
        if self.disk.hasPartitionTable():
            self.disk.savePartitionTable(self.__tmp.name)
            self.journal(self.disk, "savePartitionTable", self.__tmp.name)
        else:
            self.journal(self.disk, "noPartitionTable")

        self.disk.createPartitions()
        self.disk.restore()

    def getMetaData(self):
        ''' returns the metadata element '''
        return self.disk.getElement()

    def updateMetaData(self, element):
        ''' updates meta data information '''
        self.disk.updateChildrenWithPK(HostDisk(element, None))

# $Log: ComPartitionCopyObject.py,v $
# Revision 1.11  2010-04-23 10:55:27  marc
# - moved tmpfile as private class variable
#
# Revision 1.10  2010/04/13 13:26:05  marc
# - removed os.tempnam
#
# Revision 1.9  2010/03/08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.8  2010/02/09 21:48:24  mark
# added .storage path in includes
#
# Revision 1.7  2007/09/07 14:39:41  marc
# -logging
#
# Revision 1.6  2007/04/11 14:34:29  mark
# resolves bz#44
#
# Revision 1.5  2007/04/04 12:52:56  marc
# MMG Backup Legato Integration
# - moved prepareAsDest
#
# Revision 1.4  2007/04/02 11:50:45  marc
# MMG Backup Legato Integration:
# - calling restore on Disk e.g. to deactivate vg
#
# Revision 1.3  2007/03/26 08:01:32  marc
# - added support for resolvDeviceName()
#
# Revision 1.2  2007/02/27 15:54:28  mark
# changed Disk to HostDisk
#
# Revision 1.1  2006/12/08 09:42:26  mark
# initial check in - stable
#
