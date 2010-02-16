logging.basicConfig()
#!/usr/bin/python
"""Com.oonics Livecd admin


"""

# here is some internal information
# $Id: com-livecd-admin.py,v 1.4 2010-02-16 10:29:34 marc Exp $
#

__version__ = "$Revision: 1.4 $"
__description__="""
Comoonics LiveCD administrators utility
"""
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/bin/com-livecd-admin.py,v $

import sys
import logging
from optparse import OptionParser, IndentedHelpFormatter
logging.basicConfig()

sys.path.append("../lib")
import os.path
sys.path.append(os.path.join(os.path.normpath(sys.prefix), "lib", "python" + sys.version[:3], "site-packages"))

from comoonics import ComLog
from comoonics.ComExceptions import ComException

from comoonics.livecd.ComLivecdMaster import *




def setDebug(option, opt, value, parser):
	ComLog.setLevel(logging.DEBUG)
	setattr(parser.values, option.dest, True)

def setSimulate(option, opt, value, parser):
	ComSystem.__EXEC_REALLY_DO="simulate"
	setattr(parser.values, option.dest, True)

def setAsk(option, opt, value, parser):
	ComSystem.__EXEC_REALLY_DO="ask"
	setattr(parser.values, option.dest, True)

def cmd_help():
	print "\t commands:"
	print "\t help:\t print extended help"
	print "\t mount:\t mount livecd"

def cmd_mount():
	ComLog.debug("mount")
	pass
	

ComLog.setLevel(logging.INFO)

parser = OptionParser(description=__doc__, version=__version__)

parser.add_option("-D", "--debug", dest="debug", default=False, action="callback", callback=setDebug, help="Debug")
parser.add_option("-s", "--simulate", dest="debug", default=False, action="callback", callback=setSimulate, help="Simulate")
parser.add_option("-a", "--ask", dest="debug", default=False, action="callback", callback=setAsk, help="Ask")
parser.add_option("-d", "--device", dest="device", action="store", help="Device")
parser.add_option("-r", "--root", dest="root", default="/mnt/livecd", action="store", help="Root mountpoint")
parser.add_option("-c", "--command", dest="cmd", action="store", help="Command")


(options, args) = parser.parse_args()
    
if not options.device:
	parser.print_help()
	sys.exit(1)
    
livecd=ComLivecdMaster()
livecd.setRootMountpoint(options.root)
livecd.setDevice(options.device)

mycmd=options.cmd
if mycmd:
	ComSystem.execMethod(getattr(livecd, mycmd))



