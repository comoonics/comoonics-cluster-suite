#!/usr/bin/python
"""Com.oonics Businesscopy

The comoonics Businesscopy binary parses an xml configfile and then goes through every copy and modificationset and
does it.

"""


# here is some internal information
# $Id: com-bc.py,v 1.1 2006-06-30 13:57:13 marc Exp $
#


__version__ = "$Revision: 1.1 $"
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

ComSystem.__EXEC_REALLY_DO=""

def line(str=None):
    print
    print "--------------------"+str+"---------------------------------"

def usage(argv):
    print "%s xmlfilename" % argv[0]

# create Reader object
reader = Sax2.Reader(validate=1)

if len(sys.argv) > 1:
    filename=sys.argv[1]
else:
    print "No file as input given exiting."
    usage(sys.argv)
    sys.exit(1)

file=os.fdopen(os.open(filename,os.O_RDONLY))
line("Parsing document %s " % filename)
doc = reader.fromStream(file)
businesscopy=ComBusinessCopy.getBusinessCopy(doc.documentElement, doc)
ComSystem.__EXEC_REALLY_DO="ask"

try:
    line("executing copysets %u" % len(businesscopy.copysets))
    businesscopy.doCopysets()

    line("executing all modificationsets %u" % len(businesscopy.copysets))
    businesscopy.doModificationsets()
except Exception, e:
    ComLog.getLogger(ComBusinessCopy.BusinessCopy.__logStrLevel__).warn("Exception %s caught during copy." % e)
    import traceback
    traceback.print_exc()
    ComLog.getLogger(ComBusinessCopy.BusinessCopy.__logStrLevel__).warn("Undoing %s." % ComCopyset.Copyset.TAGNAME)
    businesscopy.undoCopysets()
    ComLog.getLogger(ComBusinessCopy.BusinessCopy.__logStrLevel__).warn("Undoing %s." % ComModificationset.Modificationset.TAGNAME)
    businesscopy.undoModificationsets()

##################
# $Log: com-bc.py,v $
# Revision 1.1  2006-06-30 13:57:13  marc
# initial revision
#