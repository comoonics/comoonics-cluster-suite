"""
Class for handling the backup of SepSesam
"""

from comoonics import ComLog
from comoonics.ComExceptions import ComException
from comoonics.backup.ComBackupHandler import BackupHandler

class SepSesamIsNotInstalledError(ComException):
    def __str__(self):
        return "Seems as SepSesam is not installed. %s is not in place." %(SepSesam.SepSesam.SESAM_CMD)
class EMCLegatoBackupHandlerConfigurationError(ComException):
    def __init__(self, name, value):
        ComException.__init__(self, value)
        self.name=name
    def __str__(self):
        if self.value:
            return "The parameter %s is not configured." %(self.name)
        else:
            return "The parameter %s, %s is configured wrong " %(self.name, self.value)

class SepSesamBackupHandler(BackupHandler):
	"""Backup Handler for SepSesam"""
	def __init__(self, name, properties=None):
		super(SepSesamBackupHandler,self).__init__(name, properties)
		self.name=name
        try:
            self.networker=SepSesam.SepSesam(properties.getAttribute("client"), name, 
            	properties.getAttribute("mediapool", None))
            if properties.has_key("level"):
                self.level=properties.getAttribute("level")
            else:
                self.level=SepSesam.SepSesam.FULL
        except KeyError, ke:
            raise EMCLegatoBackupHandlerConfigurationError(ke.__str__(), None)

	def __str__():
		return "SepSesamBackupHandler class name %(name)s" %self.name

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
        self.implementation.doBackup(self.level, _file)
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
        self.implementation.doBackup(self.level, cdir)
        os.chdir(olddir)

    def extractArchive(self, dest):
        """ extracts the whole archive to dest.
        @dest: destinationdirectory given as path
        """
        self.doRestore(self.name, dest, True)

    def extractFile(self, name, dest, dir=False):
        """ extracts a single file from the archive to dest.
        @name: the name of the file to be restored. If None the whole archive will be restored
        @dest: destinationdirectory given as path
        """
        self.log.debug("extractFile: extracting Archive: %s => %s" %(name, dest))
        self.implementation.doExtract(name, dest, dir)

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
