""" Comoonics filesystem copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFilesystemCopyObject.py,v 1.14 2011-02-21 16:23:53 marc Exp $
#


__version__ = "$Revision: 1.14 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComFilesystemCopyObject.py,v $

from comoonics.storage.ComDevice import Device
from comoonics.storage import ComFileSystem
from comoonics.storage.ComMountpoint import MountPoint
from ComCopyObject import CopyObjectJournaled
from comoonics.ComExceptions import ComException
from comoonics import ComLog

class FilesystemCopyObject(CopyObjectJournaled):
   __logStrLevel__="FilesystemCopyObject"
   log=ComLog.getLogger(__logStrLevel__)

   # Base Class for all source and destination objects"""
   def __init__(self, element, doc):
      CopyObjectJournaled.__init__(self, element, doc)
      __device=None
      try:
         __device=element.getElementsByTagName("device")[0]
         self.device=Device(__device, doc)
      except Exception, e:
         ComLog.debugTraceLog(self.log)
         raise ComException("device for copyset not defined (%s)" %(e))
      try:
         __fs=__device.getElementsByTagName("filesystem")[0]
         self.filesystem=ComFileSystem.getFileSystem(__fs, doc)
      except Exception, e:
         ComLog.debugTraceLog(self.log)
         raise ComException("filesystem for copyset not defined. Error: %s" %e)
      try:
         __mp=__device.getElementsByTagName("mountpoint")[0]
         self.mountpoint=MountPoint(__mp, doc)
      except Exception:
         raise ComException("mountpoint for copyset not defined")
      FilesystemCopyObject.log.debug("__init__: fs: %s, device: %s" %(__device, __fs))
      self.umountfs=False
      self.addToUndoMap(self.filesystem.__class__.__name__, "mount", "umountDir")
      self.addToUndoMap(self.device.__class__.__name__, "lvm_vg_activate", "lvm_vg_deactivate")

   def getFileSystem(self):
      return self.filesystem

   def getDevice(self):
      return self.device

   def getMountpoint(self):
      return self.mountpoint

   def setFileSystem(self, filesystem):
      self.setFileSystemElement(filesystem.getElement())

   def setFileSystemElement(self, element):
      __parent=self.filesystem.getElement().parentNode
      __newnode=element.cloneNode(True)
      __oldnode=self.filesystem.getElement()
      self.filesystem.setElement(__newnode)
      # only replace attributes
      try:
         __parent.replaceChild(__newnode, __oldnode)
      except Exception, e:
         ComLog.getLogger(FilesystemCopyObject.__logStrLevel__).warning(e)

   def prepareAsSource(self):
      # Check for mounted
      FilesystemCopyObject.log.debug("prepareAsSource: Name %s options: %s" %(self.device.getAttribute("name"), self.device.getAttribute("options", "")))
      for journal_command in self.device.resolveDeviceName():
         self.journal(self.device, journal_command)
      options=self.device.getAttribute("options", "")
      options=options.split(",")
      if options and "fsck" in options and not self.device.isMounted(self.mountpoint):
         self.filesystem.checkFs(self.device)
      if not self.filesystem.isCopyable():
         FilesystemCopyObject.log.debug("prepareAsSource: skipping mount not copyable")
      elif options and "skipmount" in options:
         FilesystemCopyObject.log.debug("prepareAsSource: skipping mount because specified")
      else:
         if not self.device.isMounted(self.mountpoint):
#            FilesystemCopyObject.log.debug("prepareAsSource: mounting %s, %s" %(self.device, self.mountpoint))
            self.filesystem.mount(self.device, self.mountpoint)
            self.journal(self.filesystem, "mount", [self.mountpoint])
         else:
            FilesystemCopyObject.log.debug("prepareAsSource: device is mounted, skipping")
         #self.umountfs=True
      # scan filesystem options
      self.filesystem.scanOptions(self.device, self.mountpoint)

   def prepareAsDest(self):
      # - mkfs
      # TODO add some intelligent checks
      FilesystemCopyObject.log.debug("prepareAsDest: Name %s options: %s" %(self, self.device.getAttribute("options", "")))
      for journal_command in self.device.resolveDeviceName():
         self.journal(self.device, journal_command)
#      if self.device.getAttribute("options", "") != "skipactivate" and not self.device.is_lvm_activated():
#         self.device.lvm_vg_activate()
#         self.journal(self.device, "lvm_vg_activate")
      self.filesystem.formatDevice(self.device)
      self.filesystem.mount(self.device, self.mountpoint)
      if self.filesystem.hasAttribute("label"):
         self.filesystem.labelDevice(self.device, self.filesystem.getLabel(self.device))
      if self.filesystem.needsNoMountpoint():
         self.journal(self.filesystem, "mount", [self.device])
      else:
         self.journal(self.filesystem, "mount", [self.mountpoint])

   def cleanupSource(self):
      self.log.debug("cleanupSource()")
      self.replayJournal()
      self.commitJournal()
      #if self.umountfs:
      #   self.filesystem.umountDir(self.mountpoint)
      #   self.umountfs=False

   def cleanupDest(self):
      self.log.debug("cleanupDest()")
      #self.filesystem.umountDir(self.mountpoint)
      self.replayJournal()
      self.commitJournal()

   def getMetaData(self):
      ''' returns the metadata element '''
      return self.device.getElement()


   def updateMetaData(self, element):
      """ copy all Attributes from source to dest that are not defined
      in dest
      """
      from comoonics import XmlTools
      sfilesystems=element.getElementsByTagName(ComFileSystem.FileSystem.TAGNAME)
      if sfilesystems and len(sfilesystems)==1:
         dfilesystem=self.getFileSystem().getElement()
         for index in range(0, sfilesystems[0].attributes.length):
            attribute=sfilesystems[0].attributes.item(index)
            if not dfilesystem.hasAttribute(attribute.name):
               dfilesystem.setAttribute(attribute.name, attribute.value)
      smountpoint=element.getElementsByTagName(MountPoint.TAGNAME)
      if smountpoint and len(smountpoint)==1:
         XmlTools.merge_trees_with_pk(smountpoint[0], self.getMountpoint().getElement(), self.getDocument())
