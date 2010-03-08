"""
Class for the EMC-Legator BackupHandlerImplementation.
"""
# here is some internal information
# $Id: ComEMCLegatoBackupHandler.py,v 1.6 2010-03-08 12:30:48 marc Exp $
#

import os.path
import tempfile

from comoonics import ComLog
from comoonics.ComExceptions import ComException
from comoonics.backup.ComBackupHandler import BackupHandler
from ComEMCLegatoNetworker import LegatoNetworker

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
    log=ComLog.getLogger("comoonics.backup.EMCLegato.EMCLegatoBackupHandler")
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
        self.openfiles=list()
        try:
            self.networker=LegatoNetworker(properties.getAttribute("client"), name, properties.getAttribute("server"))
            self.level=EMCLegatoBackupLevel.FULL
            if properties.has_key("level"):
                self.level=properties.getAttribute("level")
        except KeyError, ke:
            raise EMCLegatoBackupHandlerConfigurationError(ke.__str__(), None)

    def addFile(self, name, arcname=None,recursive=True):
        '''
        adds a file or directory to archiv
        If @arcname has no pathpart a metadata basedir is added.
        @name:       the name of the sourcefile
        @arcname:    the name of the file to archive this one
        @recursive:  should we archive this one recursively (not working!!!)
        '''
        import shutil
        olddir=os.getcwd()
        self.log.debug("addFile(%s, %s)" %(name, arcname))
        dir=os.path.dirname(name)
        self.log.debug("addFile changing to directory: %s" %(dir))
        os.chdir(dir)
        (_path, _name)=os.path.split(arcname)
        if not _path or _path == "":
            _path="metadata"
        created=False
        if not os.path.exists(_path):
            created=True
            os.makedirs(_path)
        _file=os.path.join(_path, _name)
        self.log.debug("addFile: copy %s => %s" %(name, _file))
        shutil.copy(name, _file)
        self.networker.executeSaveFs(self.level, _file)
#        os.unlink(_file)
#        if created:
#            os.unlink(os.path.dirname(_file))
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
        self.networker.executeSaveFs(self.level, cdir)
        os.chdir(olddir)

    def extractArchive(self, dest):
        """ extracts the whole archive to dest.
        @dest: destinationdirectory given as path
        """
        # for legato we need to cut the last part. no we don't we do it different. See LegateNetworker
        #_dest=os.path.dirname(os.path.normpath(dest))
        self.extractFile(self.name, dest, True)

    def extractFile(self, name, dest, dir=False):
        """ extracts a single file from the archive to dest.
        @name: the name of the file to be restored. If None the whole archive will be restored
        @dest: destinationdirectory given as path
        """
        self.log.debug("extractFile: extracting Archive: %s => %s" %(name, dest))
        self.networker.executeRecover(name, dest, dir)

    def getFileObj(self, name):
        ''' returns a fileobject of an archiv member '''
        self.tmppath=tempfile.mkdtemp()
        path=os.path.normpath("%s/%s" %(self.name, name))
        self.log.debug("getFileObj(%s)=>%s" %(path, self.tmppath))
        self.extractFile(path, self.tmppath)
        filename=os.path.normpath("%s/%s" %(self.tmppath, os.path.basename(name)))
        filep=open(filename)
        self.openfiles.append(filename)
        return filep

    def closeAll(self):
        for filename in self.openfiles:
            if os.path.exists(filename):
                os.unlink(filename)
        if os.path.exists(self.tmppath):
            os.rmdir(self.tmppath)

########################
# $Log: ComEMCLegatoBackupHandler.py,v $
# Revision 1.6  2010-03-08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.5  2007/07/31 10:02:54  marc
# small fix in outputting
#
# Revision 1.4  2007/07/10 11:31:54  marc
# MMG Support
#
# MMG Backup Legato Integration
#
# Revision 1.3  2007/06/13 09:00:00  marc
# - now backuping full path to support incremental backups
#
# Revision 1.2  2007/04/04 12:46:30  marc
# MMG Backup Legato Integration:
# - added restoreMethods (extractArchive, getFileobj, extractFile)
#
# Revision 1.1  2007/03/26 07:48:58  marc
# initial revision
#
