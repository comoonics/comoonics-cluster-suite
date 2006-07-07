""" Comoonics generic file modification module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFileModification.py,v 1.1 2006-07-07 11:33:24 mark Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComFileModification.py,v $

import exceptions
import xml.dom
from xml import xpath
import re
import os

from ComModification import Modification
from ComFile import File
import ComSystem
import ComLog


class FileModification(Modification):
    """ generic FileModification Modification"""
    def __init__(self, element, doc):
        Modification.__init__(self, element, doc)
        self.files=self.createFileList(element, doc)
        
    def doRealModifications(self):
        for i in range(len(self.files)):
            self.doModifications(self.files[i])
    
    def doModifications(self, file, save=True):
        pass
            
    """
    privat methods
    """

    def createFileList(self, element, doc):
        __files=list()
        __elements=xpath.Evaluate('file', element)
        for i in range(len(__elements)):
            __files.append(File(__elements[i], doc))
        return __files

# $Log: ComFileModification.py,v $
# Revision 1.1  2006-07-07 11:33:24  mark
# initial release
#

