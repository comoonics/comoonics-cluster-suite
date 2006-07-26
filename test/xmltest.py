"""XML Test

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: xmltest.py,v 1.9 2006-07-26 10:07:09 marc Exp $
#


__version__ = "$Revision: 1.9 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/test/xmltest.py,v $


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

print "Reader: %s" % reader
print "Entities %s " % doc.doctype.entities
for entity in doc.doctype.entities:
    print "Entity: %s" % entity

dtd=reader.parser._parser.get_dtd()
print "DTD-obj: %s" % dtd
print "DTD-general-Entities: %s" % dtd.get_general_entities()
print "DTD-parameter-Entities: %s" % dtd.get_parameter_entities()
entity_name="test"
e_val="test123"
entity = dtd.resolve_ge(entity_name)
print "DTD-parameter-Entity[%s]: %s" %(entity_name, entity)
print "DTD-parameter-Entity[%s]: dict %s" % (entity_name, entity.__dict__)
print "Setting entityvalue to %s" % e_val
entity.value=e_val
print "DTD-parameter-Entity[%s]: dict %s" % (entity_name, entity.__dict__)

printDom(doc)


# $Log: xmltest.py,v $
# Revision 1.9  2006-07-26 10:07:09  marc
# adapted to new versions
#
# Revision 1.8  2006/07/19 14:29:43  marc
# changed because of change in fs-hierarchie
#
# Revision 1.7  2006/06/29 16:42:20  marc
# changed validation
#
# Revision 1.6  2006/06/28 12:28:55  mark
# using SAX Parser
#
