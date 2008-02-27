"""Comoonics system module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComSystem.py,v 1.15 2008-02-27 10:42:54 marc Exp $
#


__version__ = "$Revision: 1.15 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ComSystem.py,v $

import sys
import commands
import os
import popen2

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
    elif __EXEC_REALLY_DO == SIMULATE:
        log.info("SIMULATE: "+__cmd)
        return False
    return True

def execLocalStatusOutput(__cmd):
    """ exec %__cmd and return output and status (rc, out)"""
    global __EXEC_REALLY_DO
    log.debug(__cmd)
    if __EXEC_REALLY_DO == ASK:
        __ans=raw_input(__cmd+" (y*,n,c)")
        if __ans == "c":
            __EXEC_REALLY_DO=CONTINUE
        if __ans == "y" or __ans == "" or __ans == "c":
            return commands.getstatusoutput(__cmd)
        return [0,SKIPPED]
    elif __EXEC_REALLY_DO == SIMULATE:
        log.info("SIMULATE: "+__cmd)
        return [0,SKIPPED]
    return commands.getstatusoutput(__cmd)


def execLocalOutput(__cmd, asstr=False):
    """ executes the given command and returns stdout output. If status is not 0 an ExecLocalExeception is thrown
        and errorcode, cmd, stdout and stderr are in that exception
        @asstr returns out and error as string not as array of lines.
    """
    (rc, out, err)=execLocalGetResult(__cmd, True)
    if asstr:
        out="".join(out)
        err="".join(err)
    if rc==0:
        return out
    else:
        raise ExecLocalException(__cmd, rc, out, err)

def execLocalGetResult(__cmd, err=False):
    """ exec %__cmd and returns an array ouf output lines (rc, out, err)"""
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
    elif __EXEC_REALLY_DO == SIMULATE:
        log.info("SIMULATE: "+__cmd)
        if err:
            return [0,SKIPPED, None]
        else:
            return [0, SKIPPED]
    child=popen2.Popen3(__cmd, err)
    __rc=child.wait()
    __rv=child.fromchild.readlines()
    if err:
        __err=child.childerr.readlines()
        return [__rc, __rv, __err]
    return [__rc, __rv]


def execLocal(__cmd):
    """ exec %cmd and return status output goes to sys.stdout, sys.stderr"""
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
        log.info("SIMULATE: "+__cmd)
        return 0

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
        return 0
    else:
        return cmd(*params)

def test(level):
    global __EXEC_REALLY_DO
    __EXEC_REALLY_DO=level
    cmd1='echo "hallo stdout"'
    cmd2='echo "hallo stderr" >&2'

    print execLocalOutput(cmd1)
    print execLocalStatusOutput(cmd1)
    print execLocalGetResult(cmd1)
    print execLocalOutput(cmd2)
    print execLocalStatusOutput(cmd2)
    print execLocalGetResult(cmd2, True)
    print execMethod(execLocalGetResult,cmd2,True)

    print execLocalStatusOutput("/bin/false")
    print execLocal("/bin/false")

def __line(text):
    print("-------------------------- %s --------------------------------------" %(text))

if __name__=="__main__":
    __line("level: "+SIMULATE)
    test(SIMULATE)
    __line("level: "+"")
    test("")
    __line("level: "+ASK)
    test(ASK)

# $Log: ComSystem.py,v $
# Revision 1.15  2008-02-27 10:42:54  marc
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
