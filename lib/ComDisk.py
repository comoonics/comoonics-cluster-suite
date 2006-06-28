"""Comoonics disk module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComDisk.py,v 1.4 2006-06-28 17:23:46 mark Exp $
#


__version__ = "$Revision: 1.4 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComDisk.py,v $

import os
import exceptions

import ComSystem
from ComDataObject import DataObject
from ComExceptions import *

CMD_SFDISK = "/sbin/sfdisk"

class Disk(DataObject):
    """ Disk represents a raw disk """
    def __init__(self, element, doc):
        """ creates a Disk object
        """
        DataObject.__init__(self, element, doc)
        #if not os.path.isfile( device ):
            #raise ComException(device + " not found")
        #    pass
        #self.__device=device
        self.log=ComLog.getLogger("Disk")

    def getLog(self):
        return self.log


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

    def getDumpStdout(self):
        return CMD_SFDISK + " -d " + self.getDeviceName()


    def restorePartitionTable(self, filename):
        """ writes partition table stored in <filename> to Disk.
        Note, that the format has to be sfdisk stdin compatible
        see sfdisk -d
        Throws ComException on error
        """
        __cmd = self.getRestoreStdin() + " < " + filename
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        self.log.debug("restorePartitionTable( " + filename + "):\n " + __ret)
        if __rc != 0:
            raise ComException(__cmd)

    def getRestoreStdin(self):
        return CMD_SFDISK + " " + self.getDeviceName()
    
# $Log: ComDisk.py,v $
# Revision 1.4  2006-06-28 17:23:46  mark
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
