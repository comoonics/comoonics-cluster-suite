# here is some internal information
# $Id: testLVMCopyset.py,v 1.1 2006-06-30 12:40:14 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/test/testLVMCopyset.py,v $

import sys
import os
import xml.dom
from xml.xpath          import Evaluate
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2

sys.path.append("../lib")

import ComLVM
import ComSystem
import ComLog
import ComCopyset
from ComLVMCopyObject import LVMCopyObject
from ComLVMCopyset import LVMCopyset

ComSystem.__EXEC_REALLY_DO=""

def line(str=None):
    print
    print "--------------------"+str+"---------------------------------"

# create Reader object
reader = Sax2.Reader(validate=1)

filename="./example_config.xml"
if len(sys.argv) > 1:
    filename=sys.argv[1]

file=os.fdopen(os.open(filename,os.O_RDONLY))
doc = reader.fromStream(file)

line("XML Document")
PrettyPrint(doc)

line("sets of copyset@lvm")
sets = Evaluate('businesscopy/copyset[@type="lvm"]', doc)
print sets
for i in range(len(sets)):
    line("set[%u]" % i)
    cs=ComCopyset.getCopyset(sets[i], doc)
    print "Copyset: ", cs
    print "XML: "
    PrettyPrint(cs.getElement())
    line("write to dest: %s" % cs)
    ComSystem.__EXEC_REALLY_DO="ask"
    try:
        cs.doCopy()
    except Exception, e:
        ComLog.getLogger("testLVMCopyset").warn("Exception %s caught during copy. Undoing." % e)
        import traceback
        traceback.print_exc()
        cs.undoCopy()
    

##################
# $Log: testLVMCopyset.py,v $
# Revision 1.1  2006-06-30 12:40:14  marc
# initial revision
#