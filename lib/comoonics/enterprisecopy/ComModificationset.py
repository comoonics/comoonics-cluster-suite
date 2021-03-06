"""Comoonics modificationset module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComModificationset.py,v 1.8 2011-02-15 14:52:47 marc Exp $
#


__version__ = "$Revision: 1.8 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComModificationset.py,v $

from comoonics.ComDataObject import DataObject
from comoonics.ecbase.ComJournaled import JournaledObject
from comoonics import ComLog
from comoonics.enterprisecopy import ComModification
from comoonics.enterprisecopy.ComRequirement import Requirements

log=ComLog.getLogger("comoonics.enterprisecopy.ComModificationSet")

_modificationset_registry=dict()

def registerModificationset(_type, _class):
    _modificationset_registry[_type]=_class

def getModificationset(element, doc):
    """ Factory function to create Modificationset Objects"""
    __type=element.getAttribute("type")
    if __type == "filesystem":
        from ComFilesystemModificationset import FilesystemModificationset
        return FilesystemModificationset(element, doc)
    elif __type == "partition":
        from ComPartitionModificationset import PartitionModificationset
        return PartitionModificationset(element, doc)
    elif __type == "storage":
        from comoonics.enterprisecopy.ComStorageModificationset import StorageModificationset
        return StorageModificationset(element, doc)
    elif _modificationset_registry.has_key(__type):
        return _modificationset_registry[__type](element, doc)
    raise NotImplementedError("Modifcicationset for type " + __type + " is not implemented")

class Modificationset(DataObject, Requirements):
    TAGNAME = "modificationset"
    __logStrLevel__="comoonics.enterprisecopy.ComModificationset.Modificationset"
    def __init__(self, element, doc):
        DataObject.__init__(self, element, doc)
        Requirements.__init__(self, element, doc)
        self.modifications=list()
        #log.debug("Modificationset CWD: " + os.getcwd())

    def doModifications(self):
        """starts the modification process"""
        self.doRealModifications()

    def undoModifications(self):
        """undos all modifications """
        ComLog.getLogger(Modificationset.__logStrLevel__).debug("Modifications: %s" % self.modifications)
        self.modifications.reverse()
        for mod in self.modifications:
            try:
                mod.undoRequirements()
                mod.undoModification()
            except NotImplementedError, e:
                log.warning(e)

    def doRealModifications(self):
        for mod in self.modifications:
            try:
                #mod.doPre()
                mod.doModification()
                #mod.doPost()
            except NotImplementedError, e:
                log.warning(e)

    def getModifications(self):
        return self.modifications

    """
    privat methods
    """
    def createModificationsList(self, emods, doc, *args, **kwds):
        for i in range(len(emods)):
            self.modifications.append(ComModification.getModification(emods[i], doc, *args, **kwds))
        #ComLog.getLogger(Modificationset.__logStrLevel__).debug("Modifications: %s" % self.modifications)
        return self.modifications


class ModificationsetJournaled(Modificationset, JournaledObject):
    """
    Derives anything from Modification plus journals all actions.
    Internally ModificationsetJournaled has a map of undomethods and references to objects that methods should be executed upon.
    If undo is called the journal stack is executed from top to buttom (LIFO) order.
    """
    __logStrLevel__ = "comoonics.enterprisecopy.ComModificationSet.ModificationsetJournaled"

    def __init__(self, element, doc):
        Modificationset.__init__(self, element, doc)
        JournaledObject.__init__(self)
        self.__journal__=list()
        self.__undomap__=dict()

    def undoModifications(self):
        """
        just calls replayJournal and undoModifications from Modificationset
        """
        Modificationset.undoModifications(self)
        self.replayJournal()

# $Log: ComModificationset.py,v $
# Revision 1.8  2011-02-15 14:52:47  marc
# - changes for ecbase rebase to comoonics.ecbase package
#
# Revision 1.7  2010/03/08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.6  2007/09/07 14:38:56  marc
# -added registry implementation.
# -logging
#
# Revision 1.5  2007/04/10 16:53:09  marc
# mod.doPre and mod.doPost is called by mod.doModification.
# Could be changed back later not clear of dependencies.
#
# Revision 1.4  2007/03/26 08:00:58  marc
# - added Requirements and more functionality to parents
#
# Revision 1.3  2007/02/09 12:26:12  marc
# added StorageModificationSet
#
# Revision 1.2  2006/12/08 09:42:04  mark
# added support for PartitionModificationset
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.5  2006/07/06 12:40:01  mark
# added ModificationsetJournaled
#
# Revision 1.4  2006/07/03 12:54:55  marc
# bugfixed undoing.
#
# Revision 1.3  2006/07/03 07:47:37  marc
# changed the list of modifications
#
# Revision 1.2  2006/06/30 12:38:35  marc
# added undo
#
# Revision 1.1  2006/06/30 08:04:41  mark
# initial checkin
#
