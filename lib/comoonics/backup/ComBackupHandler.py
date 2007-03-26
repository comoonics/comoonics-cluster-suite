"""
Class for the BackupHandlerImplementation.
Derives everything from ComArchiv->ArchivHandler. But perhaps in Future some specific Backupmethods are neccesary.
"""
# here is some internal information
# $Id: ComBackupHandler.py,v 1.1 2007-03-26 07:48:58 marc Exp $
#


from comoonics import ComLog
from comoonics.ComArchive import ArchiveHandler, NotImplementedError

class BackupHandler(ArchiveHandler):
    """
    Class for the handling of backup applications
    """
    log=ComLog.getLogger("BackupHandler")
    TYPE="backup"

    def __init__(self, name, properties=None):
        super(BackupHandler, self).__init__(name, properties)

    def closeAll(self):
        pass

    def hasMember(self, name):
        ''' checks wether archive hosts member file
            returns True/False
        '''
        raise NotImplementedError

    def extractFile(self, name, dest):
        ''' extracts a file or dirctory from archiv'''
        raise NotImplementedError

    def getFileObj(self, name):
        ''' returns a fileobject of an archiv member '''
        raise NotImplementedError

    def addFile(self, name, arcname=None,recursive=True):
        ''' adds a file or directory to archiv'''
        raise NotImplementedError

    def createArchive(self, source, cdir=None):
        ''' creates an archive from the whole source tree
            stays in the same filesystem
            @source: is the sourcedirectory to copy from
            @cdir:   is a chdir directory to change to
         '''
#        try:
#            os.mkdir(self.path+"/"+os.path.dirname(cdir))
#        except: pass
        raise NotImplementedError

########################
# $Log: ComBackupHandler.py,v $
# Revision 1.1  2007-03-26 07:48:58  marc
# initial revision
#
