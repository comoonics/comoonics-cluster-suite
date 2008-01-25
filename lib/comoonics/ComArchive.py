"""Comoonics archive module


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id $
#


__version__ = "$Revision: 1.14 $"
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

from exceptions import ImportError

__all__ = ["Archive", "ArchiveHandlerFactory", "ArchiveHandler"]

class NotImplementedError(ComException): pass

class ArchiveException(ComException):pass

class Archive(DataObject):
    log=ComLog.getLogger("comoonics.ComArchive.Archive")
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
        super(Archive, self).__init__(element, doc)
        Archive.log.debug("getArchiveHandler(%s, %s, %s, %s, %s)" %(self.getAttribute("name"), self.getAttribute("format"), \
             self.getAttribute("type"), self.getAttribute("compression", default="none"), self.getProperties()))
        self.ahandler=ArchiveHandlerFactory.getArchiveHandler \
            (self.getAttribute("name"), self.getAttribute("format"), \
             self.getAttribute("type"), self.getAttribute("compression", default="none"), self.getProperties())
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
            ComLog.debugTraceLog(Archive.log)
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
        Archive.log.debug("createArchive(%s, %s)" % (source, cdir))
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
class ArchiveHandler(object):
    ''' Baseclass for archiv handlers'''
    NONE="none"

    FORMAT=NONE
    COMPRESSION=NONE
    TYPE=NONE

    __logStrLevel__ = "ArchiveHandler"

    def __init__(self, name, properties=None):
        self.name=name
        self.properties=properties

    def closeAll(self):
        pass

    def getProperties(self):
        return self.properties

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
        raise NotImplementedError()

'''
Archivee Handlers
'''


''' ArchiveeHandler for tar files '''
class TarArchiveHandler(ArchiveHandler):
    FORMAT="tar"
    TYPE="file"
    TAR="/bin/tar"

    def __init__(self, name, properties=None):
        super(TarArchiveHandler, self).__init__(name, properties)
        self.tarfile=name
        self.compression=""
        self.compressionmode=""

    def getCommandOptions(self):
        """
        Returns the options for the tar command and also the supported options. Xattrs, selinux, acls
        """
        _opts=[]

        if self.getProperties():
            for _property in self.getProperties().keys():
                _value=self.getProperties()[_property].getValue()
                if _value=="":
                    if len(_property)==1:
                        _opts.append("-%s" %_property)
                    else:
                        _opts.append("--%s" %_property)
                else:
                    if len(_property)==1:
                        _opts.append("-%s %s" %(_property, _value))
                    else:
                        _opts.append("--%s %s" %(_property, _value))
        return _opts

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
        __cmd = TarArchiveHandler.TAR +" ".join(self.getCommandOptions())+" -x " + self.compression + " -f " \
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
        __cmd = TarArchiveHandler.TAR +" ".join(self.getCommandOptions())+" -c --one-file-system " + self.compression + " -f " \
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
    COMPRESSION="gzip"
    def __init__(self, name, properties=None):
        TarArchiveHandler.__init__(self, name, properties)
        self.compression="-z "
        self.compressionmode=":gz"


''' Archivee Handler for bzip2 compressed tar files '''
class TarBz2ArchiveHandler(TarArchiveHandler):
    COMPRESSION="bz2"
    def __init__(self, name, properties=None):
        TarArchiveHandler.__init__(self, name, properties)
        self.compression="-j "
        self.compressionmode=":bz2"


''' Simple Archive Handler - uses local file system '''
class SimpleArchiveHandler(ArchiveHandler):
    FORMAT="simple"
    TYPE="file"
    def __init__(self, name, properties=None):
        ArchiveHandler.__init__(self, name, properties)
        self.path="/tmp/" + name
        if os.path.exists(self.path) and not os.path.isdir(self.path):
            raise ArchiveException("Path %s already exists" %(self.path))

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
            Archive.log.debug("open(%s)" %(self.path+"/"+name))
            file = open(self.path+"/"+name, "r")
        except:
            raise ArchiveException("Cannot open %s." %(self.path+"/"+name))
        return file

    def addFile(self, name, arcname=None,recursive=True):
        ''' adds a file or directory to archiv'''
        try:
            os.mkdir(self.path+"/"+os.path.dirname(name))
        except: pass
        shutil.copy2(name, self.path+"/"+arcname)

    def createArchive(self, source, cdir=None):
        ''' creates an archive from the whole source tree
            stays in the same filesystem
            @source: is the sourcedirectory to copy from
            @cdir:   is a chdir directory to change to
         '''
#        try:
#            os.mkdir(self.path+"/"+os.path.dirname(cdir))
#        except: pass
        if cdir !=None:
            Archive.log.debug("changing to directory "+cdir)
            os.chdir(cdir)
        Archive.log.debug("Copy from "+source+" to "+self.path+"/")
        shutil.copytree(source, self.path+"/")


class IncompatibleArchiveHandlerClass(ComException):
    def __str__(self):
        return "The Class "+self.value+" is incompatible to register to ArchiveHandlerFactory"

''' Factory class for ArchiveHandler '''
class ArchiveHandlerFactoryClass:
    """
    Factory for different archiv type handlers
    """

    '''
    Internal Exception classes
    '''

    __logStrLevel__ = "ArchiveHandlerFactory"
    log=ComLog.getLogger("comoonics.ComArchive.ArchiveHandlerFactory")

    """ The static registry for all registered handlers """
    _registry=dict()

    def __init__(self):
        """
        Default contstructor that preregisters all default classes
        """
        self.registerArchiveHandler(SimpleArchiveHandler)
        self.registerArchiveHandler(TarArchiveHandler)
        self.registerArchiveHandler(TarGzArchiveHandler)
        self.registerArchiveHandler(TarBz2ArchiveHandler)

    def registerArchiveHandler(self, theclass):

        if type(theclass)!=type:
            raise IncompatibleArchiveHandlerClass(theclass)
        instance=object.__new__(theclass)
        if not isinstance(instance, ArchiveHandler):
            raise IncompatibleArchiveHandlerClass(theclass)
        #self.log.debug("ComArchive.registerArchiveHandler(%s)" %(theclass))
        element=theclass
        if not self._registry.has_key(theclass.FORMAT):
            self._registry[theclass.FORMAT]=dict()
        if not self._registry[theclass.FORMAT].has_key(theclass.TYPE):
            self._registry[theclass.FORMAT][theclass.TYPE]=dict()
        self._registry[theclass.FORMAT][theclass.TYPE][theclass.COMPRESSION]=theclass

    def getArchiveHandler(self, name, format, thetype=ArchiveHandler.NONE, compression=ArchiveHandler.NONE, properties=None):
        """
        Returns the handler registered for the given format and type combination
        """
        if self._registry.has_key(format) and \
           self._registry[format].has_key(thetype) and \
           self._registry[format][thetype].has_key(compression):
            instance=object.__new__(self._registry[format][thetype][compression])
            instance.__init__(name, properties)
            return instance
        else:
            raise ArchiveException("No ArchiveHandler found for %s, %s, %s, %s" %(name, format, thetype, compression))

    def __str__(self):
        return "%s" %(self._registry)
"""
The ArchiveHandlerFactory
Concept:
Is a static reference to ArchiveHandlerFactoryClass that holds registered ArchiveImplementations.
Every Implementation registers with a formatname and other optional Parameters like i.e. compression or type.
By default the following implementations are registered:
format      compression          Class
simple      "none"/None          SimpleArchiveHandler
tar         "none"/None          TarArchiveHandler
tar         "gzip"               TarGzArchiveHandler
tar         "bz2"                TarBz2ArchiveHandler

otherwise it raises an ArchiveException("No ArchiveHandler found for %s" %(format))

New handler should best register in their automatically executed __init__.py Module of their module
with given format, [type] and [compression] if needed.. I.e.
__init.py__:
ArchiveHandler.registerArchiveHandler(handlerClass)
format, type, compression are defined in the class itself over the static attributes:
FORMAT, TYPE, COMPRESSION
all default to NONE
"""
global ArchiveHandlerFactory
ArchiveHandlerFactory=ArchiveHandlerFactoryClass()

"""
Testing starts here
"""
class myTarArchiveHandler(TarArchiveHandler):
    FORMAT="testformat"
    TYPE="testtype"
    pass
class myTarBz2ArchiveHandler(TarBz2ArchiveHandler):
    FORMAT="testformat"
    TYPE="testtype"
    pass
class myTarGzArchiveHandler(TarGzArchiveHandler):
    FORMAT="testformat"
    TYPE="testtype"
    pass

def __TestRegisterArchiveHandler(theclass):
    print "Registering class: %s" %(theclass)
    ArchiveHandlerFactory.registerArchiveHandler(theclass)
    print "registry: %s" %(ArchiveHandlerFactory)

def __TestRetreiveArchiveHandler(theclass):
    print "Retreiving data: %s, %s, %s" %(theclass.FORMAT, theclass.TYPE, theclass.COMPRESSION)
    print ArchiveHandlerFactory.getArchiveHandler("testname", theclass.FORMAT, theclass.TYPE, theclass.COMPRESSION)

def main():
    print "Testing ArchivHandlerFactory"
    print "Registry: "
    print ArchiveHandlerFactory
    __TestRegisterArchiveHandler(myTarArchiveHandler)
    __TestRegisterArchiveHandler(myTarGzArchiveHandler)
    __TestRegisterArchiveHandler(myTarBz2ArchiveHandler)

    print "Retreiving data from registry:"
    __TestRetreiveArchiveHandler(myTarArchiveHandler)
    __TestRetreiveArchiveHandler(myTarGzArchiveHandler)
    __TestRetreiveArchiveHandler(myTarBz2ArchiveHandler)
    __TestRetreiveArchiveHandler(SimpleArchiveHandler)

if __name__ == '__main__':
    main()

##################
# $Log: ComArchive.py,v $
# Revision 1.14  2008-01-25 14:08:36  marc
# - Fix BUG#191 so that options might be given via properties (2nd)
#
# Revision 1.13  2008/01/25 13:06:58  marc
# - Fix BUG#191 so that options might be given via properties
#
# Revision 1.12  2008/01/25 10:31:55  marc
# - BUG#191 removed ACL support as it does not work so easily
#
# Revision 1.11  2008/01/24 10:07:54  marc
# bugfix for 189
# - added options for rsync so that acls and xattrs will also be synced.
#
# Revision 1.10  2007/09/07 14:44:16  marc
# - logging
# - replaced taroption -l with --one-filesystem which is upword compatible
#
# Revision 1.9  2007/03/26 08:18:09  marc
# - added some autotests
# - added 3 tier hierarchy for ArchiveHandlers (format, type, compression)
# - added more generic handling of ArchiveHandlers (register to a static registry)
#
# Revision 1.8  2007/03/08 10:54:05  marc
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
