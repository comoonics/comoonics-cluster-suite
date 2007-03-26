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
# $Id: ComStorageModificationset.py,v 1.2 2007-03-26 08:14:38 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/Attic/ComStorageModificationset.py,v $

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

def main():
    import sys
    cwd=sys.argv[0]
    cwd=cwd[:cwd.rfind("/")]
    xml_dumps=["""
    <modificationset type="storage" action="add" id="basestoragesystem" implementation="comoonics.storage.hp.ComHP_EVA_Storage" system="127.0.0.1/EVA5000" username="Administrator" password="Administrator" cmd="%s/hp/ComHP_EVA_SSSU_Sim.py">
        <disk name="Virtual Disks/atix/sourcedisk">
            <properties>
                <property name="size" value="10"/>
                <property name="disk_group" value="146er"/>
            </properties>
        </disk>
    </modificationset>
""" %(cwd),
"""
    <modificationset type="storage" action="map_luns" id="basestoragesystem" implementation="comoonics.storage.hp.ComHP_EVA_Storage" system="127.0.0.1/EVA5000" username="Administrator" password="Administrator" cmd="%s/hp/ComHP_EVA_SSSU_Sim.py">
        <disk name="Virtual Disks/atix/sourcedisk">
            <mapping lun="0">
                <host name="server1"/>
            </mapping>
        </disk>
    </modificationset>""" %(cwd)]
    for xml_dump in xml_dumps:
        testModificationsetFromXMLDump(xml_dump)

def testModificationsetFromXMLDump(xml_dump):
    from xml.dom.ext.reader import Sax2
    from comoonics.ComDisk import Disk
    reader=Sax2.Reader(validate=0)
    #mylogger.debug("xml: %s" %(match.group(1)))
    doc=reader.fromString(xml_dump)
    sms=StorageModificationset(doc.documentElement, doc)
    sms.doModifications()

if __name__ == '__main__':
    main()

# $Log: ComStorageModificationset.py,v $
# Revision 1.2  2007-03-26 08:14:38  marc
# - added support for undoing and journaling
#
# Revision 1.1  2007/02/09 11:36:16  marc
# initial revision
#
