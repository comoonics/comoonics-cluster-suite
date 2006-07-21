""" Comoonics regexp modification module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComRegexpModification.py,v 1.2 2006-07-21 08:59:09 mark Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComRegexpModification.py,v $

import exceptions
import xml.dom
from xml import xpath
import re
import os

from ComFileModification import FileModification
from comoonics.ComFile import File
from comoonics import ComSystem
from comoonics import ComLog

CMD_CP="/bin/cp"

class RegexpModification(FileModification):
    SAVESTRING=".regexp"
    """ Regular Expression Modification"""
    def __init__(self, element, doc):
        FileModification.__init__(self, element, doc)
        
    def doModifications(self, file):
        save=True
        if self.hasAttribute("nobackup"):
            if self.getAttribute("nobackup") == "1":
                save=False
        self.doRegexpModifications(file, save)
        
    def doRegexpModifications(self, file, save=True):
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
            
# $Log: ComRegexpModification.py,v $
# Revision 1.2  2006-07-21 08:59:09  mark
# added nobackup option
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.2  2006/07/07 11:35:00  mark
# changed to inherit FileModification
#
# Revision 1.1  2006/06/30 12:42:45  mark
# initial checkin
#
