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

    def doPost(self):
        """
        Does something afterwards
        """
        self._do()

######################
# $Log: ComSCSIRequirement.py,v $
# Revision 1.2  2010-03-08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.1  2007/03/26 08:04:48  marc
# initial revision
#
# Revision 1.5  2007/02/28 10:11:42  mark
# added mkdir support
#
# Revision 1.4  2006/08/02 13:55:29  marc
# added bak_suffix attribute
#
# Revision 1.3  2006/07/24 14:48:42  marc
# check is not required
#
# Revision 1.2  2006/07/24 09:58:30  marc
# support for check tag in requirement
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.5  2006/07/04 11:00:17  marc
# changed bug in cleanup
#
# Revision 1.4  2006/07/03 16:08:58  marc
# removing the unpacked archive afterwards
#
# Revision 1.3  2006/06/30 08:30:20  marc
# added logging
#
# Revision 1.2  2006/06/29 13:43:50  marc
# first version
#
# Revision 1.1  2006/06/29 13:38:06  marc
# initial revision
#
