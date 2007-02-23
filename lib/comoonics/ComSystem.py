"""Comoonics system module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComSystem.py,v 1.7 2007-02-23 12:42:43 marc Exp $
#


__version__ = "$Revision: 1.7 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ComSystem.py,v $

import sys
import commands
import os
import popen2

import ComLog

from comoonics.ComExceptions import ComException

class ExecLocalException(ComException):
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

__EXEC_REALLY_DO = "ask"
log=ComLog.getLogger("ComSystem")

def setExecMode(__mode):
    """ set the mode for system execution """
    __EXEC_REALLY_DO = __mode

def execLocalStatusOutput(__cmd):
    """ exec %__cmd and return output and status (rc, out)"""
    global __EXEC_REALLY_DO
    log.debug(__cmd)
    if __EXEC_REALLY_DO == "ask":
        __ans=raw_input(__cmd+" (y*,n,c)")
        if __ans == "y" or __ans == "":
            return commands.getstatusoutput(__cmd)
        elif __ans == "c":
            __EXEC_REALLY_DO="continue"
        return [0,"skipped"]
    return commands.getstatusoutput(__cmd)


def execLocalOutput(__cmd):
    """ executes the given command and returns stdout output. If status is not 0 an exeception is thrown
        and errorcode, cmd, stdout and stderr are in that exception """
    (rc, out, err)=execLocalGetResult(__cmd, True)
    if rc==0:
        return out
    else:
        raise ExecLocalException(__cmd, rc, out, err)

def execLocalGetResult(__cmd, err=False):
    """ exec %__cmd and returns an array ouf output lines (rc, out, err)"""
    global __EXEC_REALLY_DO
    log.debug(__cmd)
    if __EXEC_REALLY_DO == "ask":
        __ans=raw_input(__cmd+" (y*,n,c)")
        if __ans == "c":
            __EXEC_REALLY_DO="continue"
        if __ans == "n":
            if err:
                return [0, "skipped", ""]
            else:
                return [0, "skipped"]
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
    if __EXEC_REALLY_DO == "ask":
        __ans=raw_input(__cmd+" (y*,n,c)")
        if __ans == "y" or __ans=="":
            return os.system(__cmd)
        elif __ans == "c":
            __EXEC_REALLY_DO="continue"
        return 0
    return os.system(__cmd)

# $Log: ComSystem.py,v $
# Revision 1.7  2007-02-23 12:42:43  marc
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
