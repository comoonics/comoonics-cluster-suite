"""
The controller class for the comoonics assistant  

There are two xml files needed to construct the ECAssisstantController.
The first one is a template xml file, that needs to be modified
e.g.

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE localclone SYSTEM "/opt/atix/comoonics-cs/xml/comoonics-enterprise-clone.dtd">
<localclone source="disk" destination="disk">
  <cluster name="axqa01" sourcesuffix="" destsuffix="C"></cluster>
    <sourcedisks>
      <bootdisk name="/dev/sdb"/>
      <rootdisk name="/dev/sdc"/>
    </sourcedisks>
    <destdisks>
      <bootdisk name="/dev/sdl"/>
      <rootdisk name="/dev/sdm"/>
    </destdisks>
    <destpartitions>
      <rootpartition name="/dev/sdm1"/>
    </destpartitions>
  <kernel version="2.6.9-42.0.10.ELsmp"/>
</localclone>

The second one is a xml file, that defines the values that should be modified.


<info>
    <entry xpath="/localclone/cluster/@name" type="txt" helper="rh-clustername" validator=""/>
</info>


"""
import xml.dom
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml import xpath
import logging
import StringIO

from comoonics import ComLog, XmlTools, odict
from comoonics.ComDataObject import DataObject
from comoonics.enterprisecopy import ComEnterpriseCopy


from ComAssistantController import *
from ComAssistantInfo import *

import ComAssistantHelper


__logStrLevel__ = "comoonics.assistant.ECAssistant"
class ECAssistantController(AssistantController):
    def __init__(self, xml_tmpl_file, value_def_file, xsl_file=None, validate=0, scan=False):
        self.xsl_file=xsl_file
        self.xml_tmpl_file=xml_tmpl_file

        reader = Sax2.Reader(validate)
        self.doc = reader.fromStream(xml_tmpl_file)
        self.value_def_doc = reader.fromStream(value_def_file)
                
        self._createInfoDict(scan)
    
    def getNeededInfo(self):
        """
        @return: Dictionary of Info objects
        """
        return self.infodict.values()
        
    def getInfoDict(self):
        return self.infodict
    
    def run(self, really=False):
        if self.xsl_file:
            _xml=StringIO.StringIO()
            PrettyPrint(self.doc, _xml)
            _doc=XmlTools.createDOMfromXML(_xml.getvalue(), self.xsl_file)
        else:
            _doc=self.doc
        
        if really:
            ecopy=ComEnterpriseCopy.getEnterpriseCopy(_doc.documentElement, _doc)
            ecopy.doAllsets()
        else:
            PrettyPrint(_doc)

        
    def save(self):
        self.writeXMLFile(self.xml_tmpl_file)    
    
    def writeXMLFile(self, filename):
        _file=open(filename, "w")
        PrettyPrint(self.doc, _file)
        
    
    #private methods
    
    def getDocument(self):
        return self.doc
    
    def printDocument(self):
        PrettyPrint(self.doc)
        
    def _createInfoDict(self, scan):
        _infodict=odict.Odict()
        # get the root element
        _info=self.value_def_doc.getElementsByTagName("info")[0]
        # For all <entry> elements
        for _elem in _info.getElementsByTagName("entry"):
            _elem = InfoElement(_elem)
            _node=None
            # OK, now get the list of <xpath> elements
            for _xpath in _elem.getXpathList():
                _xpathname=_xpath.getAttribute("name")
                ComLog.getLogger(__logStrLevel__).debug("xpath %s" %_xpathname)
            
                try:
                    _node=xpath.Evaluate(_xpathname, self.doc)[0]
                    ComLog.getLogger(__logStrLevel__).debug("xpath %s does match" %_xpathname)
                    break
                except Exception, e:
                    ComLog.getLogger(__logStrLevel__).debug("xpath %s does not match" %_xpathname)
                    pass
                
            if _node == None:
                ComLog.getLogger(__logStrLevel__).warning("element %s not found" %_elem.getName())
                break
            
            _ainfo=AttrAssistantInfo(_node, _elem.getName(), \
                                               _elem.getAttribute("type"),\
                                               _elem.getComment(),\
                                               None,\
                                               ComAssistantHelper.createAssistantHelper(_elem.getHelperClassName(), _elem.getHelperQuery()))
            if scan:
                _ainfo.scan()
            _infodict[_elem.getName()]=_ainfo
            
        self.infodict=_infodict
    
    
    
class InfoElement(DataObject):
    def __init__(self, element, doc=None):
        DataObject.__init__(self, element, doc)
    
    def getName(self):
        return self.getAttribute("name")    

    def getXpathList(self):
        return self.getElement().getElementsByTagName("xpath")
    
    def getComment(self):
        """
        @todo: localize comment
        """
        try:
            return self.getElement().getElementsByTagName("comment")[0].firstChild.nodeValue
        except Exception:
            return 
    def getHelperClassName(self):
        try:
            return self.getElement().getElementsByTagName("helper")[0].getAttribute("name")
        except Exception, e:
            return
        
    def getHelperQuery(self):
        try:
            return self.getElement().getElementsByTagName("helper")[0].getAttribute("query")
        except Exception, e:
            return
    
    
def test():
    ComLog.setLevel(logging.DEBUG)
    ac=ECAssistantController("./localclone.xml", "./infodef.xml", "/opt/atix/comoonics-cs/xsl/localclone.xsl", scan=False)
    for _info in  ac.getNeededInfo():
        print "Name    : %s" %_info.getName()   
        print "Value   : %s" %_info.getValue()
        print "Comment : %s" %_info.getComment()
        print "Type    : %s" %_info.getType()
        
        print "---------------------------------"
        print _info
        _info.setValue("allesneu")


    ac.run()
    
    
if __name__=="__main__":
    test()
        
        

