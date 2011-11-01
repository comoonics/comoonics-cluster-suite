""" Comoonics partition copyset module

Example Configuration:
<destination>
    <disk>
        <partition name="1" type="primary" size="10G">
            <flag name="boot"/>
        </partition>
        <partition name="2" type="primary" size="20%"/>
        <partition name="3" type="primary" size="REMAIN">
            <flag name="lvm"/>
        </partition>
    </disk>
</destination>

supported size attributes:
    [0-9]+[M,G] size in mega/gigabytes
    1-100%: size in percentage of the whole disk
    REMAIN: all remaining space
    [0-9]+ size in sectors
supported type attributes:
    primary
    extended
    logical
supported flag name attributes: Note, that some may not be supported by the disk type
    boot
    root
    swap
    hidden
    raid
    lvm
    lba
"""


# here is some internal information
# $Id: ComPartitionCopyset.py,v 1.6 2010-03-08 12:30:48 marc Exp $
#


__version__ = "$Revision: 1.6 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComPartitionCopyset.py,v $

import os
import re

from ComCopyset import CopysetJournaled
from ComCopyObject import getCopyObject
from comoonics.ComExceptions import *
from comoonics import ComSystem, ComLog

__logStrLevel__ = "PartitionCopyset"
class PartitionCopyset(CopysetJournaled):
    def __init__(self, element, doc):
        CopysetJournaled.__init__(self, element, doc)
        try:
            __source=element.getElementsByTagName('source')[0]
            self.source=getCopyObject(__source, doc)
        #except Exception, e:
        except Exception, e:
            ComLog.getLogger(__logStrLevel__).warning(e)
            raise ComException("source for copyset not defined")
        try:
            __dest=element.getElementsByTagName('destination')[0]
            self.dest=getCopyObject(__dest, doc)
        except Exception, e:
        #except None:
            print ("EXCEPTION: %s\n" %e)
            ComLog.getLogger(__logStrLevel__).warning(e)
            raise ComException("destination for copyset not defined")

    def doCopy(self):
        # do everything

        self.source.prepareAsSource()

        # Update MetaData
        self.dest.updateMetaData(self.source.getMetaData())

        self.dest.prepareAsDest()

        self.source.cleanupSource()
        self.dest.cleanupDest()

    def undoCopy(self):
        self.source.cleanup()
        self.dest.cleanup()
        super(PartitionCopyset, self).undoCopy()

    def __doCopy_alt(self):
        __tmp=os.tempnam("/tmp")
        if not self.needPartitionTableUpdate():
            ComLog.getLogger("Copyset").debug("partition tables are the same. No need to update")
        else:
            if self.destination.hasPartitionTable():
                self.destination.savePartitionTable(__tmp)
                self.journal(self.destination, "savePartitionTable", __tmp)
            else:
                self.journal(self.destination, "noPartitionTable")
            if self.source.hasPartitionTable():
                __cmd = self.source.getDumpStdout()
                __cmd += " | "
                __cmd += self.destination.getRestoreStdin(True)
                __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
                ComLog.getLogger("Copyset").debug(__cmd + ": " + __ret)
                if __rc != 0:
                    raise ComException(__cmd + __ret)
            else:
                if not self.destination.deletePartitionTable():
                    raise ComException("Partition table on device %s coud not be deleted",
                                       self.destination.getDeviceName())


    def needPartitionTableUpdate(self):
        """ compares the partition tables of source and destination
        returns True if they are not the same """
        n_table=list()
        d_table=self.destination.getPartitionTable()
        s_table=self.source.getPartitionTable()
        for i in range(len(s_table)):
            n_table.append(re.sub(self.source.getDeviceName(), \
                                  self.destination.getDeviceName(), \
                                  s_table[i]))
        if d_table == n_table:
            return False
        else:
            return True
