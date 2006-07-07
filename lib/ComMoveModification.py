""" Comoonics modification module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComMoveModification.py,v 1.1 2006-07-07 11:34:23 mark Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComMoveModification.py,v $

import exceptions
import xml.dom
from xml import xpath

from ComFileModification import FileModification
from ComFile import File
import ComSystem
import ComLog

class MoveModification(FileModification):
    """ Base Class for all source and destination objects"""
    def __init__(self, element, doc):
        FileModification.__init__(self, element, doc)
    
    def doModifications(self, file):
        # TODO create bckup of file ?
        # TODO raise Warning Exception
        __cmd = "mv -f "
        __cmd += file.getAttribute("sourcefile")
        __cmd += " "
        __cmd += file.getAttribute("name")
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        if __rc:
            ComLog.getLogger("MoveModification").error("doMove: " + __cmd + " " + __ret)
        else:
            ComLog.getLogger("MoveModification").debug("doMove: "  + __cmd +" "+ __ret) 


# $Log: ComMoveModification.py,v $
# Revision 1.1  2006-07-07 11:34:23  mark
# initial revision
#
# Revision 1.1  2006/06/30 07:56:12  mark
# initial revision
#
