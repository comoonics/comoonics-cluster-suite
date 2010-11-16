""" Comoonics path modificationset module
This module execute all given modifications with the given path as current working directory

Example Configuration:
    <modificationset type="path" name="copy-to-path">
        <path name="/var/log/messages">
            <modification type="message">
Hello world
            </modification>
        </path>
    </modificationset>
"""

# here is some internal information
# $Id: ComPathModificationset.py,v 1.4 2010-11-16 11:28:04 marc Exp $
#


__version__ = "$Revision: 1.4 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComPathModificationset.py,v $

from ComModificationset import ModificationsetJournaled
from comoonics import ComLog
from comoonics.ComPath import Path
from comoonics.ComExceptions import ComException

class PathModificationset(ModificationsetJournaled):
    """ implementation class for this modificationset """
    __logStrLevel__="comoonics.enterprisecopy.ComPathModificationset.PathModificationset"
    logger=ComLog.getLogger(__logStrLevel__)

    def __init__(self, element, doc):
        """
        default constructor:
        __init__(element, doc)
        """
        super(PathModificationset, self).__init__(element, doc)
        try:
            __path=element.getElementsByTagName('path')[0]
        except Exception:
            raise ComException("Path for modificationset \"%s\" not defined" %self.getAttribute("name", "unknown"))
        self.path=Path(__path, doc)
        self.createModificationsList(self.path.getElement().getElementsByTagName("modification"), doc)
        self.addToUndoMap(self.path.__class__.__name__, "pushd", "popd")

    def doPre(self):
        import os
        self.path.mkdir()
        self.path.pushd(self.path.getPath())
        self.journal(self.path, "pushd")
        PathModificationset.logger.debug("doPre() CWD: " + os.getcwd())
        super(PathModificationset, self).doPre()

    def doPost(self):
        import os
        super(PathModificationset, self).doPost()
        oldpath=self.path.getPath()
        self.replayJournal()
        self.commitJournal()
        #os.chdir(self.cwd)
        #umount Filesystem
        #if self.umountfs:
        #    self.filesystem.umountDir(self.mountpoint)
        PathModificationset.logger.debug("doPost() CWD: " + os.getcwd())

# $Log: ComPathModificationset.py,v $
# Revision 1.4  2010-11-16 11:28:04  marc
# - fixed bug with ComPath
#
# Revision 1.3  2010/03/08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.2  2008/08/05 13:10:14  marc
# - fixed bug so that refids now work
#
# Revision 1.1  2007/09/07 14:40:07  marc
# initial revision
#
