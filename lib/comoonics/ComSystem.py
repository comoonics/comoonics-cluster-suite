"""Comoonics system module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComSystem.py,v 1.20 2010-03-29 14:14:15 marc Exp $
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


__version__ = "$Revision: 1.20 $"
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
    errormsg=kwds.get("error", "")
    if errormsg==None:
        errormsg=""

    if kwds.get("tostderr", False) != False:
        sys.stderr.write("%s" %errormsg)
        siminfo["stderr"]=errormsg
    if kwds.get("tostdout", False) != False:
        sys.stderr.write(out)
        siminfo["stdout"]=out

    if kwds.get("asstring", False) != False:
        if returncode==0:
            siminfo["return"]=out
            return out
        else:
            raise ExecLocalException(cmd, returncode, out, errormsg)
    elif kwds.get("asstring", False) == False and kwds.has_key("error"):
        return [returncode, out, errormsg]
    elif kwds.get("tostdout", False) != False:
        return returncode
    else:
        return [returncode, out]

def execLocalStatusOutput(__cmd, __output=None):
    """ 
    exec %__cmd and return output and status (rc, out).
    @param __cmd the command to be executed
    @param __output overwrite the output for this command so that it will be executed. Will only work in Simulated environment
    """
    global __EXEC_REALLY_DO
    log.debug(__cmd)
    if __EXEC_REALLY_DO == ASK:
        __ans=raw_input(__cmd+" (y*,n,c)")
        if __ans == "c":
            __EXEC_REALLY_DO=CONTINUE
        if __ans == "y" or __ans == "" or __ans == "c":
            return commands.getstatusoutput(__cmd)
        return [0,SKIPPED]
    elif isSimulate():
        return __simret(command=__cmd, output=__output)
    return commands.getstatusoutput(__cmd)


def execLocalOutput(__cmd, asstr=False, __output=None):
    """ 
    executes the given command and returns stdout output. If status is not 0 an ExecLocalExeception is thrown
    and errorcode, cmd, stdout and stderr are in that exception
    @param asstr returns out and error as string not as array of lines.
    @type asstr boolean
    @param __output overwrite the output for this command so that it will be executed. Will only work in Simulated environment
    """
    (rc, out, err)=execLocalGetResult(__cmd, True, __output)
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
        raise ExecLocalException(__cmd, rc, out, err)

def execLocalGetResult(__cmd, err=False, __output=None, __err=None):
    """ 
    exec %__cmd and returns an array ouf output lines (rc, out, err)
    @param __output overwrite the output for this command so that it will be executed. Will only work in Simulated environment
    """
    if sys.version[:3] < "2.4":
        import popen2
    else:
        import subprocess
    global __EXEC_REALLY_DO
    log.debug(__cmd)
    if __EXEC_REALLY_DO == ASK:
        __ans=raw_input(__cmd+" (y*,n,c)")
        if __ans == "c":
            __EXEC_REALLY_DO=CONTINUE
        if __ans == "n":
            if err:
                return [0, SKIPPED, ""]
            else:
                return [0, SKIPPED]
    elif isSimulate():
        if err:
            return __simret(command=__cmd, output=__output, error=__err)
        else:
            return __simret(command=__cmd, output=__output)
    if sys.version[:3] < "2.4":
        child=popen2.Popen3(__cmd, err)
        __rc=child.wait()
        __rv=child.fromchild.readlines()
        if err:
            __err=child.childerr.readlines()
            return [__rc, __rv, __err]
        return [__rc, __rv]
    else:
        p = subprocess.Popen([__cmd], shell=True, 
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                             close_fds=True)
        p.wait()
        __rc=p.returncode
        __rv=p.stdout.readlines()
        if err:
            __err=p.stderr.readlines()
            return [__rc, __rv, __err]
        return [__rc, __rv]

def execLocal(__cmd, __output=None, __error=None):
    """ 
    exec %cmd and return status output goes to sys.stdout, sys.stderr
    @param __output overwrite the output for this command so that it will be executed. Will only work in Simulated environment
    @param __error overwrite the output for this command so that it will be executed. Will only work in Simulated environment
    """
    global __EXEC_REALLY_DO
    log.debug(__cmd)
    if __EXEC_REALLY_DO == ASK:
        __ans=raw_input(__cmd+" (y*,n,c)")
        if __ans == "y" or __ans=="":
            return os.system(__cmd)
        elif __ans == "c":
            __EXEC_REALLY_DO=CONTINUE
        return 0
    elif __EXEC_REALLY_DO == SIMULATE:
        return __simret(command=__cmd, output=__output, tostdout=True, tostderr=True, error=__error)

    return os.system(__cmd)

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

    if not askExecModeCmd("%s(%s)" %(cmd.__name__, ", ".join(_tmpList))):
        return True
    else:
        return cmd(*params)

# $Log: ComSystem.py,v $
# Revision 1.20  2010-03-29 14:14:15  marc
# - added feature that simcommands will be stored in a list
#
# Revision 1.19  2009/07/22 08:37:40  marc
# fedora compliant
#
# Revision 1.18  2008/08/05 13:06:35  marc
# - added simulated output for simulated commands
#
# Revision 1.17  2008/08/04 09:17:35  marc
# - added better simulation so that you can give any method an output to be returned if simulation is on
#
# Revision 1.16  2008/03/12 09:34:42  marc
# fixed bug in execLocalOutput where when SIMULATION-Mode this function would raise an exception where it should not.
#
# Revision 1.15  2008/02/27 10:42:54  marc
# - added isSimulate() to return TRUE when simulation mode is on
#
# Revision 1.14  2007/09/18 09:23:00  marc
# changed default auf exec_really_do to unset. If not cronjobs and all automatically called jobs will fail.
#
# Revision 1.13  2007/09/07 14:46:10  marc
# - introduced set/getExecMode
# - execLocalOutput can return string
#
# Revision 1.12  2007/08/02 08:27:04  andrea2
# Added execMethod()
#
# Revision 1.11  2007/05/10 08:00:35  marc
# - better docu
#
# Revision 1.10  2007/03/26 08:36:10  marc
# - added askExecModeCmd
# - cosmetic issues and better readability
#
# Revision 1.9  2007/03/09 09:39:47  marc
# bugfix with err=False
#
# Revision 1.8  2007/03/09 09:27:58  marc
# added simulate and testing
#
# Revision 1.7  2007/02/23 12:42:43  marc
# added execLocalOutput
#
# Revision 1.6  2006/11/23 14:19:34  marc
# added continue and default y
#
# Revision 1.5  2006/10/19 10:05:14  marc
# bugfix
#
# Revision 1.4  2006/08/28 15:58:27  marc
# new comments
#
# Revision 1.3  2006/08/02 12:28:26  marc
# minor change
#
# Revision 1.2  2006/07/21 15:00:44  mark
# minor bug fixes
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.5  2006/06/28 17:24:00  mark
# bug fixes
#
# Revision 1.4  2006/06/27 11:47:07  mark
# added stderr to execLocalGetResult
#
# Revision 1.3  2006/06/26 16:55:29  mark
# added execLocalGetResult
#
# Revision 1.2  2006/06/23 11:55:14  mark
# moved Log to bottom
#
# Revision 1.1  2006/06/23 07:56:24  mark
# initial checkin (stable)
#
