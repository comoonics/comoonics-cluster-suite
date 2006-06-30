""" Comoonics modification module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComCopyModification.py,v 1.1 2006-06-30 07:56:12 mark Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComCopyModification.py,v $

import exceptions
import xml.dom
from xml import xpath

from ComModification import Modification
from ComFile import File
import ComSystem
import ComLog

class CopyModification(Modification):
    """ Base Class for all source and destination objects"""
    def __init__(self, element, doc):
        Modification.__init__(self, element, doc)
        self.files=self.createFileList(element, doc)
        
    def doRealModifications(self):
        for i in range(len(self.files)):
            self.doCopy(self.files[i])
    
    def doCopy(self, file):
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

    """
    privat methods
    """

    def createFileList(self, element, doc):
        __files=list()
        __elements=xpath.Evaluate('file', element)
        for i in range(len(__elements)):
            __files.append(File(__elements[i], doc))
        return __files

# $Log: ComCopyModification.py,v $
# Revision 1.1  2006-06-30 07:56:12  mark
# initial revision
#
