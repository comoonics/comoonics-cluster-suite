""" Comoonics copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComLVMCopyObject.py,v 1.9 2010-03-08 12:30:48 marc Exp $
#


__version__ = "$Revision: 1.9 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComLVMCopyObject.py,v $

from ComCopyObject import CopyObject
from comoonics.storage.ComLVM import VolumeGroup, LinuxVolumeManager
from comoonics import ComLog
from comoonics import XmlTools

class LVMCopyObject(CopyObject):
   """ Class for all LVM source and destination objects"""
   __logStrLevel__ = "LVMCopyObject"

   def __init__(self, element, doc):
      CopyObject.__init__(self, element, doc)
      self.vg=None
      vg_element = element.getElementsByTagName(VolumeGroup.TAGNAME)[0]
      self.vg=VolumeGroup(vg_element, doc)
      self.sactivated=False
      self.dactivated=False

   def prepareAsSource(self):
      self.getVolumeGroup().init_from_disk()
      for pv in LinuxVolumeManager.pvlist(self.getVolumeGroup(), self.getDocument()):
         pv.init_from_disk()
         self.getVolumeGroup().addPhysicalVolume(pv)
      for lv in LinuxVolumeManager.lvlist(self.getVolumeGroup(), self.getDocument()):
         lv.init_from_disk()
         self.getVolumeGroup().addLogicalVolume(lv)
         if not lv.isActivated() and not self.sactivated:
            if lv.getAttribute("attrs", "") != "": 
               self.sactivated=True
            self.vg.activate()

   def prepareAsDest(self):
      self.dactivated=True
      for pv in self.getVolumeGroup().getPhysicalVolumes():
         self.getVolumeGroup().delPhysicalVolume(pv)
         pv.resolveName()
         self.getVolumeGroup().addPhysicalVolume(pv)

   def updateMetaData(self, element):
      ComLog.getLogger(self.__logStrLevel__).debug("%u logical volumes cloning all from source" %(len(self.getVolumeGroup().getLogicalVolumes())))
      #ComLog.getLogger(self.__logStrLevel__).debug("Element to copy %s" %(element))
      if (len(self.getVolumeGroup().getLogicalVolumes()) == 0):
         #ComLog.getLogger(self.__logStrLevel__).debug("0 logical volumes cloning all from source")
         XmlTools.merge_trees_with_pk(element, self.getVolumeGroup().getElement(), self.document, "name", XmlTools.ElementFilter("logicalvolume"))
         self.vg=VolumeGroup(self.getVolumeGroup().getElement(), self.getDocument())
         #self.getVolumeGroup().updateChildrenWithPK(element)
         #from xml.dom.ext import PrettyPrint
         #PrettyPrint(self.getVolumeGroup().getElement())
         #ComLog.getLogger(self.__logStrLevel__).debug("Successfully updated the dom structure for volumegroup")

   def cleanupSource(self):
      if self.sactivated:
         self.vg.deactivate()

   def cleanupDest(self):
      if self.dactivated:
         self.vg.deactivate()

   def getVolumeGroup(self):
      return self.vg

   def getMetaData(self):
      return self.vg.getElement()
