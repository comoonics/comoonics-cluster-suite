"""Comoonics archive module


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id $
#


__version__ = "$Revision: 1.3 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/Attic/ComArchiv.py,v $

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

__all__ = ["Archiv", "ArchivHandlerFactory", "ArchivHandler"]

class ArchivException(ComException):pass

class Archiv(DataObject):
    '''
    Internal Exception classes
    '''
    class ArchivException(ComException): pass

    '''
    Interface/Wrapper class for all archiv handler
    provides methods to access archives
    method types are
        - get/addDOMElement:    get and store DOMElements in Archiv
        - getFileObj:           get FileObjects from Archiv
        - extract/addFile:      extract and store file/directory in Archiv
    IDEA: define iterator class to walk though DOMElements defined as ArchivChild
        - has/getNextFileInfo   returns a XML defined FileInfo to work with
    '''

    __logStrLevel__ = "Archive"
    ''' Static methods '''

    def __init__(self, element, doc):
        DataObject.__init__(self, element, doc)
        self.ahandler=ArchivHandlerFactory.getArchivHandler \
            (self.getAttribute("name"), self.getAttribute("format"), \
             self.getAttribute("type"), self.getAttribute("compression", default="none"))


    def closeAll(self):
        ''' closes all open fds '''
        self.ahandler.closeAll()

    def getDOMElement(self, name):
        '''returns an DOM Element from the given member name'''
        file=self.ahandler.getFileObj(name)
        reader = Sax2.Reader()
        doc = reader.fromStream(file)
        return doc.documentElement

    def addDOMElement(self, element, name):
        '''adds an DOM Element as member name'''
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

    def addFile(self, name, arcname=None, recursive=True):
        ''' appends a file or dirctory to archiv'''
        self.ahandler.addFile(name, arcname, recursive)

    def extractFile(self, name, dest):
        ''' extracts a file or directory from archiv' to destination dest '''
        self.ahandler.extractFile(name, dest)

    def createArchiv(self, source, cdir=None):
        ''' creates an archive from the whole source tree '''
        self.ahandler.createArchiv(source, cdir)

    def extractArchiv(self, dest):
        ''' extracts the whole archive to dest'''
        self.ahandler.extractArchiv(dest)

    def getMemberInfo(self, name):
        ''' returns a memberinfo object of an archiv menber '''
        pass

    def hasMember(self, name):
        ''' checks wether archive hosts member file
            returns True/False
        '''
        return self.ahandler.hasMember(name)


class ArchivMemberInfo(DataObject, TarInfo):
    ''' Member of an Archive'''
    pass

#FIXME: methods should rais a kind of NotImlementedError by default
class ArchivHandler:
    ''' Baseclass for archiv handlers'''

    __logStrLevel__ = "ArchivHandler"

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

    def extractArchiv(self, dest):
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
Archive Handlers
'''


''' ArchiveHandler for tar files '''
class TarArchivHandler(ArchivHandler):

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
        __cmd = TarArchivHandler.TAR +" -x " + self.compression + " -f " \
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


    def createArchiv(self, source, cdir=None):
        ''' creates an archive from the whole source tree '''
        if not cdir:
            cdir=os.path.cwd()
        __cmd = TarArchivHandler.TAR +" -c " + self.compression + " -f " \
                + self.tarfile + " -C " + cdir + " " + source
        __rc, __rv = ComSystem.execLocalGetResult(__cmd)
        if __rc >> 8 != 0:
            raise RuntimeError("running %s failed" %__cmd)


    def extractArchiv(self, dest):
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


''' Archive Handler for gzip compressed tar files '''
class TarGzArchivHandler(TarArchivHandler):
    def __init__(self, name):
        TarArchivHandler.__init__(self, name)
        self.compression="-z "
        self.compressionmode=":gz"


''' Archive Handler for bzip2 compressed tar files '''
class TarBz2ArchivHandler(TarArchivHandler):
    def __init__(self, name):
        TarArchivHandler.__init__(self, name)
        self.compression="-j "
        self.compressionmode=":bz2"


''' Simple Archiv Handler - uses local file system '''
class SimpleArchivHandler(ArchivHandler):
    def __init__(self, name):
        ArchivHandler.__init__(self, name)
        self.path="/tmp/" + name
        if os.path.exists(self.path) and not os.path.isdir(self.path):
            raise ArchivException("Path %s already exists" %(self.path))
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def hasMember(self, name):
        return os.path.exitsts(self.path+"/"+name)

    def extractFile(self, name, dest):
        ''' extracts a file or dirctory from archiv'''
        try:
            os.mkdir(dest+"/"+os.path.dirname(name))
        except: pass
        shutil.copy2(self.path+"/"+name, dest+"/"+os.path.dirname(name))

    def getFileObj(self, name):
        ''' returns a fileobject of an archiv member '''
        try:
            ComLog.getLogger(Archiv.__logStrLevel__).debug("open(%s)" %(self.path+"/"+name))
            file = open(self.path+"/"+name, "r")
        except:
            raise ArchivException("Cannot open %s." %(self.path+"/"+name))
        return file

    def addFile(self, name, arcname=None,recursive=True):
        ''' adds a file or directory to archiv'''
        try:
            os.mkdir(self.path+"/"+os.path.dirname(name))
        except: pass
        shutil.copy2(name, self.path+"/"+name)



''' Factory class for ArchivHandler '''
class ArchivHandlerFactory:
    ''' Factory for different archiv type handlers'''

    '''
    Internal Exception classes
    '''

    __logStrLevel__ = "ArchivHandlerFactory"
    '''
    Static Methods
    '''

    def getArchivHandler(name, format, type, compression="none"):
        if format == "simple":
            return SimpleArchivHandler(name)
        if format == "tar":
            if compression == "none":
                return TarArchivHandler(name)
            if compression == "gzip":
                return TarGzArchivHandler(name)
            if compression == "bz2":
                return TarBz2ArchivHandler(name)
        else:
            raise ArchivException("No ArchivHandler found for %s" %(format))

    getArchivHandler=staticmethod(getArchivHandler)

##################
# $Log: ComArchiv.py,v $
# Revision 1.3  2006-11-22 16:47:26  mark
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
