"""
Class for the EMC-Legator BackupHandlerImplementation.
"""
# here is some internal information
# $Id: ComEMCLegatoBackupHandler.py,v 1.1 2007-03-26 07:48:58 marc Exp $
#


from comoonics import ComLog
from comoonics.ComExceptions import ComException
from comoonics.backup.ComBackupHandler import BackupHandler
from ComEMCLegatoNetworker import LegatoNetworker, LegatoBackupLevel

from exceptions import KeyError

LEGATO_CMD="/usr/sbin/savefs"

class EMCLegatoBackupLevel(object):
    FULL="full"
    SKIP="skip"
    INCR="incr"
    ONE="1"
    TWO="2"
    THREE="3"
    FOUR="4"
    FIVE="5"
    SIX="6"
    SEVEN="7"
    EIGHT="8"
    NINE="9"

class EMCLegatoIsNotInstalledError(ComException):
    def __str__(self):
        return "Seems as EMC Legato is not installed %s is not in place." %(LEGATO_CMD)
class EMCLegatoBackupHandlerConfigurationError(ComException):
    def __init__(self, name, value):
        ComException.__init__(self, value)
        self.name=name
    def __str__(self):
        if self.value:
            return "The parameter %s is not configured." %(self.name)
        else:
            return "The parameter %s, %s is configured wrong " %(self.name, self.value)

class EMCLegatoBackupHandler(BackupHandler):
    """
    Class for the handling of backup applications
    """
    log=ComLog.getLogger("EMCLegatoBackupHandler")
    FORMAT="legato"

    def __init__(self, name, properties):
        """
        Initializes a new EMCLegatoBackupHandler from the given name
        @name:    is the group to be used
        Within the properties the following keys have to be present:
        @client:  which client is to be backuped
        @level:   which backuplevel
        """
        super(EMCLegatoBackupHandler, self).__init__(name, properties)
        self.networker=None
        try:
            self.networker=LegatoNetworker(properties.getAttribute("client"), name, properties.getAttribute("server"))
            self.level=properties.getAttribute("level")
        except KeyError, ke:
            raise EMCLegatoBackupHandlerConfigurationError(ke.__str__(), None)

    def addFile(self, name, arcname=None,recursive=True):
        '''
        adds a file or directory to archiv
        @name:       the name of the sourcefile
        @arcname:    the name of the file to archive this one
        @recursive:  should we archive this one recursively (not working!!!)
        '''
        import os
        import os.path
        import shutil
        olddir=os.getcwd()
        self.log.debug("addFile(%s, %s)" %(name, arcname))
        dir=os.path.dirname(name)
        self.log.debug("addFile changing to directory: %s" %(dir))
        os.chdir(dir)
        newfile="metadata"
        created=False
        if not os.path.exists(newfile):
            created=True
            os.mkdir(newfile)
        newfile+="/"+arcname
        self.log.debug("addFile: copy %s => %s" %(name, newfile))
        shutil.copy(name, newfile)
        self.networker.executeSaveFs(self.level, newfile)
#        os.unlink(newfile)
#        if created:
#            os.unlink(os.path.dirname(newfile))
        os.chdir(olddir)

    def createArchive(self, source, cdir=None):
        ''' creates an archive from the whole source tree
            stays in the same filesystem
            @source: is the sourcedirectory to copy from
            @cdir:   is a chdir directory to change to
         '''
        import os
        import os.path
        olddir=os.getcwd()
        if cdir and os.path.exists(cdir):
            self.log.debug("createArchive(changing to: %s)" %(cdir))
            os.chdir(cdir)
        self.log.debug("createArchive(%s, %s)" %(source, cdir))
        self.networker.executeSaveFs(self.level, source)
        os.chdir(olddir)

########################
# $Log: ComEMCLegatoBackupHandler.py,v $
# Revision 1.1  2007-03-26 07:48:58  marc
# initial revision
#
