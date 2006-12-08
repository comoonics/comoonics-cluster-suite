""" Comoonics partition copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComPartitionCopyObject.py,v 1.1 2006-12-08 09:42:26 mark Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComPartitionCopyObject.py,v $

import os

from xml import xpath
from xml.dom.ext import PrettyPrint

from ComCopyObject import CopyObjectJournaled

from comoonics.ComDisk import Disk
from comoonics.ComExceptions import *


class PartitionCopyObject(CopyObjectJournaled):
    __logStrLevel__="PartitionCopyObject"

    def __init__(self, element, doc):
        CopyObjectJournaled.__init__(self, element, doc)
        try:
            __disk=xpath.Evaluate('disk', element)[0]
            self.disk=Disk(__disk, doc)
        except Exception:
            raise ComException("disk for copyset not defined")

        self.addToUndoMap(self.disk.__class__.__name__, "savePartitionTable", "restorePartitionTable")
        self.addToUndoMap(self.disk.__class__.__name__, "noPartitionTable", "deletePartitionTable")


    def prepareAsSource(self):
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

    def prepareAsDest(self):
        pass

    def getMetaData(self):
        ''' returns the metadata element '''
        return self.disk.getElement()

    def updateMetaData(self, element):
        ''' updates meta data information '''
        self.disk.updateChildrenWithPK(Disk(element, None))

# $Log: ComPartitionCopyObject.py,v $
# Revision 1.1  2006-12-08 09:42:26  mark
# initial check in - stable
#
