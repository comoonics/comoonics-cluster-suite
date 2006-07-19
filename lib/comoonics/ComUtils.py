"""Comoonics utility module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComUtils.py,v 1.1 2006-07-19 14:29:15 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/Attic/ComUtils.py,v $



from exceptions import *

import re
import ComLog
import ComSystem

log=ComLog.getLogger("ComUtils")

CMD_SFDISK = "/sbin/sfdisk"

def isInt( str ):
    """ Is the given string an integer?     """
    ok = 1
    try:
        num = int(str)
        #log.debug(str + " is of int")
    except ValueError:
        #log.debug(str + " is not of int")
        ok = 0
    return ok

def copyPartitionTable(source_device, destination_device):
    __cmd = CMD_SFDISK + " -d " + source_device.getDeviceName() + " | " + CMD_SFDISK \
            + " " + destination_device.getDeviceName()
    __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
    log.debug("copyPartitionTable " + __ret)
    if __rc != 0:
        raise ComException(__cmd)
        
def grepInLines(lines, exp):
    rv=[]
    for line in lines:
        m = re.match(exp, line)
        try:
            res=m.group(1)
            rv.append(res)
        except Exception:
            pass
    return rv
    
# $Log: ComUtils.py,v $
# Revision 1.1  2006-07-19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.5  2006/07/04 08:33:23  mark
# minor bug fixes
#
# Revision 1.4  2006/06/28 17:24:00  mark
# bug fixes
#
# Revision 1.3  2006/06/23 16:17:38  mark
# added grepInLines
#
# Revision 1.2  2006/06/23 11:55:58  mark
# moved Log to bottom
#
# Revision 1.1  2006/06/23 07:56:24  mark
# initial checkin (stable)
#
