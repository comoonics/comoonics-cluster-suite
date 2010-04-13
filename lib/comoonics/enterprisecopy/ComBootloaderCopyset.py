""" Comoonics bootloader copyset module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComBootloaderCopyset.py,v 1.5 2010-04-13 13:25:06 marc Exp $
#


__version__ = "$Revision: 1.5 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComBootloaderCopyset.py,v $


from ComCopyset import Copyset
from comoonics.storage.ComBootDisk import BootDisk
from comoonics.ComExceptions import ComException

class BootloaderCopyset(Copyset):
    def __init__(self, element, doc):
        Copyset.__init__(self, element, doc)

        try:
            _dest=element.getElementsByTagName("destination")[0]
            __dest=element.getElementsByTagName("disk")[0]
            self.destination=BootDisk(__dest, doc)
        except Exception:
            raise ComException("destination for copyset not defined")

    def doCopy(self):
        self.destination.resolveDeviceName()
        self.destination.installBootloader()


# $Log: ComBootloaderCopyset.py,v $
# Revision 1.5  2010-04-13 13:25:06  marc
# - removed a xpath dep
#
# Revision 1.4  2010/03/08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.3  2010/02/10 12:48:46  mark
# added .storage path in includes
#
# Revision 1.2  2007/06/19 12:51:15  marc
# - Compatibility with resolvable Devicenames introduced.
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.1  2006/06/28 17:25:16  mark
# initial checkin (stable)
#