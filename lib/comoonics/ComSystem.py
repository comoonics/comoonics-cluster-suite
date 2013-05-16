"""Comoonics system module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComSystem.py,v 1.23 2010-11-21 21:48:19 marc Exp $
#
# @(#)$File$
#
# Copyright (c) 2001 ATIX GmbH, 2007 ATIX AG.
# Einsteinstrasse 10, 85716 Unterschleissheim, Germany
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


__version__ = "$Revision: 1.23 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ComSystem.py,v $

import sys
import commands
import os

import ComLog

from comoonics.ComExceptions import ComException

SIMULATE="simulate"
ASK="ask"
SKIPPED="skipped"
CONTINUE="continue"

class ExecLocalException(ComException):
   """ Exception throw if command fails. Attributes are
     @cmd: the command executed
     @rc:  the status code (!=0)
     @out: the output to stdout
     @err: the output to stderr
   """
   def __init__(self, cmd, rc, out, err):
      self.cmd=cmd
      self.rc=rc
      self.out=out
      self.err=err
   def __str__(self):
      return """cmd=%s, errorcode=%s
output:
%s
error:
%s
""" %(self.cmd, self.rc, self.out, self.err)

__EXEC_REALLY_DO = None
log=ComLog.getLogger("ComSystem")
simcmds=list()
siminfo=dict()
def clearSimCommands():
   """
   Resets all stored simcommands
   """
   global simcmds
   global siminfo
   simcmds=list()
   siminfo=dict()

def getSimCommands():
   """
   Returns all commands being simulated
   """
   global simcmds
   return simcmds
   
def getSimInfo():
   """
   Returns information on all simulated cmds
   @return: A map of simulated returncodes and the like. Attributes are "stdout", "stderr", "return". Default is None for no information.
   @rtype: L{dict}
   """
   global siminfo
   return siminfo

def setExecMode(mode):
   """ set the mode for system execution """
   global __EXEC_REALLY_DO
   __EXEC_REALLY_DO=mode
def getExecMode():
   """ returns the mode for system execution """
   return __EXEC_REALLY_DO
def isSimulate():
   """ You'll often want this """
   return __EXEC_REALLY_DO == SIMULATE

def askExecModeCmd(__cmd):
   global __EXEC_REALLY_DO
   if __EXEC_REALLY_DO == ASK:
      __ans=raw_input(__cmd+" (y*,n,c)")
      if __ans == "c":
         __EXEC_REALLY_DO=CONTINUE
      if __ans == "y" or __ans == "" or __ans=="c":
         return True
      return False
   elif isSimulate():
      log.info("SIMULATE: "+__cmd)
      simcmds.append(__cmd)
      siminfo[__cmd]=None
      return False
   return True

def __simret(**kwds):
   cmd=kwds["command"]
   log.info("SIMULATE: "+ cmd)
   simcmds.append(cmd)
   returncode=kwds.get("returncode", 0)
   siminfo["return"]=returncode
   out=kwds.get("output", SKIPPED)
   if out == None:
      out=SKIPPED
   errormsg=kwds.get("error", None)
   if errormsg and kwds.get("tostderr", False) != False:
      sys.stderr.write("%s" %errormsg)
      siminfo["stderr"]=errormsg
   if out and kwds.get("tostdout", False) != False:
      sys.stderr.write(out)
      siminfo["stdout"]=out

   if kwds.get("asstring", False) == False and type(out) != list and kwds.get("tostdout", False) == False:
      out=[out]

   if kwds.get("asstring", False) == False and kwds.get("tostderr", False) == False and kwds.get("tostderr", False) == False and errormsg and errormsg != "":
      if errormsg == True:
         errormsg=[ "" ]
      if type(errormsg) != list:
         errormsg=[errormsg]
      return [returncode, out, errormsg]
   elif kwds.get("asstring", False) == False and kwds.get("tostderr", False) != False and kwds.get("tostdout", False) != False:
      if returncode==0:
         siminfo["return"]=out
         return returncode
      else:
         raise ExecLocalException(cmd, returncode, out, errormsg)
   elif kwds.get("tostdout", False) != False:
      return returncode
   elif errormsg == None:
      return [returncode, out]
   else:
      return [returncode, out, errormsg]

def execLocalStatusOutput(cmd, output=None, rc=0):
   """ 
   exec %__cmd and return output and status (rc, out).
   @param __cmd the command to be executed
   @param __output overwrite the output for this command so that it will be executed. Will only work in Simulated environment
   """
   global __EXEC_REALLY_DO
   log.debug(cmd)
   if not output:
      output=""
   if __EXEC_REALLY_DO == ASK:
      ans=raw_input(cmd+" (y*,n,c)")
      if ans == "c":
         __EXEC_REALLY_DO=CONTINUE
      if ans == "y" or ans == "" or ans == "c":
         (rc, ret)=commands.getstatusoutput(cmd)
      (rc, ret)=(0,SKIPPED)
   elif isSimulate():
      ret=output
   else:
      (rc, ret)=commands.getstatusoutput(cmd)
   return (rc, unicode(ret, "utf-8"))


def execLocalOutput(cmd, asstr=False, output=None):
   """ 
   executes the given command and returns stdout output. If status is not 0 an ExecLocalExeception is thrown
   and errorcode, cmd, stdout and stderr are in that exception
   @param asstr returns out and error as string not as array of lines.
   @type asstr boolean
   @param __output overwrite the output for this command so that it will be executed. Will only work in Simulated environment
   """
   (rc, out, err)=execLocalGetResult(cmd, True, output)
   if asstr:
      if type(out) == list:
         out="".join(out)
      if not err:
         err=err
      else:
         err="".join(err)
   if rc==0:
      return out
   else:
      raise ExecLocalException(cmd, rc, out, err)

def execLocalGetResult(cmd, err=False, output=None, errmsg=None):
   """ 
   exec cmd and returns an array ouf output lines either (rc, out, err) or (rc, out) dependent on if err or not.
   @param output overwrite the output for this command so that it will be executed. Will only work in Simulated environment
   """
   global __EXEC_REALLY_DO
   log.debug(cmd)
   if __EXEC_REALLY_DO == ASK:
      ans=raw_input(cmd+" (y*,n,c)")
      if ans == "c":
         __EXEC_REALLY_DO=CONTINUE
      if ans == "n":
         if err:
            return [0, SKIPPED, ""]
         else:
            return [0, SKIPPED]
   elif isSimulate():
      if not err:
         err=errmsg
      if err==True and errmsg==None:
         errmsg=""
      return __simret(command=cmd, output=output, error=errmsg, tostderr=False, tostdout=False, asstring=False)
   if sys.version[:3] < "2.4":
      import popen2
      child=popen2.Popen3(cmd, err)
      rc=child.wait()
      rv=map(lambda line: unicode(line, "utf-8"), child.fromchild.readlines())
      if err:
         errmsg=map(lambda line: unicode(line, "utf-8"), child.childerr.readlines())
         return [rc, rv, errmsg]
      return [rc, rv]
   else:
      import subprocess
      p = subprocess.Popen([cmd], shell=True, 
                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                      close_fds=True)
      p.wait()
      rc=p.returncode
      rv=map(lambda line: unicode(line, "utf-8"), p.stdout.readlines())
      if err:
         errmsg=map(lambda line: unicode(line, "utf-8"), p.stderr.readlines())
         return [rc, rv, errmsg]
      return [rc, rv]

def execLocal(cmd, output=None, error=None):
   """ 
   exec %cmd and return status output goes to sys.stdout, sys.stderr
   @param output overwrite the output for this command so that it will be executed. Will only work in Simulated environment
   @param error overwrite the output for this command so that it will be executed. Will only work in Simulated environment
   """
   global __EXEC_REALLY_DO
   log.debug(cmd)
   if __EXEC_REALLY_DO == ASK:
      ans=raw_input(cmd+" (y*,n,c)")
      if ans == "y" or ans=="":
         return os.system(cmd)
      elif ans == "c":
         __EXEC_REALLY_DO=CONTINUE
      return 0
   elif isSimulate():
      return __simret(command=cmd, output=output, asstring=False, tostdout=True, tostderr=True, error=error)
   else:
      return os.system(cmd)

def execMethod(cmd, *params):
   """
   Executes the given cmd by considering variable L{__EXEC_REALLY_DO}
   (decide if command should be simulated, executed, ignored or ask
   for behaviour)
   @param cmd: function to execute
   @type cmd: function
   @param params: params of function as tuple
   @type params: tuple
   @return: return value of function, if no function is called return 0
   @rtype: depends on return type of called function, if no function is called L{int}
   """
   _tmpList = []
   for i in params:
      if type(i).__name__ == "str" or type(i).__name__ == "unicode":
         _tmpList.append(i)
      else:
         _tmpList.append(type(i).__name__)

   if not isSimulate() and not askExecModeCmd("%s(%s)" %(cmd.__name__, ", ".join(_tmpList))):
      return True
   elif isSimulate():
      return __simret(command="%s(%s)" %(cmd.__name__, ", ".join(_tmpList)), output="%s(%s)" %(cmd.__name__, ", ".join(_tmpList)), asstring=True, tostdout=True, tostderr=True, returncode=True)
   else:
      return cmd(*params)
