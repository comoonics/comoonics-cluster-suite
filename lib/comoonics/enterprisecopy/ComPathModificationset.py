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
# $Id: ComPathModificationset.py,v 1.1 2007-09-07 14:40:07 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComPathModificationset.py,v $

from ComModificationset import ModificationsetJournaled
from comoonics import ComLog, ComSystem
from comoonics.ComPath import Path
from comoonics.ComExceptions import ComException

import os
import os.path
from xml import xpath

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
            __path=xpath.Evaluate('path', element)[0]
        except Exception:
            raise ComException("Path for modificationset \"%s\" not defined" %self.getAttribute("name", "unknown"))
        self.path=Path(__path, doc)
        self.createModificationsList(__path.getElementsByTagName("modification"), doc)
        self.addToUndoMap(self.path.__class__.__name__, "pushd", "popd")

    def doPre(self):
        self.path.mkdir()
        self.path.pushd()
        self.journal(self.path, "pushd")
        PathModificationset.logger.debug("doPre() CWD: " + os.getcwd())
        super(PathModificationset, self).doPre()

    def doPost(self):
        super(PathModificationset, self).doPost()
        oldpath=self.path.getPath()
        self.replayJournal()
        self.commitJournal()
        #os.chdir(self.cwd)
        #umount Filesystem
        #if self.umountfs:
        #    self.filesystem.umountDir(self.mountpoint)
        PathModificationset.logger.debug("doPost() CWD: " + os.getcwd())

def __testPathModificationset(_modset):
    print "testing PathModificationset..."
    print "cwd: %s" %os.getcwd()
    _modset.doPre()
    print "cwd(after doPre): %s" %os.getcwd()
    _modset.doModifications()
    print "cwd(before doPost): %s" %os.getcwd()
    _modset.doPost()
    print "cwd(after all): %s" %os.getcwd()

def main():
    _xmls=[
           """
    <modificationset type="path" name="copy-to-path">
        <path name="/var/log/">
            <modification type="message">
Hello world
            </modification>
            <modification type="message">
Hello world2
            </modification>
        </path>
    </modificationset>
           """,
           """
    <modificationset type="path" name="copy-to-path">
        <path name="/tmp/$(date -u +%G%m%d%k%M%S | /usr/bin/tr -d ' ')">
            <modification type="message">
Hello world
            </modification>
        </path>
    </modificationset>
           """,
           ]
    import logging
    ComLog.setLevel(logging.DEBUG)
    from ComModificationset import registerModificationset, getModificationset
    from ComModification import registerModification
    from ComMessage import MessageModification
    from xml.dom.ext.reader import Sax2
    from comoonics.ComDisk import Disk
    registerModificationset("path", PathModificationset)
    registerModification("message", MessageModification)
    reader=Sax2.Reader(validate=0)
    for _xml in _xmls:
        doc=reader.fromString(_xml)
        _modset=getModificationset(doc.documentElement, doc)
        __testPathModificationset(_modset)

if __name__ == '__main__':
    main()

# $Log: ComPathModificationset.py,v $
# Revision 1.1  2007-09-07 14:40:07  marc
# initial revision
#
