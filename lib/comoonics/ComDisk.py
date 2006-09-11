"""Comoonics disk module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComDisk.py,v 1.3 2006-09-11 16:47:48 mark Exp $
#


__version__ = "$Revision: 1.3 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/Attic/ComDisk.py,v $

import os
import exceptions

import ComSystem
from ComDataObject import DataObject
from ComExceptions import *

CMD_SFDISK = "/sbin/sfdisk"
CMD_DD="/bin/dd"

class Disk(DataObject):
    """ Disk represents a raw disk """
    def __init__(self, element, doc):
        """ creates a Disk object
        """
        DataObject.__init__(self, element, doc)
        self.log=ComLog.getLogger("Disk")

    def getLog(self):
        return self.log

    def exists(self):
        return os.path.exists(self.getAttribute("name"))

    def getDeviceName(self):
        """ returns the Disks device name (e.g. /dev/sda) """
        return self.getAttribute("name")

    def getDevicePath(self):
        return self.getDeviceName()

    def createPartition(self):
        """ creates a new partition (Not Implemented Yet)"""
        raise exceptions.NotImplementedError()
        pass

    def savePartitionTable(self, filename):
        """ saves the Disks partition table in sfdisk format to <filename>
        Throws ComException on error
        """
        __cmd = self.getDumpStdout() + " > " + filename
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        self.log.debug("savePartitionTable( " + filename + "):\n " + __ret)
        if __rc != 0:
            raise ComException(__cmd)

    def getPartitionTable(self):
        rc, rv = ComSystem.execLocalGetResult(self.getDumpStdout())
        if rc == 0:
            return rv
        return list()

    def getDumpStdout(self):
        """ returns the command string for dumping partition information
        see sfdisk -d
        """
        return CMD_SFDISK + " -d " + self.getDeviceName()

    def hasPartitionTable(self):
        """ checks wether the disk has a partition table or not """
        #__cmd = CMD_SFDISK + " -Vq " + self.getDeviceName() + " >/dev/null 2>&1"
        #if ComSystem.execLocal(__cmd):
        #    return False
        #return True
        __cmd = CMD_SFDISK + " -l " + self.getDeviceName()
        rc, std, err = ComSystem.execLocalGetResult(__cmd, True)
        if rc!=0:
            return False
        if (" ".join(err).upper().find("ERROR")) > 0:
            return False
        return True



    def deletePartitionTable(self):
        """ deletes the partition table """
        __cmd = CMD_DD + " if=/dev/zero of=" + self.getDeviceName() + " bs=512 count=2 >/dev/null 2>&1"
        if ComSystem.execLocal(__cmd):
            return False
        return self.rereadPartitionTable()

    def rereadPartitionTable(self):
        """ rereads the partition table of a disk """
        __cmd = CMD_SFDISK + " -R " + self.getDeviceName() + " >/dev/null 2>&1"
        if ComSystem.execLocal(__cmd):
            return False
        return True

    def restorePartitionTable(self, filename):
        """ writes partition table stored in <filename> to Disk.
        Note, that the format has to be sfdisk stdin compatible
        see sfdisk -d
        Throws ComException on error
        """
        __cmd = self.getRestoreStdin(True) + " < " + filename
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        self.log.debug("restorePartitionTable( " + filename + "):\n " + __ret)
        if __rc != 0:
            raise ComException(__cmd)

    def getRestoreStdin(self, force=False):
        """ returns command string to restore a partition table
        config from sfdisk stdin
        see sfdisk < config
        """
        __cmd = [CMD_SFDISK]
        if force:
            __cmd.append("--force")
        __cmd.append(self.getDeviceName())
        return " ".join(__cmd)

# $Log: ComDisk.py,v $
# Revision 1.3  2006-09-11 16:47:48  mark
# modified hasPartitionTable to support gnbd devices
#
# Revision 1.2  2006/07/20 10:24:42  mark
# added getPartitionTable method
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.8  2006/07/05 12:29:34  mark
# added sfdisk --force option
#
# Revision 1.7  2006/07/03 13:02:51  mark
# moved devicefile check in exists() methos
#
# Revision 1.6  2006/07/03 09:27:12  mark
# added some methods for partition management
# added device check in constructor
#
# Revision 1.5  2006/06/29 08:17:16  mark
# added some comments
#
# Revision 1.4  2006/06/28 17:23:46  mark
# modified to use DataObject
#
# Revision 1.3  2006/06/23 16:17:16  mark
# removed devicefile check because there is a bug
#
# Revision 1.2  2006/06/23 11:58:32  mark
# moved Log to bottom
#
# Revision 1.1  2006/06/23 07:56:24  mark
# initial checkin (stable)
#
