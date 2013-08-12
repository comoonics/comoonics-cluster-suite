""" Comoonics Archive copy object module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComArchiveCopyObject.py,v 1.12 2011-02-15 14:52:47 marc Exp $
#


__version__ = "$Revision: 1.12 $"

from comoonics import ComLog, ComSystem
from ComCopyObject import CopyObjectJournaled
from comoonics.ComExceptions import ComException
from comoonics.ecbase.ComMetadataSerializer import getMetadataSerializer
from comoonics.storage.ComArchive import Archive

class ArchiveCopyObject(CopyObjectJournaled):
   """ Class for all source and destination objects"""
   __logStrLevel__ = "ArchiveCopyObject"
   log=ComLog.getLogger(__logStrLevel__)

   def __init__(self, element, doc):
      CopyObjectJournaled.__init__(self, element, doc)
      _metadata=self.element.getElementsByTagName("metadata")
      if len(_metadata)>0:
         __serializer=_metadata[0]
         self.serializer=getMetadataSerializer(__serializer, doc)
      else:
         self.log.warn("ArchivCopyObject %s has no metadata defined!" %self.getAttribute("name", "unknown"))


   def prepareAsSource(self):
      if hasattr(self, "serializer"):
         self.metadata=self.serializer.resolve()
      else:
         self.metadata=None

   def cleanupSource(self):
      pass

   def getMetaData(self):
      ''' returns a list of metadata elements '''
      return self.metadata

   def updateMetaData(self, element):
      ''' updates all meta data information '''
      self.metadata=element

   def getDataArchive(self):
      ''' returns data archive object'''
      import comoonics.XmlTools
      try:
         __archive=comoonics.XmlTools.evaluateXPath('data/archive', self.element)[0]
         return Archive(__archive, self.document)
      except Exception:
         raise ComException("no data archiv description found")


   def prepareAsDest(self):
      ''' writes all metadata to archive'''
      self.log.debug("prepareAsDest()")
      ComSystem.execMethod(self.serializer.serialize, self.metadata)

   def cleanupDest(self):
      pass

