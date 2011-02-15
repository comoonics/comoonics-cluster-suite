""" Comoonics storage copyset module
This module will automatically find the right storage module via the implementation attribute

Example Configuration for the HP_EVA implementation:
    <modificationset type="storage" action="add" id="basestoragesystem" implementation="hp.ComHP_EVA" system="127.0.0.1/EVA5000" username="atix" password="atix">
        <disk name="Virtual Disks/atix/sourcedisk">
            <properties>
                <property name="size" value="10"/>
                <property name="disk_group" value="146er"/>
            </properties>
        </disk>
    </modificationset>
    <copyset name="snapdisk" type="storage" action="add_snapshot" refid="basestoragesystem">
        <source type="volume"><disk name="Virtual Disks/atix/sourcedisk/ACTIVE"/></source>
        <destination type="snapshot">
            <disk name="sourcedisk_snap">
                <properties>
                    <!-- Fully or demand -->
                    <property name="ALLOCATION_POLICY" value="Fully"/>
                    <!-- vraid0, vraid1, vraid5 -->
                    <property name="Redundancy" value="VRaid0"/>
                </properties>
            </disk>
        </destination>
    </copyset>
    <modificationset type="storage" action="map_lun" refid="basestoragesystem">
        <disk name="Virtual Disks/atix/sourcedisk_snap">
            <mapping lun="0">
                <host name="server1"/>
            </mapping>
        </disk>
    </modificationset>
    <modificationset type="storage" action="delete_snapshot" refid="basestoragesystem">
        <disk name="Virtual Disks/atix/sourcedisk_snap"/>
    </modificationset>
    <copyset name="clonedisk" type="storage" action="add_clone" refid="basestoragesystem">
        <source type="volume"><disk name="Virtual Disks/atix/sourcedisk/ACTIVE"/></source>
        <destination type="snapshot">
            <disk name="sourcedisk_snap">
                <properties>
                    <!-- Fully or demand -->
                    <property name="ALLOCATION_POLICY" value="Fully"/>
                    <!-- vraid0, vraid1, vraid5 -->
                    <property name="Redundancy" value="VRaid0"/>
                    <!-- nowait -->
                    <property name="nowait"/>
                </properties>
            </disk>
        </destination>
    </copyset>
    <modificationset type="storage" action="map_lun" refid="basestoragesystem">
        <disk name="Virtual Disks/atix/sourcedisk_snap">
            <mapping lun="1">
                <host name="server1"/>
            </mapping>
        </disk>
    </modificationset>
    <modificationset type="storage" action="delete_clone" refid="basestoragesystem">
        <disk name="Virtual Disks/atix/sourcedisk_snap"/>
    </modificationset>

"""


# here is some internal information
# $Id: ComStorageCopyset.py,v 1.2 2011-02-15 14:52:47 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComStorageCopyset.py,v $

from comoonics.enterprisecopy.ComCopyset import Copyset
from comoonics.storage.ComStorage import Storage
from comoonics.enterprisecopy.ComStorageCopyobject import StorageCopyObject
from comoonics.ecbase.ComJournaled import JournaledObject
from comoonics import ComLog

class StorageCopyset(Copyset):
    """ The class for a storagecopyset. It will automatically instantiate the proper storage object and find the
    right methods to execute via the types of source and destination or the children of the disk element.
    """

    __logStrLevel__="StorageCopyset"
    def __init__(self, element, doc):
        super(StorageCopyset, self).__init__(element, doc)
        self.implementation=self.getElement().getAttribute("implementation")
        mylogger.debug("%s@%s Implementation: %s" %(self.getElement().tagName, self.getElement().getAttribute("name"), self.implementation))
        self.storage=Storage.getStorageObject(self.implementation, self.getElement())
        self.source=StorageCopyObject(element.getElementsByTagName("source")[0], doc, self.storage)
        self.destination=StorageCopyObject(element.getElementsByTagName("destination")[0], doc, self.storage)

    def doCopy(self):
        self.source.prepareAsSource()
        self.destination.prepareAsDest()
        ret=self.destination.doAction(self.getAttribute("action"), self.source)
        self.source.cleanupSource()
        self.destination.cleanupDest()

    def undoCopy(self):
        self.destination.undoRequirements()
        if isinstance(self.destination, JournaledObject):
            self.destination.replayJournal()

mylogger=ComLog.getLogger(StorageCopyset.__logStrLevel__)

########################
# $Log: ComStorageCopyset.py,v $
# Revision 1.2  2011-02-15 14:52:47  marc
# - changes for ecbase rebase to comoonics.ecbase package
#
# Revision 1.1  2010/03/08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.2  2007/03/26 08:12:56  marc
# - added support for journaling
#
# Revision 1.1  2007/02/09 11:36:16  marc
# initial revision
#
