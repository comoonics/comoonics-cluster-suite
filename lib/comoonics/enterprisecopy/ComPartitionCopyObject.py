""" Comoonics partition copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComPartitionCopyObject.py,v 1.5 2007-04-04 12:52:56 marc Exp $
#


__version__ = "$Revision: 1.5 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComPartitionCopyObject.py,v $

import os

from xml import xpath
from xml.dom.ext import PrettyPrint

from ComCopyObject import CopyObjectJournaled

from comoonics.ComDisk import HostDisk
from comoonics.ComExceptions import *


class PartitionCopyObject(CopyObjectJournaled):
    __logStrLevel__="PartitionCopyObject"

    def __init__(self, element, doc):
        CopyObjectJournaled.__init__(self, element, doc)
        try:
            __disk=xpath.Evaluate('disk', element)[0]
            self.disk=HostDisk(__disk, doc)
        except Exception:
            raise ComException("disk for copyset not defined")

        self.addToUndoMap(self.disk.__class__.__name__, "savePartitionTable", "restorePartitionTable")
        self.addToUndoMap(self.disk.__class__.__name__, "noPartitionTable", "deletePartitionTable")


    def prepareAsSource(self):
        for journal_command in self.disk.resolveDeviceName():
            self.journal(self.disk, journal_command)
        self.disk.initFromDisk()

    def prepareAsDest(self):
        for journal_command in self.disk.resolveDeviceName():
            self.journal(self.disk, journal_command)
        self.disk.initFromDisk()

    def cleanupSource(self):
        self.commitJournal()

    def cleanupDest(self):
        __tmp=os.tempnam("/tmp")
        if self.disk.hasPartitionTable():
            self.disk.savePartitionTable(__tmp)
            self.journal(self.disk, "savePartitionTable", __tmp)
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
# Revision 1.5  2007-04-04 12:52:56  marc
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
