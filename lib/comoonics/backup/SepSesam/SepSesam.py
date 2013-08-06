"""
Class for the SesSesam Backupcontroller.
"""
import os.path
from comoonics import ComLog, ComSystem
from comoonics.ComExceptions import ComException

class SepSesamIsNotInstalledError(ComException):
   def __str__(self):
      return "Seems as SepSesam is not installed. %s is not in place." %(self.value)

SEPSESAM_CMD="/opt/sesam/bin/sesam/sm_cmd"
class SepSesam(object):
   FULL="F"
   COPY="C"
   DIFFERENTIAL="D"
   INCREMENTAL="I"
   
   log=ComLog.getLogger("comoonics.backup.SepSesam.SepSesam")

   def __init__(self, group, client, mediapool=None, cmd=SEPSESAM_CMD):
      """ Class for Controlling the SepSesam Client """
      if not os.path.exists(cmd):
         raise SepSesamIsNotInstalledError(cmd)
      self.log.debug(".__init__(%s, %s, %s)"%(client, group))
      self.client=client
      self.group=group
      self.mediapool=mediapool
      self.level=SepSesam.FULL

   def doBackup(self, level, filename=None):
      output=""
      self.level=level
      #output=self.add_backuptask(filename=filename)
      output+=self.start_backuptask(filename)
      #output+=self.wait_for_task()
      #output+=self.delete_task()
      return output

   def doRecover(self, filename, destdir, recdir=True):
      output=self.start_restoretask()
      #output+=self.wait_for_task()
      return output

   def add_backuptask(self, filename=None):
      cmd="add task %(taskname)s -c %(client)s -j %(group)s" %(self.__dict__)
      if filename:
         cmd+=" -s %s" %filename
      return self.execute(cmd)

   def start_backuptask(self, filename=None):
      cmd="backup %(group)s -l %(level)s" %self.__dict__
      if self.mediapool:
         cmd+=" -m %s" %self.mediapool
      if filename:
         cmd+=" -s %s" %filename
      return self.execute(cmd)

   def start_restoretask(self, filename=None):
      cmd="restore -j %(group)s" %self.__dict__
      if self.mediapool:
         cmd+=" -m %s" %self.mediapool
      if filename:
         cmd+=" -s %s" %filename
      return self.execute(cmd)

   def execute(self, cmd):
      return ComSystem.execLocalOutput("%s %s" %(self.SESAM_CMD, cmd))