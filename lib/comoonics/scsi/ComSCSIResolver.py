"""Comoonics scsi module

Classes for resolving scsi devices by different selektors
"""


# here is some internal information
# $Id: ComSCSIResolver.py,v 1.4 2010-03-08 12:30:48 marc Exp $
#


__version__ = "$Revision: 1.4 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/scsi/ComSCSIResolver.py,v $

from comoonics import ComLog
from comoonics.storage.ComDisk import HostDisk
from comoonics.scsi import ComSCSI

log=ComLog.getLogger("comoonics.scsi.ComSCSI")

class SCSIWWIDResolver(HostDisk.DeviceNameResolver):
    key="wwid"
    def resolve(self, value):
        return ComSCSI.getBlockDeviceForUID(value)

class FCTransportResolver(HostDisk.DeviceNameResolver):
    key="fctransport"
    def resolve(self, value):
        if len(value.split(":"))==2:
            (wwwn, lun)=value.split(":")
            return ComSCSI.getBlockDeviceForWWWNLun(wwwn, lun)
        else:
            (wwwn, lun, other)=value.split(":")
            return "%s%s" %(ComSCSI.getBlockDeviceForWWWNLun(wwwn, lun), other)

###########################
# $Log: ComSCSIResolver.py,v $
# Revision 1.4  2010-03-08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.3  2007/07/25 11:35:13  marc
# - loglevel
#
# Revision 1.2  2007/04/04 12:33:58  marc
# MMG Backup Legato Integration :
# - short "hack" for partitions
#
# Revision 1.1  2007/03/26 08:04:58  marc
# initial revision
#
