"""Comoonics system module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComSystem.py,v 1.5 2006-10-19 10:05:14 marc Exp $
#


__version__ = "$Revision: 1.5 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ComSystem.py,v $

import sys
import commands
import os
import popen2

import ComLog


__EXEC_REALLY_DO = "ask"
log=ComLog.getLogger("ComSystem")

def setExecMode(__mode):
    """ set the mode for system execution """
    __EXEC_REALLY_DO = __mode

def execLocalStatusOutput(__cmd):
    """ exec %__cmd and return output and status (rc, out)"""
    log.debug(__cmd)
    if __EXEC_REALLY_DO == "ask":
        __ans=raw_input(__cmd+" (y*,n,c)")
        if __ans == "y" or __ans == "":
            return commands.getstatusoutput(__cmd)
        elif __ans == "c":
            ComSystem.__EXEC_REALLY_DO=""
        return [0,"skipped"]
    return commands.getstatusoutput(__cmd)


def execLocalGetResult(__cmd, err=False):
    """ exec %__cmd and returns an array ouf output lines (rc, out, err)"""
    log.debug(__cmd)
    if __EXEC_REALLY_DO == "ask":
        __ans=raw_input(__cmd+" (y,n)")
        if __ans != "y":
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
    log.debug(__cmd)
    if __EXEC_REALLY_DO == "ask":
        __ans=raw_input(__cmd+" (y,n)")
        if __ans == "y":
            return os.system(__cmd)
        return 0
    return os.system(__cmd)

# $Log: ComSystem.py,v $
# Revision 1.5  2006-10-19 10:05:14  marc
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
