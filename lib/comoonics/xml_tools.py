#!/usr/bin/python
"""
Collection of xml tools
"""

__version__= "$Revision $"

# $Id: xml_tools.py,v 1.1 2006-12-08 08:32:05 marc Exp $

import warnings

def overwrite_element_with_xpaths(element, xpaths):
    """ Overwrites all node values referred with the xpaths and the given values. Xpaths has to be a map with
        xpath as key and value as value. All other referred nodetypes are silently ignored.
    """
    for xpath in xpaths.keys():
        try:
            import xml
            if isinstance(element, xml.dom.Node):
                from xml.dom   import Element, Node
                from xml.xpath import Evaluate
                sets = Evaluate(xpath, element)
                for set in sets:
                    set.nodeValue=xpaths[xpath]
            else:
                import libxml2
                ctxt = element.xpathNewContext()
                sets = ctxt.xpathEvalExpression(xpath)
                for set in sets:
                    print "%s, %s" %(set.name, set.content)
                    set.setContent(xpaths[xpath])
                    print "%s, %s" %(set.name, set.content)
#                import StringIO
#                ctxt.xpathFreeContext()
#                f = StringIO.StringIO()
#                buf = libxml2.createOutputBuffer(f, 'UTF-8')
#                element.saveFormatFileTo(buf, 'UTF-8', 0)
#                print f.getvalue()
        except:
            warnings.warn("Could not apply value \"%s\" to xpath \"%s\"." %(xpaths[xpath], xpath))
            import traceback
            traceback.print_exc()

    return element

def main():
    xml="""<?xml version="1.0" encoding="UTF-8"?>
<localclone>
  <node name="lilr629"/>
  <destdisks><disk name="/dev/gnbd/singleclone"/></destdisks>
  <kernel version="2.6.9-34.0.1.ELsmp"/>
</localclone>
    """
    from xml.dom.ext import PrettyPrint
    from xml.dom.minidom import parseString
    doc=parseString(xml)
    xpaths={"/localclone/node/@name": "myname",
            "/localclone/destdisks/disk/@name": "/dev/sda1"}
    print "-----------_Before_-------------"
    PrettyPrint(doc)
    overwrite_element_with_xpaths(doc.documentElement, xpaths)
    print "-----------_After(overwrite_element_with_xpaths)_--------------"
    PrettyPrint(doc)


if __name__ == '__main__':
    main()

#################
# $Log: xml_tools.py,v $
# Revision 1.1  2006-12-08 08:32:05  marc
# initial revision
#