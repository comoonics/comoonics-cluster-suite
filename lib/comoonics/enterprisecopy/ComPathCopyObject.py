"""
CopyObject to implement a path source/destination.
"""

# here is some internal information
# $Id: ComPathCopyObject.py,v 1.3 2008-03-12 12:28:32 marc Exp $
#


__version__ = "$Revision: 1.3 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComPathCopyObject.py,v $

from ComCopyObject import CopyObjectJournaled
from comoonics import ComLog, ComSystem
from comoonics.ComPath import Path
from comoonics.ComSystem import ExecLocalException
from comoonics.ComExceptions import ComException

import os
import os.path
from xml import xpath
import xml.dom

class PathCopyObject(CopyObjectJournaled):
    __logStrLevel__="comoonics.enterprisecopy.ComPathCopyObject.PathCopyObject"
    logger=ComLog.getLogger(__logStrLevel__)

    def __init__(self, *params, **kwds):
        """
        Supported constructors
        __init__(element, doc)
        __init__(path, source=True|False)
        __init__(path=path, source=True, dest=True)
        """
        PathCopyObject.logger.debug("__init__()")
        if (len(params)==2 and not isinstance(params[0], xml.dom.Node)) or (kwds and kwds.has_key("path") and (kwds.has_key("source") or kwds.has_key("dest"))):
            _path=None
            _source=(len(params)==2 and params[1]==True) or (kwds and kwds.has_key("source") and kwds["source"]==True)
            if len(params)>=1:
                _path=params[0]
            else:
                _path=kwds["path"]
            _tagname="destination"
            if _source:
                _tagname="source"
            doc=xml.dom.getDOMImplementation().createDocument(None, _tagname, None)
            element=doc.documentElement
            element.setAttribute("type", "path")
            if isinstance(_path, basestring):
                _path=Path(_path)
            element.appendChild(_path.getElement())
            self.path=_path
            CopyObjectJournaled.__init__(self, element, doc)
        else:
            element=params[0]
            doc=params[1]
            CopyObjectJournaled.__init__(self, element, doc)
            try:
                __path=xpath.Evaluate('path', element)[0]
                self.path=Path(__path, doc)
            except Exception:
                raise ComException("Path for copyobject \"%s\" not defined" %self.getAttribute("name", "unknown"))
        PathCopyObject.logger.debug("__init__(%s)" %self.path)
        self.addToUndoMap(self.path.__class__.__name__, "pushd", "popd")

    def __prepare(self):
        self.origpath=self.path.getPath()
        ComSystem.execMethod(self.path.mkdir)
        ComSystem.execMethod(self.path.pushd)
        if not ComSystem.isSimulate():
            self.journal(self.path, "pushd")
        PathCopyObject.logger.debug("prepareAsSource() CWD: " + os.getcwd())

    def __cleanup(self):
        oldpath=self.path.getPath()
        self.replayJournal()
        self.commitJournal()
        #os.chdir(self.cwd)
        #umount Filesystem
        #if self.umountfs:
        #    self.filesystem.umountDir(self.mountpoint)
        PathCopyObject.logger.debug("__cleanup: remove: %s" %self.getAttribute("remove", "false"))
        self.path.remove(oldpath)
        PathCopyObject.logger.debug("doPost() CWD: " + os.getcwd())
        self.path.setPath(self.origpath)

    def prepareAsSource(self):
        ''' prepare CopyObject as source '''
        self.__prepare()

    def cleanupSource(self):
        ''' do source specific cleanup '''
        self.__cleanup()

    def cleanupDest(self):
        ''' do destination specific cleanup '''
        self.__cleanup()

    def prepareAsDest(self):
        ''' prepare CopyObject as destination '''
        self.__prepare()

    def getMetaData(self):
        ''' returns the metadata element '''
        return self.getPath().getElement()

    def updateMetaData(self, element):
        ''' updates meta data information '''
        pass
    def getPath(self):
        return self.path

    def getMountpoint(self):
        return self.getPath().getElement()

def __testPathCopyset(_modset):
    print "testing PathModificationset..."
    print "cwd: %s" %os.getcwd()
    _modset.doPre()
    print "cwd(after doPre): %s" %os.getcwd()
    _modset.doCopy()
    print "cwd(before doPost): %s" %os.getcwd()
    _modset.doPost()
    print "cwd: %s" %os.getcwd()

def __testPathCopyObject(_copyobj):
    from xml.dom.ext import PrettyPrint
    PrettyPrint(_copyobj.getElement())

def main():
    _xmls=[
           """
    <copyset type="filesystem" name="save-sysreport-redhat">
        <source type="path">
            <path name="/tmp/sysreport-$(date -u +%G%m%d%k%M%S | /usr/bin/tr -d ' ')"/>
        </source>
        <destination type="backup">
            <metadata>
                <archive name='/tmp/meta-clone-lilr627-02.tar' format='tar' type='file'>
                    <file name='./path.xml'/>
                </archive>
            </metadata>
            <data>
                <archive name='/tmp/path-02.tgz' format='tar' type='file' compression='gzip'/>
            </data>
        </destination>
    </copyset>
           """,
           ]
    import logging
    ComLog.setLevel(logging.DEBUG)
    from ComCopyset import getCopyset, Copyset
    from ComCopyObject import registerCopyObject
    from xml.dom.ext.reader import Sax2
    from comoonics.ComDisk import Disk
    from ComPathCopyObject import PathCopyObject
    ComSystem.setExecMode(ComSystem.SIMULATE)
    print "registering %s" %PathCopyObject
    registerCopyObject("path", PathCopyObject)
    reader=Sax2.Reader(validate=0)
    print "Test with xml:"
    for _xml in _xmls:
        doc=reader.fromString(_xml)
        _copyset=Copyset(doc.documentElement, doc)
        print "Copyset: %s" %_copyset
        __testPathCopyset(_copyset)
    print "Test with params"
    _copyobj=PathCopyObject("/tmp/path", True)
    __testPathCopyObject(_copyobj)
    print "Test with keys"
    _copyobj=PathCopyObject(path="/tmp/path", dest=True)
    __testPathCopyObject(_copyobj)

if __name__ == '__main__':
    main()

# $Log: ComPathCopyObject.py,v $
# Revision 1.3  2008-03-12 12:28:32  marc
# - added a constructor that also would take Paths as is
# - added tests.
# - support for simulation
#
# Revision 1.2  2008/02/29 15:02:48  mark
# workaroud for bz 204
#
# Revision 1.1  2007/09/07 14:39:54  marc
# initial revision
#
