""" Comoonics SCSIRescanRequirement class


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id: ComSCSIRequirement.py,v 1.2 2010-03-08 12:30:48 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComSCSIRequirement.py,v $

from comoonics.ComExceptions import ComException
from ComRequirement import Requirement
from comoonics import ComLog
from comoonics import ComSystem

class SCSIRequirementException(ComException): pass

class SCSIRequirement(Requirement):
   """
   Requirement Class for handling scsirescans. The attribute format defines the type of rescan
   either fc for rescanning all fcadapters or scsi for rescanning all scsiadapters including fcadapters.
   name must be the function until now only rescan is supported.

   A xml document fragment for a archive requirement could look as follows:

      <device refid="bootfs">
         <modification type="copy">
            <requirement type="scsi" format="fc" name="rescan" dest="host1"/>
            <file name="etc/cluster.conf" sourcefile="/etc/copysets/lilr10023/cluster.conf"/>
         </modification>
      </device>

   """

   # Static methods and objects/attributes
   __logStrLevel__ = "SCSIRequirement"
   log=ComLog.getLogger(__logStrLevel__)

   # Public methods

   def __init__(self, element, doc):
      """
      Creates a new requirement instance
      """
      Requirement.__init__(self, element, doc)
      if not self.hasAttribute("format"):
         raise SCSIRequirementException("Format has to be defined for %s" % self.__class__.__name__)
      self.format=self.getAttribute("format")
      self.name=self.getAttribute("name")
      self.dest=None
      if self.hasAttribute("dest"):
         self.dest=self.getAttribute("dest")

   def check(self):
      """
      Returns true if checks have to be performed
      """
      return not self.hasAttribute("check") or not self.getAttribute("check") == "no"

   def doPre(self):
      """
      Unpacks the given file to dest
      """
      self._do()

   def _do(self):
      """
      If need be does something
      """
      from comoonics.scsi import ComSCSI
      if self.name == "rescan":
         ComSCSI.rescan(self.dest)
      elif self.name == "rescan_qla":
         ComSCSI.rescan_qla(self.dest)
      else:
         raise SCSIRequirementException("Unsupported SCSI Rescan name %s", self.name)
      #stabilized.stabilized(file="/proc/partitions", iterations=10, type="hash")
      ComSystem.execLocalOutput("udevsettle")

   def doPost(self):
      """
      Does something afterwards
      """
      self._do()
