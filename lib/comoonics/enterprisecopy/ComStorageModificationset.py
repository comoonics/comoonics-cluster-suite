"""
Comoonics storage copyset module
This module will automatically find the right storage module via the implementation attribute

Example Configuration for the HP_EVA implementation:
    <modificationset type="storage" action="add" id="basestoragesystem" implementation="comoonics.storage.hp.ComHP_EVA_Storage" system="127.0.0.1/EVA5000" username="atix" password="atix">
        <disk name="Virtual Disks/atix/sourcedisk">
            <properties>
                <property name="size" value="10"/>
                <property name="disk_group" value="146er"/>
            </properties>
        </disk>
    </modificationset>
    <modificationset type="storage" action="map_lun" refid="basestoragesystem">
        <disk name="Virtual Disks/atix/sourcedisk_snap">
            <mapping lun="0">
                <host name="server1"/>
            </mapping>
        </disk>
    </modificationset>
    <modificationset type="storage" action="delete_snap" refid="basestoragesystem">
        <disk name="Virtual Disks/atix/sourcedisk_snap"/>
    </modificationset>
"""

# here is some internal information
# $Id: ComStorageModificationset.py,v 1.1 2010-03-08 12:30:48 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComStorageModificationset.py,v $

from comoonics.enterprisecopy.ComModificationset import Modificationset
from comoonics.storage.ComStorage import Storage
from comoonics import ComLog

class StorageModificationset(Modificationset):
    """ implementation for the Modificationset of a storage system. """
    __logStrLevel__="StorageModificationset"
    def __init__(self, element, doc):
        super(StorageModificationset, self).__init__(element, doc)
        self.implementation=self.getAttribute("implementation")
        self.action=self.getAttribute("action")
        self.storage=Storage.getStorageObject(self.implementation, self.getElement())
        self.createModificationsList(self.getElement().getElementsByTagName("disk"), doc, storage=self.storage, action=self.action, type=self.getAttribute("type"))
        for modification in self.getModifications():
            modification.storage=self.storage

    def doPre(self):
        """ connects to the storage system """
        super(StorageModificationset, self).doPre()
        self.storage.connect()

    def doPost(self):
        """ disconnects from the storage system """
        super(StorageModificationset, self).doPost()
        self.storage.close()

mylogger=ComLog.getLogger(StorageModificationset.__logStrLevel__)

# $Log: ComStorageModificationset.py,v $
# Revision 1.1  2010-03-08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.2  2007/03/26 08:14:38  marc
# - added support for undoing and journaling
#
# Revision 1.1  2007/02/09 11:36:16  marc
# initial revision
#
