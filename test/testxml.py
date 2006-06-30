"""XML Test

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: testxml.py,v 1.2 2006-06-30 13:56:21 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/test/testxml.py,v $


import os
import sys
import xml.dom
from xml.dom import EMPTY_NAMESPACE
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml import xpath
import xml

def printDom(doc):
    PrettyPrint(doc)

filename="./example_config.xml"
if len(sys.argv) > 1:
    filename=sys.argv[1]

# create Reader object
reader = Sax2.Reader(validate=1)

#parse the document
file=os.fdopen(os.open(filename,os.O_RDONLY))
doc = reader.fromStream(file)

printDom(doc)

# $Log: testxml.py,v $
# Revision 1.2  2006-06-30 13:56:21  marc
# changed default filename
#
# Revision 1.1  2006/06/29 16:36:35  marc
# test for xml
#
# Revision 1.6  2006/06/28 12:28:55  mark
# using SAX Parser
#
