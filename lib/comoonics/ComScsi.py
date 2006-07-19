"""Comoonics SCSI module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComScsi.py,v 1.1 2006-07-19 14:29:15 marc Exp $
#


__version__ = "$$"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/Attic/ComScsi.py,v $

import os
import sys
from types import *
from exceptions import *

import ComLog
import ComSystem
import ComUtils
from ComExceptions import *

class SCSI:
    def __init__(self):
        self.log=ComLog.getLogger("SCSI")

    def getAllSCSIHosts(self):
        try:
            return os.listdir("/sys/class/scsi_host")
        except Exception:
            #return ["host0", "host1"] 
            raise ComException("/sys/class/scsi_host not available")
        
        
    def rescan(self, __hosts, __bus, __target, __lun):
        """ Rescan SCSI
        invokes a rescan via /sys/class/scsi_host/hostH/scan interface
        IDEAS
        INPUTS
          * host - name of scsi host ( - for all )
          * bus - number of scsi bus (- for all )
          * target - number of target ( - for all )
          * lun - number of lun ( - for all )

        """
        __syspath = "/sys/class/scsi_host"

        if not os.path.isdir( __syspath ):
            raise ComException(__syspath + " not found")
            pass

    
        if __hosts == "-":
            __hosts=self.getAllSCSIHosts()

        if  not ( ComUtils.isInt(__bus) or  __bus == "-"):
            raise ComException( __bus + " is not valid to scan SCSI Bus"); 
    
        if  not ( ComUtils.isInt(__target) or  __target == "-"):
            raise ComException( __bus + " is not valid to scan SCSI Target")

        if  not (ComUtils.isInt(__lun) or  __lun == "-"):
            raise ComException( __bus + " is not valid to scan SCSI Lun")

        print "Hosts: ", __hosts

        for __host in __hosts:
            ComSystem.execLocal( "echo \""+__bus+"\" \""+ __target+"\" \""+ __lun+ "\" > "+__syspath+"/"+__host+"/scan")

# $Log: ComScsi.py,v $
# Revision 1.1  2006-07-19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.2  2006/06/23 11:56:52  mark
# moved Log to bottom
#
# Revision 1.1  2006/06/23 07:56:24  mark
# initial checkin (stable)
#
