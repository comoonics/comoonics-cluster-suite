"""Comoonics archive module


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id $
#


__version__ = "$Revision: 1.1 $"
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
    class ArchiveException(ComException): pass

    '''
    Baseclass for all Archiv Objects. Shares attributes and methods for all subclasses
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

    def getElement(self, name):
        '''returns an DOM Element from the given member name'''
        pass

    def getNextMemberFile(self):
        ''' returns next File defined in DOM '''
        pass

    def getNextMemberFileInArchiv(self):
        ''' return next File in Archiv'''
        pass

    def getFileObj(self, name, mode="r"):
        ''' returns a fileobject of an archiv member '''
        return self.ahandler.getFileObj(name, mode)

    def getMemberInfo(self, name):
        ''' returns a memberinfo object of an archiv menber '''
        pass

    def extractNextMemberFile(self):
        pass

    def extractFile(self, name, dest, recursive=True):
        ''' extracts a file or dirctory from archiv'''
        self.ahandler.extractFile(name, dest, recursive)

    def extractAll(self, dest):
        ''' extracts the whole archive'''
        pass

    def appendNextMemberFile(self):
        pass

    def addFile(self, name, recursive=True):
        ''' appends a file or dirctory to archiv'''
        self.ahandler.addFile(name, recursive)

    def createArchive(self, source):
        ''' creates an archive from the whole source tree '''
        pass

    def hasMember(self, name):
        pass

    def hasNextMemberFile(self):
        pass

    def hasNextMemberFileInArchiv(self):
        pass


class ArchivMemberInfo(DataObject, TarInfo):
    ''' Member of an Archive'''


# FIXME: de we need the wrapper class ?
class ArchivHandler:
    ''' Baseclass for archiv handlers'''

    __logStrLevel__ = "ArchivHandler"

    def __init__(self, name, mode):
        self.name=name
        self.mode=mode

    def open(self, name, mode):
        ''' opens an Archiv'''
        pass

    def hasMember(self, name):
        pass

    def extractFile(self, name, dest, recursive=True):
        ''' extracts a file or dirctory from archiv'''
        pass

    def getFileObj(self, name, mode="r"):
        ''' returns a fileobject of an archiv member '''
        pass


    def addFile(self, name, recursive=True):
        ''' adds a file or dirctory to archiv'''
        pass

class TarArchivHandler(ArchivHandler):
    def __init__(self, name, mode):
        self.tarfile=tarfile.open(name, mode)

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
# Revision 1.1  2006-10-09 14:22:35  mark
# initial check in
#
