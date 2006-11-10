"""Comoonics archive module


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/Attic/ComArchiv.py,v $

import os
import string
import shutil
import xml.dom
from xml.dom import Element, Node
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
        - get/addFileObj:       get and store FileObjects in Archiv
        - extract/addFile:      extract and store file/directory in Archiv
    IDEA: define iterator class to walk though DOMElements defined as ArchivChild
        - has/getNextFileInfo   returns a XML defined FileInfo to work with
    '''

    __logStrLevel__ = "Archive"
    ''' Static methods '''

    def __init__(self, element, doc):
        DataObject.__init__(self, element, doc)
        self.ahandler=ArchivHandlerFactory.getArchivHandler\
            (self.getAttribute("name"), self.getAttribute("format"), self.getAttribute("type"))


    # FIXME: Do we need this ?
    #def open(self, name, mode):
    #    ''' opens an archive '''
    #    pass

    def getDOMElement(self, name):
        '''returns an DOM Element from the given member name'''
        pass

    def getFileObj(self, name, mode="r"):
        ''' returns a fileobject of an archiv member '''
        return self.ahandler.getFileObj(name, mode)

    def addFileObj(self, file):
        ''' adds a file defined by fileobject to archiv '''
        pass

    def addFile(self, name, recursive=True):
        ''' appends a file or dirctory to archiv'''
        self.ahandler.addFile(name, recursive)

    def extractFile(self, name, dest, recursive=True):
        ''' extracts a file or directory from archiv' to destination dest '''
        self.ahandler.extractFile(name, dest, recursive)

    def createArchive(self, source):
        ''' creates an archive from the whole source tree '''
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


class ArchivMemberInfo(DataObject, TarInfo):
    ''' Member of an Archive'''
    pass

#FIXME: methods should rais a kind of NotImlementedError by default
class ArchivHandler:
    ''' Baseclass for archiv handlers'''

    __logStrLevel__ = "ArchivHandler"

    def __init__(self, name, mode):
        self.name=name
        self.mode=mode

    def open(self, name, mode):
        ''' opens an Archiv'''
        pass

    def getFileObj(self, name, mode="r"):
        ''' returns a fileobject of an archiv member '''
        pass

    def addFileObj(self, file):
        ''' adds a file defined by fileobject to archiv '''
        pass

    def addFile(self, name, recursive=True):
        ''' appends a file or dirctory to archiv'''
        pass

    def extractFile(self, name, dest, recursive=True):
        ''' extracts a file or directory from archiv' to destination dest '''
        pass

    def createArchive(self, source):
        ''' creates an archive from the whole source tree '''
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

class TarArchivHandler(ArchivHandler):
    def __init__(self, name, mode):
        self.tarfile=tarfile.open(name, mode)

    def getFileObj(self, name, mode="r"):
        ''' returns a fileobject of an archiv member '''
        return self.tarfile.exractfile(name)

    def extractFile(self, name, dest, recursive=True):
        ''' extracts a file or directory from archiv' to destination dest '''
        #TODO: check recursive flag
        return self.tarfile.extract(name, dest)

    def hasMember(self, name):
        try:
            self.tarfile.getMember(name)
        except KeyError:
            return False
        return True

class SimpleArchivHandler(ArchivHandler):
    def __init__(self, name, mode):
        ArchivHandler.__init__(self, name, mode)
        self.path="/tmp/" + name
        if os.path.exists(self.path) and not os.path.isdir(self.path):
            raise ArchivException("Path %s already exists" %(self.path))
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def hasMember(self, name):
        return os.path.exitsts(self.path+"/"+name)

    def extractFile(self, name, dest, recursive=True):
        ''' extracts a file or dirctory from archiv'''
        try:
            os.mkdir(dest+"/"+os.path.dirname(name))
        except: pass
        shutil.copy2(self.path+"/"+name, dest+"/"+os.path.dirname(name))

    def getFileObj(self, name, mode="r"):
        ''' returns a fileobject of an archiv member '''
        try:
            ComLog.getLogger(Archiv.__logStrLevel__).debug("open(%s, %s)" %(self.path+"/"+name, mode))
            file = open(self.path+"/"+name, mode)
        except:
            raise ArchivException("Cannot open %s." %(self.path+"/"+name))
        return file

    def addFile(self, name, recursive=True):
        ''' adds a file or directory to archiv'''
        try:
            os.mkdir(self.path+"/"+os.path.dirname(name))
        except: pass
        shutil.copy2(name, self.path+"/"+name)




class ArchivHandlerFactory:
    ''' Factory for different archiv type handlers'''

    '''
    Internal Exception classes
    '''

    __logStrLevel__ = "ArchivHandlerFactory"
    '''
    Static Methods
    '''

    def getArchivHandler(name, format, type):
        if format == "simple":
            return SimpleArchivHandler(name, 0)
        else:
            raise ArchivException("No ArchivHandler found for %s" %(format))

    getArchivHandler=staticmethod(getArchivHandler)

##################
# $Log: ComArchiv.py,v $
# Revision 1.2  2006-11-10 11:41:23  mark
# reorganization, minor changes, comments
#
# Revision 1.1  2006/10/09 14:22:35  mark
# initial check in
#
