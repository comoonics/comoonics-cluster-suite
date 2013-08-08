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

   def __init__(self, group=None, job=None, client=None, mediapool=None, level=None, cmd=SEPSESAM_CMD, taskname=None):
      """ Class for Controlling the SepSesam Client """
      if not job and not group:
         raise TypeError("Either specify job or group for successfull creation of SepSesam.")
      if not cmd:
         cmd=SEPSESAM_CMD
      if not os.path.exists(cmd):
         raise SepSesamIsNotInstalledError(cmd)
      self.log.debug(".__init__(group: %s, client: %s, mediapool: %s)"%(group, client, mediapool))
      self.group=group
      self.job=job
      self.client=client
      self.mediapool=mediapool
      if level:
         self.level=level
      else:
         self.level=self.FULL
      self.cmd=cmd
      if taskname:
         self.taskname=taskname
      else:
         self.taskname=""

   def doBackup(self, level=None, filename=None, create=False):
      output=""
      if level:
         self.level=level
      if create:
         output+=self.add_backuptask(filename=filename)
      output+=self.start_backuptask(filename)
      output+=self.wait_for_task()
      if create:
         output+=self.delete_backuptask()
      return output

   def doRecover(self, filename, destdir, recdir=True):
      output=self.start_restoretask()
      #output+=self.wait_for_task()
      return output

   def start_backuptask(self, filename):
      if self.group and self.group!= "":
         return self.start_backupgroup()
      else:
         return self.start_backupjob()

   def start_backupgroup(self):
      return self.start_backup_action("-G %s" %self.group)

   def start_backupjob(self):
      return self.start_backup_action("-j %s" %self.job)

   def start_backup_action(self, action):
      cmd="backup %s %s -l %s" %(self.taskname, action, self.level)
      if self.mediapool:
         cmd+=" -m %s" %self.mediapool
      return self.execute(cmd)
 
   def wait_for_task(self):
      return ""

   def add_backuptask(self, filename=None):
      if self.group and self.group!="":
         return self.add_backuptask_group(filename)
      else:
         return self.add_backuptask_job(filename)
      
   def add_backuptask_job(self, filename=None):
      return self.add_backuptask_action("-j %s" %self.job, filename)
   def add_backuptask_group(self, filename):
      return self.add_backuptask_action("-G %s" %self.group, filename)
   def add_backuptask_action(self, action, filename):
      cmd="add task %s %s" %(self.taskname, action)
      if self.client:
         cmd+=" -c %s" %self.client
      if filename:
         cmd+=" -s %s" %filename
      return self.execute(cmd)

   def delete_backuptask(self, filename=None):
      cmd="remove task %(taskname)s" %(self.__dict__)
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
      return ComSystem.execLocalOutput("%s %s" %(self.cmd, cmd), asstr=True)