""" Comoonics Requirement class


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id: ComRequirement.py,v 1.4 2007-09-07 14:41:55 marc Exp $
#


__version__ = "$Revision: 1.4 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComRequirement.py,v $

from comoonics.ComDataObject import DataObject
from comoonics.ComExceptions import ComException
from comoonics.ComJournaled import JournaledObject
from comoonics import ComLog

class UnsupportedRequirementException(ComException): pass

_requirement_registry=dict()

def registerRequirement(_type, _class):
    _requirement_registry[_type]=_class

def getRequirement(element, doc):
    """ Factory function to create Requirement"""
    __type=element.getAttribute("type")
    if __type == "archive":
        from ComArchiveRequirement import ArchiveRequirement
        return ArchiveRequirement(element, doc)
    elif __type == "scsi":
        from ComSCSIRequirement import SCSIRequirement
        return SCSIRequirement(element, doc)
    elif _requirement_registry.has_key(__type):
        return _requirement_registry[__type](element, doc)
    else:
        raise UnsupportedRequirementException("Unsupported Requirement type %s in element %s" % (__type, element.tagName))

class Requirement(DataObject):
    """
    Requirement baseclass is responsible for resolving requirements needed for the copy or modificationsets.
    """

    """
    Static methods and objects/attributes
    """
    __logStrLevel__ = "Requirement"
    log=ComLog.getLogger(__logStrLevel__)
    TAGNAME = "requirement"
    PRE=1
    POST=2
    BOTH=3

    """
    Public methods
    """

    def __init__(self, element, doc):
        """
        Creates a new requirement instance
        """
        DataObject.__init__(self, element, doc)
        self.order=Requirement.PRE

    def isPre(self):
        """
        checks if this requirement has to be run before (doPre) or after (doPost). default True
        """
        if (self.hasAttribute("order") and self.getAttribute("order")!="pre" and self.getAttribute("order")!="before") or self.order==Requirement.POST:
            return False
        return True

    def isPost(self):
        """
        checks if this requirement has to be run before (doPre) or after (doPost). default True
        """
        if (self.hasAttribute("order") and (self.getAttribute("order")=="post" or self.getAttribute("order")=="after")) or self.order==Requirement.POST or self.order==Requirement.BOTH:
            return True
        return False

    def doPre(self):
        """
        Does something previously
        """
        pass

    def do(self):
        """
        If need be does something
        called pre AND post
        """
        pass

    def doPost(self):
        """
        Does something afterwards
        """
        pass

    def doUndo(self):
        """
        Undos this requirement
        """
        pass

class RequirementJournaled(Requirement, JournaledObject):
    """
    Derives anything from Copyset plus journals all actions.
    Internally CopysetJournaled has a map of undomethods and references to objects that methods should be executed upon.
    If undo is called the journal stack is executed from top to buttom (LIFO) order.
    """
    __logStrLevel__ = "RequirementJournaled"

    def __init__(self, element, doc):
        Requirement.__init__(self, element, doc)
        JournaledObject.__init__(self)
        self.__journal__=list()
        self.__undomap__=dict()

    def undoRequirement(self):
        """
        just calls replayJournal
        """
        self.replayJournal()

class Requirements(object):
    __logStrLevel__ = "comoonics.enterprisecopy.ComRequirements.Requirements"
    log=ComLog.getLogger(__logStrLevel__)
    def __init__(self, element, doc):
        __reqs=list()
        __elements=element.getElementsByTagName(Requirement.TAGNAME)
        for i in range(len(__elements)):
            if __elements[i].parentNode == element:
                __reqs.append(getRequirement(__elements[i], doc))
        self.requirements=__reqs
        #Requirements.log.debug("__init__: requirements: %s, baseclass: %s" %(self.requirements, self.__class__))
    def getRequirements(self):
        return self.requirements
    def doPre(self):
        """ do preprocessing
        """
        #Requirements.log.debug("doPre: requirements: %s, baseclass: %s" %(self.requirements, self.__class__))
        for i in range(len(self.requirements)):
            if self.requirements[i].isPre():
                self.requirements[i].doPre()
            self.requirements[i].do()

    def doPost(self):
        """ do postprocessing
        """
        #Requirements.log.debug("doPost: requirements: %s, baseclass: %s" %(self.requirements, self.__class__))
        for i in range(len(self.requirements)):
            if self.requirements[i].isPost():
                self.requirements[i].doPost()
            self.requirements[i].do()

    def undoRequirements(self):
        """ undo the requirements """
        for req in self.requirements:
            if isinstance(req, RequirementJournaled):
                req.undoRequirement()


###################################
# $Log: ComRequirement.py,v $
# Revision 1.4  2007-09-07 14:41:55  marc
# -added registry implementation.
# -logging
#
# Revision 1.3  2007/04/10 16:54:04  marc
# added attribute order for allowing requirements with doPre and doPost being called not only one method. (see ArchiveRequirement)
#
# Revision 1.2  2007/03/26 08:04:29  marc
# - added class Requirments as parentclass for all children needing requirements
# - changed undoCopy to undoRequirement
# - logging
# - added support Requirements called after or before executing a child (see doPre, doPost and do)
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.4  2006/06/30 12:40:29  marc
# added undo
#
# Revision 1.3  2006/06/29 13:37:15  marc
# *** empty log message ***
#
# Revision 1.2  2006/06/29 12:34:22  marc
# added Factory and changed classname.
#
# Revision 1.1  2006/06/29 12:20:28  marc
# initial revision
#