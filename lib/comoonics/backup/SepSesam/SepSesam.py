"""
Class for the SesSesam Backupcontroller.
"""
import os.path
import re
import time
from comoonics import ComLog, ComSystem
from comoonics.ComExceptions import ComException

class SepSesamIsNotInstalledError(ComException):
   def __str__(self):
      return "Seems as SepSesam is not installed. %s is not in place." %(self.value)

class SepSesamParameterError(TypeError): pass
class SepSesamOutputFormatError(TypeError): pass
class SepSesamWaitTimeoutExceeded(RuntimeError): pass

SEPSESAM_CMD="/opt/sesam/bin/sesam/sm_cmd"
class SepSesam(object):
   FULL="F"
   COPY="C"
   DIFFERENTIAL="D"
   INCREMENTAL="I"
   
   JOBID_REGEXP='STATUS=SUCCESS MSG="([^"]+)"'
   
   log=ComLog.getLogger("comoonics.backup.SepSesam.SepSesam")

   def __init__(self, group=None, client=None, mediapool=None, level=None, cmd=SEPSESAM_CMD, taskname=None, job=None,
                waittimeout=30, waitcount=0):
      """ Class for Controlling the SepSesam Client """
      if not client and not group:
         raise TypeError("Either specify client or group for successfull creation of SepSesam.")
      if not cmd:
         cmd=SEPSESAM_CMD
      if not os.path.exists(cmd):
         raise SepSesamIsNotInstalledError(cmd)
      self.log.debug(".__init__(group: %s, client: %s, mediapool: %s)"%(group, client, mediapool))
      self.group=group
      self.client=client
      self.mediapool=mediapool
      if level:
         self.level=level
      else:
         self.level=self.FULL
      self.job=job
      self.cmd=cmd
      if taskname:
         self.taskname=taskname
      else:
         self.taskname=""
      self.job=job
      self.lastoutput=""
      self.waitcount=waitcount
      self.waittimeout=waittimeout

   def doBackup(self, level=None, filename=None, create=False, reallyDo=True):
      output=""
      if level:
         self.level=level
      if not reallyDo:
         return 0, "ignored"
      if create:
         output+=self.add_backuptask(filename=filename)
      output+=self.start_backuptask(filename)
      jobid=self.get_jobid_from_cmdoutput(output)
      state,msg=self.wait_for_task(jobid=jobid, waittimeout=self.waittimeout, waitcount=self.waitcount)
      if create:
         output+=self.delete_backuptask()
      self.lastoutput=output
      # return state and message!
      return state,msg

   def doRecover(self, filename, destdir, recdir=True):
      output=self.start_restoretask()
      self.lastoutput=output
      #output+=self.wait_for_task()
      return

   def get_jobid_from_cmdoutput(self, output, matcher=None):
      """
      Expects the sm_cmd output from the lines of output begining from the end.
      Output might look as follows: 
      STATUS=SUCCESS MSG="SC20130809061320239@9DdOQVSaem6"
      The jobid will be SC20130809061320239@9DdOQVSaem6
      @param output: the output generated from the sesam commands executed before
      @matcher: the regular expression to match the output. See JOBID_REGEXP above
      @return: the jobid 
      """
      if not matcher:
         matcher=self.JOBID_REGEXP
      rlines=output.split("\n")
      rlines.reverse()
      for line in rlines:
         match=re.match(matcher, line)
         if match:
            return match.group(1)
      raise SepSesamOutputFormatError("The output format of the command cannot be parsed for a valid job id.")

   def start_backuptask(self, filename):
      if self.group and self.group!= "":
         return self.start_backupgroup()
      else:
         return self.start_backupjob()

   def start_backupgroup(self):
      return self.start_backup_action("-G %s" %self.group)

   def start_backupjob(self):
      return self.start_backup_action()

   def start_backup_action(self, action=""):
      cmd="backup %s %s -l %s" %(self.taskname, action, self.level)
      if self.job:
         cmd+=" -j %s" %self.job
      if self.mediapool:
         cmd+=" -m %s" %self.mediapool
      return self.execute(cmd)
 
   def wait_for_task(self, jobid, waittimeout=30, waitcount=0):
      """
      Scans the logs (results) tables for this job to be completed.
      This method will block until checkamount checks have been made or a log is found.
      sleeptimeout*checkamount is the maximum time to stay in this method.
      If checkamount is 0 (default) it will wait forever until a log is found for this job.
      @param jobid: the jobid for the job in question.
      @param waittimeout: how many seconds to wait between log checks.
      @param waitcount: how often to check for logs. 
      @raise SepSesamWaitTimeoutExceeded: if the wait timeout has been exceeded.
      @return: (state, msg) of the job. msg is a string informing about the result and state an 
               integer (0=success, failure otherwise) 
      """
      count=0
      sqlquery="select state,msg from results where saveset='"+jobid+"'"
      while waitcount==0 or count<waitcount:
         try:
            state,msg=self.sql(sqlquery)
            state=int(state)
            return state,msg
         except ValueError:
            pass
         time.sleep(waittimeout)
         count+=1
      raise SepSesamWaitTimeoutExceeded("SepSesam timeout to wait for job %s to completed exceeded. Timeout: %s, Count: %s." 
                                        %(jobid, waittimeout, waitcount))

   def add_backuptask(self, filename=None):
      if self.group and self.group!="":
         return self.add_backuptask_group(filename)
      else:
         return self.add_backuptask_client(filename)
      
   def add_backuptask_group(self, filename):
      return self.add_backuptask_action("-G %s" %self.group, filename)
   def add_backuptask_client(self, filename):
      return self.add_backuptask_action("", filename)
   def add_backuptask_action(self, action, filename):
      cmd="add task %s %s" %(self.taskname, action)
      if self.client:
         cmd+=" -c %s" %self.client
      if self.job:
         cmd+=" -j %s" %self.job
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

   def sql(self, sqlquery, outputformat="noheader", outputdelim=";"):
      return self.execute("sql \"%s\" -F %s -d '%s'" %(sqlquery, outputformat, outputdelim)).split(outputdelim)

   def execute(self, cmd):
      return ComSystem.execLocalOutput("%s %s" %(self.cmd, cmd), asstr=True)
