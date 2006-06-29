""" Comoonics Requirement class


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id: ComArchiveRequirement.py,v 1.2 2006-06-29 13:43:50 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComArchiveRequirement.py,v $

from ComExceptions import ComException
from ComRequirement import Requirement
import os
import ComSystem

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
    
    def doPre(self):
        """
        Unpacks the given file to dest
        """
        srcfile=self.getAttribute("name")
        destfile=self.getAttribute("dest")
        
        if not os.access(srcfile, os.R_OK) or not os.access(destfile, os.F_OK) or not os.access(destfile, os.W_OK):
            raise ArchiveRequirementException("Either srcfile %s is not readable or dest %s is not writeable" % (srcfile, destfile))
        os.chdir(destfile)
        __cmd="gzip -cd %s | cpio -i" % srcfile
        (rc, rv) = ComSystem.execLocalGetResult(__cmd)
        if rc >> 8 != 0:
            raise RuntimeError("running \"%s\" failed: %u, %s" % (__cmd, rc,rv))

    
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
        
        if not os.access(srcfile, os.R_OK) or not os.access(destfile, os.F_OK) or not os.access(destfile, os.W_OK):
            raise ArchiveRequirementException("Either srcfile %s is not readable or dest %s is not writeable" % (srcfile, destfile))
        os.chdir(destfile)
        __cmd="cp %s %s" %(srcfile, srcfile+".bak")
        (rc, rv) = ComSystem.execLocalGetResult(__cmd)
        if rc >> 8 != 0:
            raise RuntimeError("running \"%s\" failed: %u, %s" % (__cmd, rc,rv))

        __cmd="find . | cpio -o -c |gzip -9 > %s" % (srcfile, destfile)
        (rc, rv) = ComSystem.execLocalGetResult(__cmd)
        if rc >> 8 != 0:
            raise RuntimeError("running \"%s\" failed: %u, %s" % (__cmd, rc,rv))

######################
# $Log: ComArchiveRequirement.py,v $
# Revision 1.2  2006-06-29 13:43:50  marc
# first version
#
# Revision 1.1  2006/06/29 13:38:06  marc
# initial revision
#
