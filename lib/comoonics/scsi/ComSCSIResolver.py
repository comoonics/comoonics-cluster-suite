"""Comoonics scsi module

Classes for resolving scsi devices by different selektors
"""


# here is some internal information
# $Id: ComSCSIResolver.py,v 1.1 2007-03-26 08:04:58 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/scsi/ComSCSIResolver.py,v $

from comoonics import ComLog
from comoonics.ComExceptions import ComException
from comoonics.ComDisk import HostDisk
from comoonics.scsi import ComSCSI

import os
import os.path
import re
from comoonics import ComSystem

log=ComLog.getLogger("ComSCSI")

class SCSIWWIDResolver(HostDisk.DeviceNameResolver):
    key="wwid"
    def resolve(self, value):
        return ComSCSI.getBlockDeviceForUID(value)

class FCTransportResolver(HostDisk.DeviceNameResolver):
    key="fctransport"
    def resolve(self, value):
        (wwwn, lun)=value.split(":")
        return ComSCSI.getBlockDeviceForWWWNLun(wwwn, lun)

def test():
    res=SCSIWWIDResolver()
    print "SCSIWWIDResolver.key: "+res.getKey()
    res=FCTransportResolver()
    print "SCSIWWIDResolver.key: "+res.getKey()

if __name__=="__main__":
    test()

###########################
# $Log: ComSCSIResolver.py,v $
# Revision 1.1  2007-03-26 08:04:58  marc
# initial revision
#
