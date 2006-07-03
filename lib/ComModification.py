""" Comoonics modification module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComModification.py,v 1.4 2006-07-03 12:54:26 marc Exp $
#


__version__ = "$Revision: 1.4 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComModification.py,v $
import exceptions
import xml.dom
from xml import xpath

from ComDataObject import DataObject
import ComRequirement


def getModification(element, doc):
    """ Factory function to create Modification Objects"""
    __type=element.getAttribute("type")
    if __type == "copy":
        from ComCopyModification import CopyModification
        return CopyModification(element, doc)
    if __type == "regexp":
        from ComRegexpModification import RegexpModification
        return RegexpModification(element, doc)
    raise exceptions.NotImplementedError("Modifcation for type: "+ __type + " is not implemented")
        

class Modification(DataObject):
    TAGNAME="Modification"

    """ Base Class for all source and destination objects"""
    def __init__(self, element, doc):
        DataObject.__init__(self, element, doc)
        self.requirements=self.createRequirementsList(element, doc)
        
    def doModification(self):    
        """ do the modifications 
        """
        self.doPre()
        self.doRealModifications()
        self.doPost()
        pass

    def undoModification(self):
        """ undos this modification if necessary """
        
        pass
        
    def doPre(self):
        """ do preprocessing
        """
        for i in range(len(self.requirements)):
            self.requirements[i].doPre()
            self.requirements[i].do()
            pass
            
    def doPost(self):
        """ do postprocessing
        """
        for i in range(len(self.requirements)):
            self.requirements[i].doPost()
            pass
        
    def doRealModifications(self):
        pass


    """
    privat methods
    """
    def createRequirementsList(self, element, doc):
        __reqs=list()
        __elements=xpath.Evaluate('requirement', element)
        for i in range(len(__elements)):
            __reqs.append(ComRequirement.getRequirement(__elements[i], doc))
        return __reqs
# $Log: ComModification.py,v $
# Revision 1.4  2006-07-03 12:54:26  marc
# commented out the requirements
#
# Revision 1.3  2006/07/03 07:47:22  marc
# changed the modifications
#
# Revision 1.2  2006/06/30 12:42:05  mark
# bug fixes
#
# Revision 1.1  2006/06/30 08:04:17  mark
# initial checkin
#
