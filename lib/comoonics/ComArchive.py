"""Comoonics archive module


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id $
#


__version__ = "$Revision: 1.8 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/Attic/ComArchive.py,v $

import os
import string
import shutil
import tempfile
import xml.dom
from xml.dom import Element, Node
from xml.dom.ext.reader import Sax2

import tarfile
from tarfile import TarInfo

import ComSystem
from ComDataObject import DataObject
import ComLog
from ComExceptions import ComException

__all__ = ["Archive", "ArchiveHandlerFactory", "ArchiveHandler"]

class ComNotImplementedError(ComException): pass

class ArchiveException(ComException):pass

class Archive(DataObject):
    '''
    Internal Exception classes
    '''
    class ArchiveException(ComException): pass

    '''
    Interface/Wrapper class for all archiv handler
    provides methods to access archives
    method types are
        - get/addDOMElement:    get and store DOMElements in Archive
        - getFileObj:           get FileObjects from Archive
        - extract/addFile:      extract and store file/directory in Archive
    IDEA: define iterator class to walk though DOMElements defined as ArchiveChild
        - has/getNextFileInfo   returns a XML defined FileInfo to work with
    '''

    __logStrLevel__ = "Archive"
    ''' Static methods '''

    def __init__(self, element, doc):
        DataObject.__init__(self, element, doc)
        self.ahandler=ArchiveHandlerFactory.getArchiveHandler \
            (self.getAttribute("name"), self.getAttribute("format"), \
             self.getAttribute("type"), self.getAttribute("compression", default="none"))
        self.child=self.element.firstChild

    def closeAll(self):
        ''' closes all open fds '''
        self.ahandler.closeAll()

    def getDOMElement(self, name):
        '''returns a DOM Element from the given member name'''
        file=self.ahandler.getFileObj(name)
        reader = Sax2.Reader()
        doc = reader.fromStream(file)
        self.ahandler.closeAll()
        return doc.documentElement

    def getNextDOMElement(self):
        ''' returns a DOM representation of the next defined file
            <file name="filename.xml"/>
        '''
        file=self.getNextFileObj()
        # there is no nextElement
        if file == None:
            return None

        reader = Sax2.Reader()
        doc = reader.fromStream(file)
        self.ahandler.closeAll()
        return doc.documentElement


    def addNextDOMElement(self, element):
        """ adds this element to the next file element in this archive """
        self.addDOMElement(element)

    def addDOMElement(self, element, name=None):
        '''adds an DOM Element as member name'''
        if name == None:
            name=self.getNextFileName()
        fd, path = tempfile.mkstemp()
        file = os.fdopen(fd, "w")
        xml.dom.ext.PrettyPrint(element, file)
        file.close()
        try:
            self.ahandler.addFile(path, name)
            os.unlink(path)
        except Exception, e:
            os.unlink(path)
            raise e

    def getFileObj(self, name):
        ''' returns a fileobject of an archiv member '''
        return self.ahandler.getFileObj(name)

    def getNextFileName(self):
        """ returns the name of the next file in the archive as stated by the file element """
        while self.child != None:
            # This is not an element
            if self.child.nodeType != Node.ELEMENT_NODE:
                self.child=self.child.nextSibling
                continue
            # This is not a file
            if self.child.tagName != "file":
                self.child=self.child.nextSibling
                continue
            else:
                break
        # there is no other child
        if self.child == None:
            return None
        filename=self.child.getAttribute("name")
        self.child=self.child.nextSibling
        return filename

    def getNextFileObj(self):
        ''' returns a fileobject of the next defined file
            <file name="filename.xml"/>
        '''
        file = self.getFileObj(self.getNextFileName())
        return file


    def addFile(self, name, arcname=None, recursive=True):
        ''' appends a file or dirctory to archiv'''
        self.ahandler.addFile(name, arcname, recursive)

    def extractFile(self, name, dest):
        ''' extracts a file or directory from archiv' to destination dest '''
        self.ahandler.extractFile(name, dest)

    def createArchive(self, source, cdir=None):
        ''' creates an archive from the whole source tree '''
        ComLog.getLogger("Copyset").debug("createArchive(%s, %s)" % (source, cdir))
        self.ahandler.createArchive(source, cdir)

    def extractArchive(self, dest):
        ''' extracts the whole archive to dest'''
        self.ahandler.extractArchive(dest)

    def getMemberInfo(self, name):
        ''' returns a memberinfo object of an archiv menber '''
        pass

    def hasMember(self, name):
        ''' checks wether archive hosts member file
            returns True/False
        '''
        return self.ahandler.hasMember(name)


class ArchiveMemberInfo(DataObject, TarInfo):
    ''' Member of an Archivee'''
    pass

#FIXME: methods should rais a kind of NotImlementedError by default
class ArchiveHandler:
    ''' Baseclass for archiv handlers'''

    __logStrLevel__ = "ArchiveHandler"

    def __init__(self, name):
        self.name=name

    def closeAll(self):
        pass

    def getFileObj(self, name):
        ''' returns a fileobject of an archiv member '''
        pass

    def addFile(self, name, arcname=None, recursive=True):
        ''' appends a file or dirctory to archiv'''
        pass

    def extractFile(self, name, dest):
        ''' extracts a file or directory from archiv' to destination dest '''
        pass

    def createArchive(self, source, cdir):
        ''' creates an archive from the whole source tree
            if cdir is defined, archive handler will first change
            into cdir directory
        '''
        pass

    def extractArchive(self, dest):
        ''' extracts the whole archive to dest'''
        pass

    def getMemberInfo(self, name):
        ''' returns a memberinfo object of an archiv menber '''
        pass

    def hasMember(self, name):
        ''' checks wether archive hosts member file
            returns True/False
        '''
        pass

    def __niy(self):
        ''' default behavior is NotImplementedError '''
        raise ComNotImplementedError()

'''
Archivee Handlers
'''


''' ArchiveeHandler for tar files '''
class TarArchiveHandler(ArchiveHandler):

    TAR="/bin/tar"

    def __init__(self, name):
        self.tarfile=name
        self.compression=""
        self.compressionmode=""

    def closeAll(self):
        ''' closes all open fds '''
        self.tarf.close()

    def getFileObj(self, name):
        ''' returns a fileobject of an archiv member '''
        self.tarf=tarfile.open(self.tarfile, "r"+self.compressionmode)
        file=self.tarf.extractfile(os.path.normpath(name))
        return file

    def extractFile(self, name, dest):
        ''' extracts a file or directory from archiv' to destination dest '''
        __cmd = TarArchiveHandler.TAR +" -x " + self.compression + " -f " \
                + self.tarfile + " -C " + dest + " " + name
        __rc, __rv = ComSystem.execLocalGetResult(__cmd)
        if __rc >> 8 != 0:
            raise RuntimeError("running %s failed" %__cmd)

    def addFile(self, name, arcname=None, recursive=True):
        ''' appends a file or dirctory to archiv'''
        try:
            tarf=tarfile.open(self.tarfile, "a:"+self.compressionmode)
        except IOError:
            tarf=tarfile.open(self.tarfile, "w:"+self.compressionmode)
        tarf.add(os.path.normpath(name), arcname, recursive)
        tarf.close()


    def createArchive(self, source, cdir=None):
        ''' creates an archive from the whole source tree
            stays in the same filesystem
         '''
        if not cdir:
            cdir=os.getcwd()
        __cmd = TarArchiveHandler.TAR +" -cl " + self.compression + " -f " \
                + self.tarfile + " -C " + cdir + " " + source
        __rc, __rv = ComSystem.execLocalGetResult(__cmd)
        if __rc >> 8 != 0:
            raise RuntimeError("running %s failed" %__cmd)


    def extractArchive(self, dest):
        ''' extracts the whole archive to dest'''
        self.extractFile("", dest)


    def hasMember(self, name):
        ''' checks if archive has a member named name '''
        tarf = tarfile.open(self.tarfile, "r"+self.compressionmode)
        try:
            tarf.getmember(os.path.normpath(name))
            tarf.close()
        except KeyError:
            tarf.close()
            return False
        return True


''' Archivee Handler for gzip compressed tar files '''
class TarGzArchiveHandler(TarArchiveHandler):
    def __init__(self, name):
        TarArchiveHandler.__init__(self, name)
        self.compression="-z "
        self.compressionmode=":gz"


''' Archivee Handler for bzip2 compressed tar files '''
class TarBz2ArchiveHandler(TarArchiveHandler):
    def __init__(self, name):
        TarArchiveHandler.__init__(self, name)
        self.compression="-j "
        self.compressionmode=":bz2"


''' Simple Archive Handler - uses local file system '''
class SimpleArchiveHandler(ArchiveHandler):
    def __init__(self, name):
        ArchiveHandler.__init__(self, name)
        self.path="/tmp/" + name
        if os.path.exists(self.path) and not os.path.isdir(self.path):
            raise ArchiveException("Path %s already exists" %(self.path))
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def hasMember(self, name):
        return os.path.exists(self.path+"/"+name)

    def extractFile(self, name, dest):
        ''' extracts a file or dirctory from archiv'''
        try:
            os.mkdir(dest+"/"+os.path.dirname(name))
        except: pass
        shutil.copy2(self.path+"/"+name, dest+"/"+os.path.dirname(name))

    def getFileObj(self, name):
        ''' returns a fileobject of an archiv member '''
        try:
            ComLog.getLogger(Archive.__logStrLevel__).debug("open(%s)" %(self.path+"/"+name))
            file = open(self.path+"/"+name, "r")
        except:
            raise ArchiveException("Cannot open %s." %(self.path+"/"+name))
        return file

    def addFile(self, name, arcname=None,recursive=True):
        ''' adds a file or directory to archiv'''
        try:
            os.mkdir(self.path+"/"+os.path.dirname(name))
        except: pass
        shutil.copy2(name, self.path+"/"+name)



''' Factory class for ArchiveHandler '''
class ArchiveHandlerFactory:
    ''' Factory for different archiv type handlers'''

    '''
    Internal Exception classes
    '''

    __logStrLevel__ = "ArchiveHandlerFactory"
    '''
    Static Methods
    '''

    def getArchiveHandler(name, format, type, compression="none"):
        if format == "simple":
            return SimpleArchiveHandler(name)
        if format == "tar":
            if compression == "none":
                return TarArchiveHandler(name)
            if compression == "gzip":
                return TarGzArchiveHandler(name)
            if compression == "bz2":
                return TarBz2ArchiveHandler(name)
        else:
            raise ArchiveException("No ArchiveHandler found for %s" %(format))

    getArchiveHandler=staticmethod(getArchiveHandler)

##################
# $Log: ComArchive.py,v $
# Revision 1.8  2007-03-08 10:54:05  marc
# fixed bugs from eclipse
#
# Revision 1.7  2006/12/14 09:12:15  mark
# added -l option to tar
#
# Revision 1.6  2006/12/08 09:43:50  mark
# minor fixes
#
# Revision 1.5  2006/11/27 12:12:50  marc
# bug fix
#
# Revision 1.4  2006/11/23 13:58:24  mark
# minor fixes
#
# Revision 1.3  2006/11/23 10:13:08  mark
# added getNextElement, getNextDOMElement
#
# Revision 1.2  2006/11/22 17:01:45  mark
# minor fix
#
# Revision 1.1  2006/11/22 16:58:19  mark
# added 'e' to Archiv ;-)
#
# Revision 1.3  2006/11/22 16:47:26  mark
# first stable revision
# Archive Handler:
# tar
# tar.gz
# tar.bz2
#
# Revision 1.2  2006/11/10 11:41:23  mark
# reorganization, minor changes, comments
#
# Revision 1.1  2006/10/09 14:22:35  mark
# initial check in
#
