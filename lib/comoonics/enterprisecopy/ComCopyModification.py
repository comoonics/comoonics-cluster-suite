""" Comoonics modification module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComCopyModification.py,v 1.3 2010-03-08 12:30:48 marc Exp $
#


__version__ = "$Revision: 1.3 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComCopyModification.py,v $

from ComFileModification import FileModification
from comoonics import ComSystem
from comoonics import ComLog

class CopyModification(FileModification):
    """ Base Class for all source and destination objects"""
    def __init__(self, element, doc):
        FileModification.__init__(self, element, doc)
    
    def doModifications(self, file):
        # TODO create bckup of file ?
        # TODO raise Warning Exception
        cmd = "cp -a "
        cmd += file.getAttribute("sourcefile")
        cmd += " "
        cmd += file.getAttribute("name")
        rc, ret = ComSystem.execLocalStatusOutput(cmd)
        if rc:
            ComLog.getLogger("CopyModification").error("doCopy: " + cmd + " " + ret)
        else:
            ComLog.getLogger("CopyModification").debug("doCopy: "  + cmd +" "+ ret)


# $Log: ComCopyModification.py,v $
# Revision 1.3  2010-03-08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.2  2010/02/09 21:48:24  mark
# added .storage path in includes
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.2  2006/07/07 11:35:36  mark
# changed to inherit FileModification
#
# Revision 1.1  2006/06/30 07:56:12  mark
# initial revision
#
