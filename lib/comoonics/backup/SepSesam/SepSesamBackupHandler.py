"""
Class for handling the backup of SepSesam
"""

from comoonics import ComLog
from comoonics.ComProperties import Properties
from comoonics.ComExceptions import ComException
from comoonics.backup.ComBackupHandler import BackupHandler
from SepSesam import SepSesam
import os.path
import tempfile

class SepSesamHandlerConfigurationError(ComException):
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
   FORMAT="sepsesam"
   TYPE="backup"
   def __init__(self, name, properties=None):
      if not properties:
         properties=Properties()
      super(SepSesamBackupHandler,self).__init__(name, properties)
      try:
         self.implementation=SepSesam(client=self.properties.get("client", None).getValue(), taskname=self.name, 
                                      group= self.properties.get("group", None).getValue(),
                                      mediapool=self.properties.get("mediapool", None).getValue(),
                                      level=self.properties.get("level", None).getValue(),
                                      job=self.properties.get("job", None).getValue(), 
                                      cmd=self.properties.get("cmd", None).getValue())
      except KeyError, ke:
         raise SepSesamHandlerConfigurationError(ke.__str__(), None)

   def __str__(self):
      return "SepSesamBackupHandler class name %s" %self.name
         
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
      budir=os.path.dirname(name)
      self.log.debug("addFile changing to directory: %s" %(budir))
      os.chdir(budir)
      (_path, _name)=os.path.split(arcname)
      if not _path or _path == "":
         _path="metadata"
      #created=False
      if not os.path.exists(_path):
      #   created=True
         os.makedirs(_path)
      _file=os.path.join(_path, _name)
      self.log.debug("addFile: copy %s => %s" %(name, _file))
      shutil.copy(name, _file)
      self.implementation.doBackup(self.level, _file)
#        os.unlink(_file)
#        if created:
#            os.unlink(os.path.dirname(_file))
      os.chdir(olddir)
      
   def createArchive(self, source, cdir=None, create=False):
      ''' 
      creates an archive from the whole source tree
      stays in the same filesystem
      @source: is the sourcedirectory to copy from
      @cdir:   is a chdir directory to change to
      @create: create the backup job if it not already exists. Default don't create.
      '''
      olddir=os.getcwd()
      if cdir and os.path.exists(cdir):
         self.log.debug("createArchive(changing to: %s)" %(cdir))
         os.chdir(cdir)
      self.log.debug("createArchive(%s, %s)" %(source, cdir))
      output=self.implementation.doBackup(filename=source, create=create)
      os.chdir(olddir)
      return output
      
   def extractArchive(self, dest):
      """ extracts the whole archive to dest.
      @dest: destinationdirectory given as path
      """
      self.doRestore(self.name, dest, True)

   def extractFile(self, name, dest, budir=False):
      """ extracts a single file from the archive to dest.
      @name: the name of the file to be restored. If None the whole archive will be restored
      @dest: destinationdirectory given as path
      """
      self.log.debug("extractFile: extracting Archive: %s => %s" %(name, dest))
      self.implementation.doExtract(name, dest, budir)

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
