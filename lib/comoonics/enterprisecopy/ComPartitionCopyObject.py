""" Comoonics partition copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComPartitionCopyObject.py,v 1.11 2010-04-23 10:55:27 marc Exp $
#


__version__ = "$Revision: 1.11 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComPartitionCopyObject.py,v $

import os

from ComCopyObject import CopyObjectJournaled

from comoonics.storage.ComDisk import HostDisk
from comoonics.ComExceptions import ComException
from comoonics import ComLog


class PartitionCopyObject(CopyObjectJournaled):
   __logStrLevel__="comoonics.enterprisecopy.PartitionCopyObject"
   logger=ComLog.getLogger(__logStrLevel__)

   def __init__(self, element, doc):
      CopyObjectJournaled.__init__(self, element, doc)
      try:
         __disk=element.getElementsByTagName('disk')[0]
         self.disk=HostDisk(__disk, doc)
      except Exception:
         raise ComException("disk for copyset not defined")

      self.addToUndoMap(self.disk.__class__.__name__, "savePartitionTable", "restorePartitionTable")
      self.addToUndoMap(self.disk.__class__.__name__, "noPartitionTable", "deletePartitionTable")
      # We need to have the tempfile globlally available because of it deleteing itself when not
      # referenced anymore.
      import tempfile
      self.__tmp=tempfile.NamedTemporaryFile()


   def prepareAsSource(self):
      for journal_command in self.disk.resolveDeviceName():
         self.journal(self.disk, journal_command)
      self.disk.initFromDisk()

   def prepareAsDest(self):
      for journal_command in self.disk.resolveDeviceName():
         self.journal(self.disk, journal_command)
         getattr(self.disk, journal_command)()

   def cleanupSource(self):
      self.commitJournal()

   def cleanupDest(self):
      if self.disk.hasPartitionTable():
         self.disk.savePartitionTable(self.__tmp.name)
         self.journal(self.disk, "savePartitionTable", self.__tmp.name)
      else:
         self.journal(self.disk, "noPartitionTable")

      # if disk already contians LVM configuration remove it
      pvs=list()
      from comoonics.storage.ComLVM import PhysicalVolume, LinuxVolumeManager
      try:
         pv=PhysicalVolume(self.disk.getAttribute("name"), self.getDocument())
         pv.init_from_disk()
         pvs.append(pv)
      except LinuxVolumeManager.LVMCommandException:
         try:
            for partition in self.disk.getAllPartitions():
               pv=PhysicalVolume(self.disk.getDeviceName()+self.disk.getPartitionDelim()+partition.getAttribute("name"), self.getDocument())
               pv.init_from_disk()
               pvs.append(pv)
         except LinuxVolumeManager.LVMCommandException:
            ComLog.debugTraceLog(self.logger)
      if not pvs or len(pvs)==0:
         self.log.debug("Could not find LVM physical volume on device %s. OK." %self.disk.getAttribute("name"))
      for pv in pvs:
         try:
            for lv in LinuxVolumeManager.lvlist(pv.parentvg):
               lv.remove()
            pv.parentvg.remove()
            pv.remove()
         except LinuxVolumeManager.LVMCommandException:
            ComLog.debugTraceLog(self.logger)
            self.log.info("Could not remove LVM configuration from device %s. Will continue nevertheless." %pv.getAttribute("name"))

      self.disk.createPartitions()
      self.disk.restore()

   def getMetaData(self):
      ''' returns the metadata element '''
      return self.disk.getElement()

   def updateMetaData(self, element):
      ''' updates meta data information '''
      self.disk.updateChildrenWithPK(HostDisk(element, None))
