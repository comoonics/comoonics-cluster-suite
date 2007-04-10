""" Comoonics modification module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComModification.py,v 1.5 2007-04-10 16:52:17 marc Exp $
#


__version__ = "$Revision: 1.5 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComModification.py,v $
import exceptions
import xml.dom
from xml import xpath

from comoonics.ComDataObject import DataObject
from comoonics.ComJournaled import JournaledObject
from comoonics.enterprisecopy.ComRequirement import Requirements

def getModification(element, doc, *args, **kwds):
    """ Factory function to create Modification Objects"""
    __type=element.getAttribute("type")
    if kwds.has_key("type"):
        __type=kwds["type"]
    if __type == "copy":
        from ComCopyModification import CopyModification
        return CopyModification(element, doc, *args, **kwds)
    elif __type == "move":
        from ComMoveModification import MoveModification
        return MoveModification(element, doc, *args, **kwds)
    elif __type == "regexp":
        from ComRegexpModification import RegexpModification
        return RegexpModification(element, doc, *args, **kwds)
    elif __type == "exec":
        from ComExecutionModification import ExecutionModification
        return ExecutionModification(element, doc, *args, **kwds)
    elif __type == "storage":
        from comoonics.storage.ComStorageModification import StorageModification
        return StorageModification(element, doc, *args, **kwds)
    raise exceptions.NotImplementedError("Modifcation for type: "+ __type + " is not implemented")


class Modification(DataObject, Requirements):
    TAGNAME="Modification"

    """ Base Class for all source and destination objects"""
    def __init__(self, element, doc, *args, **kwds):
        DataObject.__init__(self, element, doc)
        Requirements.__init__(self, element, doc)

    def doModification(self):
        """ do the modifications and requirements if possible
        """
        self.doPre()
        self.doRealModifications()
        self.doPost()

    def undoModification(self):
        """ undos this modification if necessary """
        pass

    def doRealModifications(self):
        pass

class ModificationJournaled(Modification, JournaledObject):
    """
    Derives anything from Modification plus journals all actions.
    Internally ModificationJournaled has a map of undomethods and references to objects that methods should be executed upon.
    If undo is called the journal stack is executed from top to buttom (LIFO) order.
    """
    __logStrLevel__ = "CopysetJournaled"

    def __init__(self, element, doc):
        Modification.__init__(self, element, doc)
        JournaledObject.__init__(self)
        self.__journal__=list()
        self.__undomap__=dict()

    def undoModification(self):
        """
        just calls replayJournal
        """
        self.replayJournal()


# $Log: ComModification.py,v $
# Revision 1.5  2007-04-10 16:52:17  marc
# removed an unnecessary pass
#
# Revision 1.4  2007/03/26 08:00:08  marc
# - moved the requirements to parentclass Requirements
# - added ModificationJournaled
#
# Revision 1.3  2007/02/09 12:25:50  marc
# added StorageModification
#
# Revision 1.2  2006/07/21 15:16:56  mark
# added ExecutionModification
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.5  2006/07/07 11:33:44  mark
# added factory for move
#
# Revision 1.4  2006/07/03 12:54:26  marc
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
