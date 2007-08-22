""" Comoonics Requirement class


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id: ComArchiveRequirement.py,v 1.7 2007-08-22 16:25:46 marc Exp $
#


__version__ = "$Revision: 1.7 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComArchiveRequirement.py,v $

from comoonics.ComExceptions import ComException
from ComRequirement import Requirement
import os
from comoonics import ComSystem
from comoonics import ComLog

class ArchiveRequirementException(ComException): pass

class ArchiveRequirement(Requirement):
    """
    Requirement Class for handling archive files. The attribute format defines the type of archive. Until now only
    "cpio" is supported as type.

    A xml document fragment for a archive requirement could look as follows:

        <device refid="bootfs">
            <modification type="copy">
                <requirement type="archive" format="cpio" name="/initrd_sr-2.6.9-34.0.1.ELsmp.img" dest="/tmp/test"/>
                <file name="etc/cluster.conf" sourcefile="/etc/copysets/lilr10023/cluster.conf"/>
            </modification>
        </device>

    """

    """
    Static methods and objects/attributes
    """
    __logStrLevel__ = "ArchiveRequirement"

    """
    Public methods
    """

    def __init__(self, element, doc):
        """
        Creates a new requirement instance
        """
        Requirement.__init__(self, element, doc)
        if not self.hasAttribute("format"):
            raise ArchiveRequirementException("Format has to be defined for %s" % self.__class__.__name__)
        if not self.getAttribute("format") == "cpio":
            raise ArchiveRequirementException("Format %s is not implemented for %s" % (self.getAttribute("format"), self.__class__.__name__  ))
        if not self.hasAttribute("name") or not self.hasAttribute("dest"):
            raise ArchiveRequirementException("Either name or destination not defined in element")
        self.order=Requirement.BOTH

    def check(self):
        """
        Returns true if checks have to be performed
        """
        return not self.hasAttribute("check") or not self.getAttribute("check") == "no"

    def doPre(self):
        """
        Unpacks the given file to dest
        """
        srcfile=self.getAttribute("name")
        destfile=self.getAttribute("dest")
        __mkdir=self.getAttributeBoolean("mkdir", default=True)

        if not os.path.exists(destfile) and __mkdir:
            ComLog.getLogger(ArchiveRequirement.__logStrLevel__).debug("Path %s does not exists. I'll create it." % destfile)
            os.makedirs(destfile)

        if self.check():
            if not os.access(srcfile, os.R_OK) or not os.access(destfile, os.F_OK) or not os.access(destfile, os.W_OK):
                raise ArchiveRequirementException("Either srcfile %s is not readable or dest %s is not writeable" % (srcfile, destfile))

        __cmd="rm -rf %s/*" % destfile
        (rc, rv) = ComSystem.execLocalGetResult(__cmd)
        if rc >> 8 != 0:
            raise RuntimeError("running \"%s\" failed: %u, %s" % (__cmd, rc,rv))

        self.olddir=os.curdir
        os.chdir(destfile)
        __cmd="gzip -cd %s | cpio -i" % srcfile
        (rc, rv, stderr) = ComSystem.execLocalGetResult(__cmd, True)
        if rc >> 8 != 0:
            raise RuntimeError("running \"%s\" failed: %u, %s, %s" % (__cmd, rc,rv, stderr))


    def do(self):
        """
        If need be does something
        """
        pass

    def doPost(self):
        """
        Does something afterwards
        """
        srcfile=self.getAttribute("name")
        destfile=self.getAttribute("dest")

        if self.check():
            if not os.access(srcfile, os.R_OK) or not os.access(destfile, os.F_OK) or not os.access(destfile, os.W_OK):
                raise ArchiveRequirementException("Either srcfile %s is not readable or dest %s is not writeable" % (srcfile, destfile))
        os.chdir(destfile)
        __cmd="cp %s %s" %(srcfile, srcfile+self.getAttribute("bak_suffix", ".bak"))
        try:
            (rc, rv, stderr) = ComSystem.execLocalGetResult(__cmd, True)
            if rc >> 8 != 0:
                raise RuntimeError("running \"%s\" failed: %u, %s, errors: %s" % (__cmd, rc,rv, stderr))
        except RuntimeError, re:
            ComLog.getLogger(ArchiveRequirement.__logStrLevel__).warn("Cannot backup sourcefile %s=%s, %s." %(srcfile, srcfile+".bak", re))

        __cmd="find . | cpio -o -c |gzip -9 > %s" % (srcfile)
        (rc, rv, stderr) = ComSystem.execLocalGetResult(__cmd, True)
        os.chdir(self.olddir)
        if rc >> 8 != 0:
            raise RuntimeError("running \"%s\" failed: %u, %s, errors: %s" % (__cmd, rc,rv, stderr))
        __cmd="rm -rf %s/*" % destfile
        (rc, rv) = ComSystem.execLocalGetResult(__cmd)
        if rc >> 8 != 0:
            raise RuntimeError("running \"%s\" failed: %u, %s" % (__cmd, rc,rv))

######################
# $Log: ComArchiveRequirement.py,v $
# Revision 1.7  2007-08-22 16:25:46  marc
# Fixed Bug BZ#86 (cpio does not work if tmp dir has files)
#
# Revision 1.6  2007/04/10 16:51:24  marc
# changed to order.BOTH
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
