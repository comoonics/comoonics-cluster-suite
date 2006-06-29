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
# $Id: ComLVMCopyset.py,v 1.1 2006-06-29 13:47:51 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComLVMCopyset.py,v $

from xml.dom import Element
from exceptions import IndexError
import ComCopyObject
import ComLog
from ComCopyset import Copyset
from ComDataObject import DataObject
from xml.dom.NodeFilter import NodeFilter
from ComExceptions import ComException
from ComLVMCopyObject import LVMCopyObject
from ComLVM import VolumeGroup, LinuxVolumeManager, LogicalVolume

class LVMCopyset(Copyset):
    
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
            pass
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
        Copyset.__init__(self, element, doc)
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
        for pv in LinuxVolumeManager.pvlist(self.source.getVolumeGroup(), doc):
            pv.init_from_disk()
            self.source.getVolumeGroup().addPhysicalVolume(pv)
        for lv in LinuxVolumeManager.lvlist(self.source.getVolumeGroup(), doc):
            lv.init_from_disk()
            self.source.getVolumeGroup().addLogicalVolume(lv)
        self.dest=ComCopyObject.getCopyObject(__dest, doc)
        LVMCopyset.updateFromElement(self.dest, self.source)

        
    def doCopy(self):
        # do everything
        self.prepareSource()
        self.prepareDest()
        ComLog.getLogger(self.__logStrLevel__).debug("Copying volumegroup %s => %s" % (self.source.vg.getAttribute("name"), self.dest.vg.getAttribute("name")))
        for pv in self.dest.vg.getPhysicalVolumes():
            pv.create()
        self.dest.vg.create()
        self.dest.vg.activate()
        for lv in self.dest.vg.getLogicalVolumes():
            lv.create()
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
# Revision 1.1  2006-06-29 13:47:51  marc
# initial revision
#