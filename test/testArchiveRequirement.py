# here is some internal information
# $Id: testArchiveRequirement.py,v 1.2 2006-07-19 14:29:43 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/test/testArchiveRequirement.py,v $

import sys
import os
import xml.dom
from xml.xpath          import Evaluate
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2

sys.path.append("../lib")

from comoonics import ComLVM
from comoonics import ComSystem
from comoonics import ComLog
from comoonics.enterprisecopy import ComRequirement
from comoonics.enterprisecopy import ComCopyset

ComSystem.__EXEC_REALLY_DO=""

def line(str=None):
    print
    print "--------------------"+str+"---------------------------------"

# create Reader object
reader = Sax2.Reader()

filename="./example_config.xml"
if len(sys.argv) > 1:
    filename=sys.argv[1]

file=os.fdopen(os.open(filename,os.O_RDONLY))
doc = reader.fromStream(file)

line("XML Document")
PrettyPrint(doc)

line("reqss of modification@archive")
reqs = Evaluate('enterprisecopy/modificationset/device/modification/requirement[@type="archive"]', doc)
print reqs
for i in range(len(reqs)):
    line("reqs[%u]" % i)
    req=ComRequirement.getRequirement(reqs[i], doc)
    print "Requirement: ", req
    print "XML: "
    PrettyPrint(req.getElement())
    line("write to dest: %s" % req)
    ComSystem.__EXEC_REALLY_DO="ask"
    line("req.doPre")
    req.doPre()
    line("req.doPost")
    req.doPost()
    

##################
# $Log: testArchiveRequirement.py,v $
# Revision 1.2  2006-07-19 14:29:43  marc
# changed because of change in fs-hierarchie
#
# Revision 1.1  2006/06/30 08:30:39  marc
# initial revision
#