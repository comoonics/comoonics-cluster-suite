#!/usr/bin/python
"""Com.oonics Businesscopy

The comoonics Businesscopy binary parses an xml configfile and then goes through every copy and modificationset and
does it.

"""


# here is some internal information
# $Id: com-bc.py,v 1.5 2006-07-04 11:38:21 mark Exp $
#


__version__ = "$Revision: 1.5 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/bin/Attic/com-bc.py,v $

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
import ComBusinessCopy
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
    businesscopy=ComBusinessCopy.getBusinessCopy(doc.documentElement, doc)
    if ASK_MODE:
        ComSystem.__EXEC_REALLY_DO="ask"
except KeyboardInterrupt:
    ComLog.getLogger(ComBusinessCopy.BusinessCopy.__logStrLevel__).info("Leaving because of user signal")
    sys.exit(1)
    
try:
    line("executing copysets %u" % len(businesscopy.copysets))
    businesscopy.doCopysets()

    line("executing all modificationsets %u" % len(businesscopy.modificationsets))
    businesscopy.doModificationsets()

    line("Successfully executed businesscopy.")
except KeyboardInterrupt:
    ComLog.getLogger(ComBusinessCopy.BusinessCopy.__logStrLevel__).info("Leaving because of user signal")
    sys.exit(1)
except Exception, e:
    ComLog.getLogger(ComBusinessCopy.BusinessCopy.__logStrLevel__).warn("Exception %s caught during copy." % e)
    import traceback
    traceback.print_exc()
    line("undoing executing all copysets %u" % len(businesscopy.copysets))
    ComLog.getLogger(ComBusinessCopy.BusinessCopy.__logStrLevel__).warn("Undoing %s." % ComCopyset.Copyset.TAGNAME)
    businesscopy.undoCopysets()
    line("undoing executing all modificationsets %u" % len(businesscopy.modificationsets))
    ComLog.getLogger(ComBusinessCopy.BusinessCopy.__logStrLevel__).warn("Undoing %s." % ComModificationset.Modificationset.TAGNAME)
    businesscopy.undoModificationsets()

    line("Errors during execution of businesscopy.")

##################
# $Log: com-bc.py,v $
# Revision 1.5  2006-07-04 11:38:21  mark
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