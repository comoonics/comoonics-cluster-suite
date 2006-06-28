"""XML Test

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: xmltest.py,v 1.6 2006-06-28 12:28:55 mark Exp $
#


__version__ = "$Revision: 1.6 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/test/xmltest.py,v $


import os
import xml.dom
from xml.dom import EMPTY_NAMESPACE
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml import xpath

def printDom(doc):
    PrettyPrint(doc)

# create Reader object
reader = Sax2.Reader()

#parse the document
file=os.fdopen(os.open("./example_config.xml",os.O_RDONLY))
doc = reader.fromStream(file)

printDom(doc)

# $Log: xmltest.py,v $
# Revision 1.6  2006-06-28 12:28:55  mark
# using SAX Parser
#
