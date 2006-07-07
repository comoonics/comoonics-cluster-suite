#!/usr/bin/python
"""Com.oonics Enterprisecopy

The comoonics Enterprisecopy binary parses an xml configfile and then goes through every copy and modificationset and
does it.

"""


# here is some internal information
# $Id: com-ec.py,v 1.1 2006-07-07 08:40:02 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/bin/Attic/com-ec.py,v $

from exceptions import Exception
import sys
import os
import xml.dom
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2

sys.path.append("../lib")

import ComLVM
import ComSystem
import ComLog
import ComEnterpriseCopy
import ComCopyset
import ComModificationset
import getopt
import logging
import warnings

ComSystem.__EXEC_REALLY_DO=""

def line(str=None):
    print
    print "--------------------"+str+"---------------------------------"

def usage(argv):
    print "%s [-a|--ask] [-d|-debug] [-n|--novalidate] xmlfilename" % argv[0]
    print '''
    executes all commands described in the <xmlfile>
    
    -a|--ask ask before any command is executed
    -d|--debug be more helpfull
    -n|--novalidate don't validate the xml. Handle with care!!!
    '''

def setWarnings():
    warnings.filterwarnings(action = 'ignore', message='tempnam.*', category=RuntimeWarning, module='Com*')
    
try:
    (opts, args_proper)=getopt.getopt(sys.argv[1:], 'adn', [ 'ask', 'debug', 'novalidate' ])
except getopt.GetoptError, goe:
    print "Error parsing params: %s", goe
    usage()
    sys.exit(1)

VALIDATE=True
DEBUG=False
ASK_MODE=False
ComLog.setLevel(logging.INFO)
for (opt, value) in opts:
#    print "Option %s" % opt
    if opt == "-a" or opt == "--ask":
        ASK_MODE=True
    elif opt == "-d" or opt == "--debug":
        DEBUG=True
        ComLog.setLevel(logging.DEBUG)
    elif opt == "-n" or opt == "--novalidate":
        VALIDATE=FALSE

# filter warnings
setWarnings()

# create Reader object
if VALIDATE:
    reader = Sax2.Reader(validate=1)
else:
    reader = Sax2.Reader(validate=0)

if len(args_proper) > 0:
    filename=args_proper[0]
else:
    print "No file as input given exiting."
    usage(sys.argv)
    sys.exit(1)

try:
    file=os.fdopen(os.open(filename,os.O_RDONLY))
    line("Parsing document %s " % filename)
    doc = reader.fromStream(file)
    businesscopy=ComEnterpriseCopy.getEnterpriseCopy(doc.documentElement, doc)
    if ASK_MODE:
        ComSystem.__EXEC_REALLY_DO="ask"
except KeyboardInterrupt:
    ComLog.getLogger(ComEnterpriseCopy.EnterpriseCopy.__logStrLevel__).info("Leaving because of user signal")
    sys.exit(1)
    
try:
    if businesscopy.hasAttribute("name"):
        line("Execution of businesscopy %s" % (businesscopy.getAttribute("name")))
    else:
        line("Execution of businesscopy %s" % ("unknown"))

    line("Executing copysets %u" % len(businesscopy.copysets))
    businesscopy.doCopysets()

    line("Executing all modificationsets %u" % len(businesscopy.modificationsets))
    businesscopy.doModificationsets()

    line("Successfully executed businesscopy.")
except KeyboardInterrupt:
    ComLog.getLogger(ComEnterpriseCopy.EnterpriseCopy.__logStrLevel__).info("Leaving because of user signal")
    sys.exit(1)
except Exception, e:
    ComLog.getLogger(ComEnterpriseCopy.EnterpriseCopy.__logStrLevel__).warn("Exception %s caught during copy." % e)
    import traceback
    traceback.print_exc()
    line("Undoing executing all copysets %u" % len(businesscopy.copysets))
    ComLog.getLogger(ComEnterpriseCopy.EnterpriseCopy.__logStrLevel__).warn("Undoing %s." % ComCopyset.Copyset.TAGNAME)
    businesscopy.undoCopysets()
    line("Undoing executing all modificationsets %u" % len(businesscopy.modificationsets))
    ComLog.getLogger(ComEnterpriseCopy.EnterpriseCopy.__logStrLevel__).warn("Undoing %s." % ComModificationset.Modificationset.TAGNAME)
    businesscopy.undoModificationsets()

    line("Errors during execution of businesscopy.")

##################
# $Log: com-ec.py,v $
# Revision 1.1  2006-07-07 08:40:02  marc
# initial revision business is enterprise now.
#
# Revision 1.6  2006/07/05 13:06:50  marc
# support names on every tag.
#
# Revision 1.5  2006/07/04 11:38:21  mark
# added support for Ctrl-C interrupt
#
# Revision 1.4  2006/07/04 11:16:11  mark
# added setWarinings()
#
# Revision 1.3  2006/07/04 11:01:48  marc
# be a little more verbose
#
# Revision 1.2  2006/07/03 16:11:10  marc
# added commandline params
#
# Revision 1.1  2006/06/30 13:57:13  marc
# initial revision
#