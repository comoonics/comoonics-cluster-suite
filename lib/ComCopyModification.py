""" Comoonics modification module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComCopyModification.py,v 1.2 2006-07-07 11:35:36 mark Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComCopyModification.py,v $

import exceptions
import xml.dom
from xml import xpath

from ComFileModification import FileModification
from ComFile import File
import ComSystem
import ComLog

class CopyModification(FileModification):
    """ Base Class for all source and destination objects"""
    def __init__(self, element, doc):
        FileModification.__init__(self, element, doc)
    
    def doModifications(self, file):
        # TODO create bckup of file ?
        # TODO raise Warning Exception
        __cmd = "cp -a "
        __cmd += file.getAttribute("sourcefile")
        __cmd += " "
        __cmd += file.getAttribute("name")
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        if __rc:
            ComLog.getLogger("CopyModification").error("doCopy: " + __cmd + " " + __ret)
        else:
            ComLog.getLogger("CopyModification").debug("doCopy: "  + __cmd +" "+ __ret) 


# $Log: ComCopyModification.py,v $
# Revision 1.2  2006-07-07 11:35:36  mark
# changed to inherit FileModification
#
# Revision 1.1  2006/06/30 07:56:12  mark
# initial revision
#
