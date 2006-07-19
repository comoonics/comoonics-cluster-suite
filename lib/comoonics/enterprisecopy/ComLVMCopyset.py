""" Comoonics LVM copyset module

will copy a source lvm configuration defined by a source dom to a destination lvm configuration defined by a dest dom.

    <copyset type="lvm">
        <source>
            <volumegroup name="vgtest"/>
        </source>
        <destination>
              <volumegroup name="vgtest_new">
                  <physicalvolume name="/dev/sda"/>
              </volumegroup>
          </destination>
    </copyset>


"""


# here is some internal information
# $Id: ComLVMCopyset.py,v 1.1 2006-07-19 14:29:15 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComLVMCopyset.py,v $

from exceptions import IndexError
from comoonics import ComLog
from comoonics.ComLVM import VolumeGroup, LinuxVolumeManager, LogicalVolume

import ComCopyObject
from ComCopyset import CopysetJournaled
from ComLVMCopyObject import LVMCopyObject

class LVMCopyset(CopysetJournaled):
    
    def updateFromElement(edit_copyobject, source_copyobject):
        """
        Updates the whole tree from the given element
        
        edit_copyobject - is the element to copy to
        source_updatecopyobject - is the element to copy from
        """
        log=ComLog.getLogger("")
        log.debug("before updateAttributes %s, %s, attributes: %u, %u" % (edit_copyobject.getElement().tagName, source_copyobject.getElement().tagName, len(edit_copyobject.getElement().attributes), len(source_copyobject.getElement().attributes)))
        edit_copyobject.updateAttributes(source_copyobject.getElement().attributes)
        log.debug("after updateAttributes %s, %s, attributes: %u, %u" % (edit_copyobject.getElement().tagName, source_copyobject.getElement().tagName, len(edit_copyobject.getElement().attributes), len(source_copyobject.getElement().attributes)))

        if isinstance(edit_copyobject, LVMCopyObject):
            LVMCopyset.updateFromElement(edit_copyobject.getVolumeGroup(), source_copyobject.getVolumeGroup())
        elif isinstance(edit_copyobject, VolumeGroup):
            for lv in source_copyobject.getLogicalVolumes():
                if edit_copyobject.hasLogicalVolume(lv.getAttribute("name")):
                    LVMCopyset.updateFromElement(edit_copyobject.getLogicalVolume(lv.getAttribute("name")), lv)
                else:
                    edit_copyobject.addLogicalVolume(LogicalVolume(lv.getElement().cloneNode(True), edit_copyobject, edit_copyobject.getDocument()))

# We don't synchronize pvs!!!!!!!!!!!!
#            for pv in source_copyobject.getPhysicalVolumes():
#                if edit_copyobject.hasPhysicalVolume(pv.getAttribute("name")):
#                    LVMCopyset.updateFromElement(edit_copyobject.getPhysicalVolume(pv.getAttribute("name")), pv)
#                else:
#                    edit_copyobject.addPhysicalVolume(lv)
   
    updateFromElement=staticmethod(updateFromElement)
    
    __logStrLevel__ = "LVMCopyset"
    def __init__(self, element, doc):
        CopysetJournaled.__init__(self, element, doc)
        try:
            __source=self.getElement().getElementsByTagName('source')[0]
        except IndexError, ie:
            raise IndexError("Source for copyset %s not defined: %s" % (element.tagName, ie))
        try:
            __dest=self.getElement().getElementsByTagName('destination')[0]
        except IndexError, ie:
            raise IndexError("Destination for copyset %s not defined: %s" % (element.tagName, ie))
        self.source=ComCopyObject.getCopyObject(__source, doc)
        self.source.getVolumeGroup().init_from_disk()
        self.addToUndoMap(self.source.getVolumeGroup().__class__.__name__, "create", "remove")
        self.addToUndoMap(self.source.getVolumeGroup().__class__.__name__, "activate", "deactivate")
        for pv in LinuxVolumeManager.pvlist(self.source.getVolumeGroup(), doc):
            pv.init_from_disk()
            self.source.getVolumeGroup().addPhysicalVolume(pv)
            self.addToUndoMap(pv.__class__.__name__,"create", "remove")
        for lv in LinuxVolumeManager.lvlist(self.source.getVolumeGroup(), doc):
            lv.init_from_disk()
            self.source.getVolumeGroup().addLogicalVolume(lv)
            self.addToUndoMap(lv.__class__.__name__,"create", "remove")
        self.dest=ComCopyObject.getCopyObject(__dest, doc)
        LVMCopyset.updateFromElement(self.dest, self.source)
        
    def doCopy(self):
        # do everything
        self.prepareSource()
        self.prepareDest()
        ComLog.getLogger(self.__logStrLevel__).debug("Copying volumegroup %s => %s" % (self.source.vg.getAttribute("name"), self.dest.vg.getAttribute("name")))
        for pv in self.dest.vg.getPhysicalVolumes():
            try:
                pv.create()
                self.journal(pv, "create")
            except LinuxVolumeManager.LVMAlreadyExistsException, e:
                ComLog.getLogger(self.__logStrLevel__).debug("Skipping creating of %s %s as it already exists" % (pv.__class__.__name__, pv.getAttribute("name")))

        try:
            self.dest.vg.create()
            self.journal(self.dest.vg, "create")
        except LinuxVolumeManager.LVMAlreadyExistsException, e:
            ComLog.getLogger(self.__logStrLevel__).debug("Skipping creating of %s %s as it already exists" % (self.dest.vg.__class__.__name__, self.dest.vg.getAttribute("name")))
        self.dest.vg.activate()
        self.journal(self.dest.vg, "activate")
        for lv in self.dest.vg.getLogicalVolumes():
            try:
                lv.create()
                self.journal(lv, "create")
            except LinuxVolumeManager.LVMAlreadyExistsException, e:
                ComLog.getLogger(self.__logStrLevel__).debug("Skipping creating of %s %s as it already exists" % (lv.__class__.__name__, lv.getAttribute("name")))

        self.postSource()
        self.postDest()
    
    def prepareSource(self):
        #do things like fsck, mount
        # scan for fsconfig
        self.source.prepareAsSource()
    
    def postSource(self):
        self.source.cleanupSource()
    
    def postDest(self):
        self.dest.cleanupDest()
    
    def prepareDest(self):
        # do things like mkfs, mount
        self.dest.prepareAsDest()

########################
# $Log: ComLVMCopyset.py,v $
# Revision 1.1  2006-07-19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.5  2006/07/03 16:10:44  marc
# removed a weired pass
#
# Revision 1.4  2006/07/03 12:53:42  marc
# changed error detection
#
# Revision 1.3  2006/06/30 13:58:13  marc
# removed dummyexception
#
# Revision 1.2  2006/06/30 08:28:45  marc
# added journal functionality
#
# Revision 1.1  2006/06/29 13:47:51  marc
# initial revision
#