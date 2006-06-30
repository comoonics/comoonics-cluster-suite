""" Comoonics regexp modification module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComRegexpModification.py,v 1.1 2006-06-30 12:42:45 mark Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComRegexpModification.py,v $

import exceptions
import xml.dom
from xml import xpath
import re
import os

from ComModification import Modification
from ComFile import File
import ComSystem
import ComLog

CMD_CP="/bin/cp"

class RegexpModification(Modification):
    SAVESTRING=".regexp"
    """ Regular Expression Modification"""
    def __init__(self, element, doc):
        Modification.__init__(self, element, doc)
        self.files=self.createFileList(element, doc)
        
    def doRealModifications(self):
        for i in range(len(self.files)):
            self.doRegexp(self.files[i])
    
    def doRegexp(self, file, save=True):
        __search = self.getAttribute("search")
        __replace = self.getAttribute("replace")
        if save:
            __cmd = list()
            __cmd.append(CMD_CP)
            __cmd.append(file.getAttribute("name"))
            __cmd.append(file.getAttribute("name")+self.SAVESTRING) 
            __rc, __ret = ComSystem.execLocalStatusOutput(" ".join(__cmd))
            if __rc:
                ComLog.getLogger("RegexpModification").error(" ".join(__cmd) + " " + __ret)
            else:
                ComLog.getLogger("RegexpModification").debug(" ".join(__cmd) + " " + __ret) 
        if file.hasAttribute("sourcefile"):
            __source=open(file.getAttribute("sourcefile"))
        else:
            __source=open(file.getAttribute("name"))
        __lines=__source.readlines()
        __source.close()
        __dest=open(file.getAttribute("name"), 'w')
        for line in __lines:
            __dest.write(re.sub(__search, __replace, line))
        
        __dest.close()
            
    """
    privat methods
    """

    def createFileList(self, element, doc):
        __files=list()
        __elements=xpath.Evaluate('file', element)
        for i in range(len(__elements)):
            __files.append(File(__elements[i], doc))
        return __files

# $Log: ComRegexpModification.py,v $
# Revision 1.1  2006-06-30 12:42:45  mark
# initial checkin
#
