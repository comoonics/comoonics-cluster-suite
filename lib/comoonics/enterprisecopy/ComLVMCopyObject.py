""" Comoonics copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComLVMCopyObject.py,v 1.2 2006-11-23 14:16:16 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComLVMCopyObject.py,v $

from ComCopyObject import CopyObject
from comoonics.ComDataObject import DataObject
from comoonics.ComLVM import VolumeGroup

class LVMCopyObject(CopyObject):
    """ Class for all LVM source and destination objects"""
    __logStrLevel__ = "LVMCopyObject"

    def __init__(self, element, doc):
        CopyObject.__init__(self, element, doc)
        self.vg=None
        vg_element = element.getElementsByTagName(VolumeGroup.TAGNAME)[0]
        self.vg=VolumeGroup(vg_element, doc)

    def prepareAsSource(self):
        self.vg.activate()

    def cleanupSource(self):
        pass
#        self.vg.deactivate()

    def cleanupDest(self):
        self.cleanupSource()

    def prepareAsDest(self):
        pass

    def getVolumeGroup(self):
        return self.vg

#################
# $Log: ComLVMCopyObject.py,v $
# Revision 1.2  2006-11-23 14:16:16  marc
# added logStrLevel
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.1  2006/06/29 13:47:39  marc
# initial revision
#