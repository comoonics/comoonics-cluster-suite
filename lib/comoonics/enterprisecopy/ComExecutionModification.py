""" Comoonics execution modification module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComExecutionModification.py,v 1.2 2010-02-09 21:48:24 mark Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComExecutionModification.py,v $

import exceptions
import xml.dom
from xml import xpath
import re
import os

from ComModification import Modification
from comoonics.storage.ComFile import File
from comoonics import ComSystem
from comoonics import ComLog
from comoonics.ComExceptions import ComException


class ExecutionModification(Modification):
    """ ExcecutionModification Modification"""
    
    __logStrLevel__ = "ExecutionModification"
    
    def __init__(self, element, doc):
        Modification.__init__(self, element, doc)
        
    def doRealModifications(self):
        __cmd=self.getAttribute("command")
        __rc, __ret, __err = ComSystem.execLocalGetResult(__cmd, True)
        if __rc:
            raise ComException(__cmd + ":  out:" + " ".join(__ret) + \
                                                            " err: " + " ".join(__err))
        else:
            ComLog.getLogger("ExecutionModification").debug(__cmd + ":  return:" + " ".join(__ret) + \
                                                            " err: " + " ".join(__err))
    
            
    """
    privat methods
    """


# $Log: ComExecutionModification.py,v $
# Revision 1.2  2010-02-09 21:48:24  mark
# added .storage path in includes
#
# Revision 1.1  2006/07/21 15:16:28  mark
# initial check in
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.1  2006/07/07 11:33:24  mark
# initial release
#

