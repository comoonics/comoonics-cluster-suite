#!/usr/bin/python
"""
Python implementation of the HP SSSU utility to communicate with the HP EVA Storage Array system
"""

# here is some internal information
# $Id: ComHP_EVA.py,v 1.3 2007-04-04 12:37:07 marc Exp $
#

__version__ = "$Revision: 1.3 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/hp/ComHP_EVA.py,v $

import re
from comoonics import pexpect, ComLog
from comoonics import ComExceptions

class HP_EVA_ObjectNotInitialized(ComExceptions.ComException): pass
class HP_EVA_IncompatibleContainerElement(ComExceptions.ComException): pass
class HP_EVA_SystemNotFound(ComExceptions.ComException):pass

class HP_EVA_Object(object):
    __logStrLevel__="HP_EVA_Object"
    ALL_ATTRIBS=1
    CHILD_ATTRIBS=None
    ALIASES={"vdisk" : "virtualdisk",
             "lun": "presentedunit"}
    def fromXML(element, theclass=None):
        from xml.dom import Node
        from comoonics import XmlTools
        localmap=globals()
        objecttype=None
        instance=None
        if not theclass:
            ot_elements=element.getElementsByTagName("objecttype")
            if len(ot_elements)==1:
                objecttype=XmlTools.getTextFromElement(ot_elements[0])
                #mylogger.debug("objecttype: %s, %s" %(objecttype, localmap))
        if localmap.has_key("HP_EVA_%s" %(element.nodeName.capitalize())) and not theclass and not objecttype:
            myclass=localmap["HP_EVA_%s" %(element.nodeName.capitalize())]
            #mylogger.debug("theclass: %s" %(myclass))
            instance=HP_EVA_Object.fromXML(element, myclass)
        elif objecttype and localmap.has_key("HP_EVA_%s" %(objecttype.capitalize())) and not theclass:
            myclass=localmap["HP_EVA_%s" %(objecttype.capitalize())]
            #mylogger.debug("theclass: %s" %(myclass))
            instance=HP_EVA_Object.fromXML(element, myclass)
        elif theclass:
            #mylogger.debug("theclass: %s" %(theclass))
            instance=object.__new__(theclass)
            instance.__init__()
            for child in element.childNodes:
                if child.nodeType == Node.ELEMENT_NODE:
                    paramname=child.nodeName
                    paramvalue=XmlTools.getTextFromElement(child)
                    if paramvalue:
                        paramvalue=paramvalue.strip()
                    if paramname and paramvalue and paramvalue!="":
                        #mylogger.debug("setattr(%s, %s, %s)" %(theclass, paramname, paramvalue))
                        setattr(instance, paramname, paramvalue)
                    elif paramname == "parentstoragecellinfo":
                        ids=child.getElementsByTagName("storagecellid")
                        if len(ids)==1:
                            id=XmlTools.getTextFromElement(ids[0])
                            if HP_EVA_Storagecells.has_key(id):
                                #mylogger.debug("storagecellkey: %s, keys: %s, has_key:%u" %(id, HP_EVA_Storagecells.names(), HP_EVA_Storagecells.has_key(id)))
                                instance.setParent(HP_EVA_Storagecells.get(id))
                    elif paramname:
                        setattr(instance, paramname, HP_EVA_Object.fromXML(child))

        return instance
    fromXML=staticmethod(fromXML)

    def __new__(cls, *args, **kwds):
        if kwds:
            if kwds.has_key('classtype'):
                localmap=globals()
                if localmap.has_key("HP_EVA_%s" %(kwds['classtype'].capitalize())):
                    cls=localmap["HP_EVA_%s" %(kwds['classtype'].capitalize())]
                elif HP_EVA_Object.ALIASES.has_key(kwds['classtype']):
                    cls=localmap["HP_EVA_%s" %(HP_EVA_Object.ALIASES[kwds['classtype']].capitalize())]
                del kwds['classtype']
        return object.__new__(cls)

    def __init__(self, **kwds):
        params=parent=None
        if kwds.has_key("parent"):
            parent=kwds["parent"]
            del kwds["parent"]
#        if kwds.has_key("classtype"):
#            del kwds['classtype']
        self.__transient__=HP_EVA_Container()
        self.objectid=""
        #self.objectuid=""
        self.objecttype=HP_EVA_Object.getObjectType(self)
        self.objectname=""
        self.objectwwn=""
        self.objecthexuid=""
        self.parentstoragecellinfo=None
        if parent:
            self.setParent(parent)
        else:
            #self.objectparentuid="0.0.0.0.0.0.0"
            self.objectparenthexuid="0000-0000-0000-0000-0000-0000-0000-0000"
            self.objectparentid="0000000000000000000000000000000000000000"
        if kwds:
            #mylogger.debug("type: %s, kwds%s: %s" %(self.objecttype, type(kwds), kwds))
            for key in kwds.keys():
                self.__dict__[key]=kwds[key]

    def __setattr__(self, name, value):
        self.__dict__[name]=value
        if name == "objectid" and value and value!= "" and self.parentstoragecellinfo:
            self.setParent(self.parentstoragecellinfo)
        if name == "objectname" and value and value!= "" and self.parentstoragecellinfo:
            self.setParent(self.parentstoragecellinfo)

    def getTransient(self, id_name):
        if self.__transient__.has_key(id_name):
            return self.__transient__[id_name]
        elif self.ALIASES and type(self.ALIASES) == dict and self.ALIASES.has_key(id_name):
            return self.__transient__[self.ALIASES[id_name]]
        else:
            return None

    def setTransient(self, id_name, element):
        if self.ALIASES and type(self.ALIASES) == dict and self.ALIASES.has_key(id_name):
            key=self.ALIASES[id_name]
        self.__transient__[key]=element

    def setParent(self, parent):
        self.parentstoragecellinfo=parent
        parent.getTransient(self.objecttype).addElement(self)
        #self.objectparentwwn=parent.objectwwn
        #self.objectparenthexuid=parent.objecthexuid
        #self.objectparentid=parent.objectid

    def getChildAttribs(self, parentname):
        if self.CHILD_ATTRIBS and type(self.CHILD_ATTRIBS)==dict and self.CHILD_ATTRIBS.has_key(parentname):
            return self.CHILD_ATTRIBS[parentname]
        elif self.CHILD_ATTRIBS and type(self.CHILD_ATTRIBS)==dict and self.CHILD_ATTRIBS.has_key("default"):
            return self.CHILD_ATTRIBS["default"]
        elif self.CHILD_ATTRIBS and type(self.CHILD_ATTRIBS) == tuple:
            return self.CHILD_ATTRIBS
        elif self.CHILD_ATTRIBS==HP_EVA_Object.ALL_ATTRIBS:
            return self.__dict__.keys()
        else:
            return None
    def __str__(self):
        return self.toString()
    def toString(self, prefix="", tab="  ", centerjust=40, withparams=True, fillchar="."):
        name=HP_EVA_Object.__name__.replace("HP_EVA_", "").lower()
        if withparams:
            return HP_EVA_Object.formatMap(name, self.__dict__, prefix, tab, centerjust)
        else:
            return "%s%s\n" %(prefix, name)
    def toStringChild(self, parentname, prefix="", tab="  ", centerjust=40, fillchar="."):
        attribs=self.getChildAttribs(parentname)
        buf="%s%s\n" %(prefix, parentname)
        if attribs and (type(attribs)==tuple or type(attribs)==list):
#            mylogger.debug("attribs(%s)" ", ".join(attribs))
            for key in attribs:
                buf=buf+HP_EVA_Object.formatPair(key, getattr(self, key), prefix+tab, tab, centerjust, fillchar)+"\n"
        elif attribs and type(attribs)==dict:
            for key in attribs.keys():
                buf=buf+HP_EVA_Object.formatPair(attribs[key], getattr(self, key), prefix+tab, tab, centerjust, fillchar)+"\n"
        return buf
    def formatMap(name, map, prefix="", tab="  ", centerjust=40, fillchar="."):
        buf="%s%s\n" %(prefix, name)
        for key in map.keys():
            value=map[key]
            if not key.startswith("__") and not key.endswith("__"):
                if isinstance(value, HP_EVA_Object):
                    buf=buf+value.toStringChild(key, prefix+tab, tab, centerjust, fillchar)
                elif type(value) == dict:
                    buf=buf+HP_EVA_Object.formatMap(key, value, prefix+tab, tab, centerjust, fillchar)+"\n"
                elif type(value) == list:
                    for val in value:
                        buf=buf+HP_EVA_Object.formatPair(key, val, prefix+tab, tab, centerjust, fillchar)+"\n"
                else:
                    buf=buf+HP_EVA_Object.formatPair(key, value, prefix+tab, tab, centerjust, fillchar)+"\n"
        return buf
    formatMap=staticmethod(formatMap)
    def formatPair(key, value, prefix="", tab="  ", centerjust=40, fillchar="."):
        if isinstance(value, HP_EVA_Object):
            buf=value.toStringChild(key, prefix, tab, centerjust, fillchar)
        else:
            buf="%s%s" %(prefix, key)
            buf=buf.ljust(centerjust, fillchar)
            buf="%s: %s" %(buf, value)
        return buf
    formatPair=staticmethod(formatPair)

    def toXML(self, rootel=None, doc=None):
        import xml.dom
        if not doc:
            doc=xml.dom.getDOMImplementation().createDocument(None, "object", None)
        if not rootel:
            rootel=doc.documentElement
        HP_EVA_Object.appendAttribMap(rootel, doc, self.__dict__)
        return rootel
    def toXMLChild(self, parentname, rootel=None, doc=None):
        attribs=self.getChildAttribs(parentname)
        element=doc.createElement(parentname)
        if attribs and (type(attribs)==tuple or type(attribs)==list):
            for key in attribs:
                value=getattr(self,key)
                if isinstance(value, HP_EVA_Object):
                    element.appendChild(value.toXMLChild(key, element, doc))
                elif type(value)==list:
                    for val in value:
                        element.appendChild(val.toXMLChild(key, element, doc))
                else:
                    HP_EVA_Object.appendAttrib(element, doc, key, value)
        elif attribs and type(attribs)==dict:
            for key in attribs.keys():
                HP_EVA_Object.appendAttrib(element, doc, attribs[key], getattr(self, key))
        return element
    def getObjectType(classinstance):
        if type(classinstance)==type:
            return classinstance.__name__.replace("HP_EVA_", "").lower()
        else:
            return classinstance.__class__.__name__.replace("HP_EVA_", "").lower()
    getObjectType=staticmethod(getObjectType)
    def appendAttribMap(rootel, doc, map):
        for key in map.keys():
            value=map[key]
            if not key.startswith("__") and not key.endswith("__"):
                if isinstance(value, HP_EVA_Object):
                    rootel.appendChild(value.toXMLChild(key, rootel, doc))
                elif type(value) == list:
                    for val in value:
                        rootel.appendChild(val.toXMLChild(key, rootel, doc))
                elif type(value) == dict:
                    baseel=doc.createElement(key)
                    HP_EVA_Object.appendAttribMap(baseel, doc, value)
                    rootel.appendChild(baseel)
                elif type(value) == str or type(value) == unicode:
                    HP_EVA_Object.appendAttrib(rootel, doc, key, value)
#                else:
#                    mylogger.debug("HP_EVA_Object.appendAttribMap: %s, %s, %s" %(key, value, type(value)))

    appendAttribMap=staticmethod(appendAttribMap)
    def appendAttrib(baseelement, doc, key, value):
        valueel=doc.createElement(key)
        if value and value != "":
            valueel.appendChild(doc.createTextNode(value))
        baseelement.appendChild(valueel)
    appendAttrib=staticmethod(appendAttrib)

class HP_EVA_Virtualdisk(HP_EVA_Object):
    """ Representation of an EVA-VDisk """
    def __init__(self, **kwds):
        super(HP_EVA_Virtualdisk, self).__init__(**kwds)
        if self.objecttype=="virtualdisk":
            self.objectname="%s\ACTIVE" %(self.objectname)
class HP_EVA_Snapshot(HP_EVA_Virtualdisk):
    """ Representation of an EVA-VDisk """
    def __init__(self, **kwds):
        super(HP_EVA_Snapshot, self).__init__(**kwds)
        if self.objecttype=="virtualdisk":
            self.objectname="%s\ACTIVE" %(self.objectname)
class HP_EVA_Presentedunit(HP_EVA_Object): pass

class HP_EVA_Host(HP_EVA_Object):
    def __init__(self, params=None):
        super(HP_EVA_Host, self).__init__(params)
class HP_EVA_Diskgroupfolder(HP_EVA_Object):
    def __init__(self, **params):
        self.totaldisks=0
        self.levelingstate="inactive"
        self.levelingprogress=100
        self.rssdiskstate="none"
        self.srclevelactual="vraid0"
        self.diskdrivetype="online"
        self.requestedsparepolicy="single"
        self.currentsparepolicy="single"
        self.totalstoragespace=0
        self.totalstoragespacegb=0
        self.usedstoragespace=0
        self.usedstoragespacegb=0
        self.occupancyalarmlevel=90
        self.operationalstate="good"
        self.operationalstatedetail="initialized_ok"
        self.vraid0storagespace=0
        self.vraid1storagespace=0
        self.vraid5storagespace=0
        self.vraid0storagespacegb=0
        self.vraid1storagespacegb=0
        self.vraid5storagespacegb=0
        super(HP_EVA_Diskgroupfolder, self).__init__(**params)
class HP_EVA_Disk(HP_EVA_Object):
    def __init__(self, **params):
        self.operationalstate="good"
        self.operationalstatedetail="member_ok"
        self.formattedcapacity=0
        self.diskdrivetype="online"
        self.mediaaccessible="no"
        self.failurepredicted="no"
        self.manufacturer=""
        self.modelnumber=""
        self.firmwareversion=""
        self.disktype="fibre_channel_disk"
        self.rssindex=0
        self.rssid=0
        self.migrationprogress="n/a"
        self.storagecellname=""
        self.occupancy=0
        self.migrationstate="not_migrating"
        self.canlocaterss=1
        self.diskbaynumber=0
        self.looppair="looppair1"
        self.shelfnumber=0
        self.DiskCanCodeLoad=0
        if params["parent"]:
            self.actualusage="grouped"
            self.requestedusage="grouped"
        else:
            self.actualusage="ungrouped"
            self.requestedusage="ungrouped"
        self.quorumdisk="no"
        self.loops={"loop1": HP_EVA_Loop({"loopname": "loopa"}),
                    "loop2": HP_EVA_Loop({"loopname": "loopb"})}
        super(HP_EVA_Disk, self).__init__(**params)

class HP_EVA_Loop(HP_EVA_Object):
    CHILD_ATTRIBS=("loopname", "portwwid", "loopid", "assignedlun", "loopstate", "loopalpa")
    def __init__(self, **params):
        super(HP_EVA_Loop, self).__init__(**params)
class HP_EVA_Presentation(HP_EVA_Object):
    CHILD_ATTRIBS=HP_EVA_Object.ALL_ATTRIBS
    """ Representation of a HP presentation """
    def __init__(self, params=None):
        pass
        #HP_EVA_Object.__init__(self, params)
class HP_EVA_Presentations(HP_EVA_Object):
    CHILD_ATTRIBS=HP_EVA_Object.ALL_ATTRIBS
    """ Representation of HP presentations """
    def __init__(self, **params):
#        pass
        self.presentation=list()

    def __setattr__(self, name, value):
#        mylogger.debug("HP_EVA_Presentations.setattr(%s, %s, %s)" %(self.__class__, name, value))
        if name == "presentation" and value:
            self.presentation.append(value)
        else:
            self.__dict__[name]=value

class HP_EVA_Controllertime(HP_EVA_Object):
    CHILD_ATTRIBS=("day", "month", "year", "hour", "minute", "second")
    def __init__(self, day="", month="", year="", hour="", minute="", second=""):
        super(HP_EVA_Controllertime, self).__init__()
        self.day=day
        self.month=month
        self.year=year
        self.hour=hour
        self.minute=minute
        self.second=second

class HP_EVA_Storagecell(HP_EVA_Object):
    CHILD_ATTRIBS={"parentstoragecellinfo": {"objectname": "storagecellname", "objectid": "storagecellid", "objectwwn": "storagecellwwn"}}
    """ Class representing the HP EVA """
    def __init__(self, **params):
        HP_EVA_Object.__init__(self, **params)
        self.__transient__["virtualdisk"]=HP_EVA_Container()
        self.__transient__["snapshot"]=self.__transient__["virtualdisk"]
        self.__transient__["presentedunit"]=HP_EVA_Container()
        self.display_xmlstatus=False

    def __setattr__(self, name, value):
        self.__dict__[name]=value
        if name == "objectid" and value and value!= "":
            self.register()
        if name == "objectname" and value and value!= "":
            self.register()


    def register(self, registry=None):
        """ Registeres this storagecell to the given storagecells or if not given to the static variable
        HP_StorageCells"""
        if not self.objectid or self.objectid == "":
            raise HP_EVA_ObjectNotInitialized("Storagesystem not initialized")
        if not registry:
            registry=HP_EVA_Storagecells
        registry.addElement(self)

    def manage(self):
        return 0

    def addVdisk(self, vdisk):
        self.getTransient("virtualdisk").addElement(vdisk)
        vdisk.setParent(self)
    def delVdisk(self, vdisk):
        self.getTransient("virtualdisk").deleteElement(vdisk)

class HP_EVA_Storagecell_HSV110(HP_EVA_Storagecell):
    def __init__(self, **params):
        self.systemtype="HSV110"
        super(HP_EVA_Storagecell_HSV110, self).__init__(**params)
        self.objecttype=HP_EVA_Object.getObjectType(HP_EVA_Storagecell)

class HP_EVA_Container(dict):
    def __init__(self, mapping=None):
        super(HP_EVA_Container, self).__init__()
        self._names=dict()
        if mapping and type(mapping)==dict:
            for key in mapping.keys():
                self.__setitem__(key, mapping[key])
        elif mapping and type(mapping)==list:
            for element in mapping:
                self.addElement(element)

    def __getitem__(self, id_name):
        return self.get(id_name)

    def __delitem__(self, id_name):
        element=self.get(id_name)
        if element and self._names.has_key(element.objectname):
            self._names.__delitem__(element.objectname)
        else:
            raise KeyError(id_name)
        return super(HP_EVA_Container, self).__delitem__(element.objectid)

    def __setitem__(self, id, element):
        if isinstance(element, HP_EVA_Object) and not element.objectname=="":
            self._names[element.objectname]=element
        super(HP_EVA_Container, self).__setitem__(id, element)

    def __str__(self):
        return super(HP_EVA_Container, self).__str__()+"\n"+self._names.__str__()

    def clear(self):
        super(HP_EVA_Container, self).clear()
        self._names.clear()

    def copy(self):
        return super(HP_EVA_Container, self).copy()

    def get(self, id_name, d=None):
        if super(HP_EVA_Container, self).has_key(id_name):
            return super(HP_EVA_Container, self).get(id_name, d)
        elif self._names.has_key(id_name):
            return self._names.get(id_name, d)
        else:
            return d

    def has_key(self, id_name):
        if super(HP_EVA_Container, self).has_key(id_name):
            return True
        elif self._names.has_key(id_name):
            return True
        else:
            return False

    def pop(self, key, d):
        x=super(HP_EVA_Container, self).pop(key, d)
        self._names.pop(key, d)
        return x

    def popitem(self):
        (k,v)=super(HP_EVA_Container, self).popitem()
        if self._names.has_key(k):
            self._names.pop(k)
        return (k,v)

    def setdefault(self, k, d):
        super(HP_EVA_Container, self).setdefault(k, d)
        self._names.setdefault(k,d)

    def update(self, E, **F):
        super(HP_EVA_Container, self).update(E, F)
        self._names.update(E, F)

    def addElement(self, element):
        if isinstance(element, HP_EVA_Object):
            self.__setitem__(element.objectid, element)
        else:
            raise HP_EVA_IncompatibleContainerElement()

    def deleteElement(self, element):
        if isinstance(element, HP_EVA_Object):
            del self[element.objectid]
        else:
            raise HP_EVA_IncompatibleContainerElement()

    def names(self):
        return self._names.keys()

    def ids(self):
        return self.keys()

HP_EVA_Storagecells=HP_EVA_Container()
mylogger=ComLog.getLogger(HP_EVA_Object.__logStrLevel__)

class Test_HP_EVA_Controllertime(HP_EVA_Controllertime):
    def __init__(self):
        super(Test_HP_EVA_Controllertime, self).__init__("0", "0", "0", "0", "0", "0")
    def __getattribute__(self, name):
        import time
        mytime=time.localtime()
        if name=="year":
            return "%u" %(mytime[0])
        elif name=="month":
            return "%u" %(mytime[1])
        elif name=="day":
            return "%u" %(mytime[2])
        elif name=="hour":
            return "%u" %(mytime[3])
        elif name=="minute":
            return "%u" %(mytime[4])
        elif name=="second":
            return "%u" %(mytime[5])
        else:
            return super(Test_HP_EVA_Controllertime, self).__getattribute__(name)
class Test_HP_EVA_Storagecell_HSV110(HP_EVA_Storagecell_HSV110):
    def __init__(self, params=None):
        super(Test_HP_EVA_Storagecell_HSV110, self).__init__()
#        self.objecttype=HP_EVA_Object.getObjectType(HP_EVA_StorageCell)
        self.objectwwn="5000-1FE1-FFFF-FFFF"
        self.objectid="08000".ljust(34,"F")+"1"
        self.objectname="EVA1"
        self.storagesystemcontrollermemory="512"
        self.storagesystemcontrollercachememory="2048"
        self.uid="8.7.16.%s.%s.%s.%s" %("".ljust(10, "9"), "".ljust(7, "9"), "".ljust(5, "9"), "".ljust(7, "9"))
        self.operationalstate= "good"
        self.operationalstatedetail="initialized_ok"
        self.comments=""
        self.hexuid="6005-%s-%s-%s-%s-%s-%s-%s" %("".ljust(4, "F"), "".ljust(4, "F"), "".ljust(4, "F"), "".ljust(4, "F"), "".ljust(4, "F"), "".ljust(4, "F"), "".ljust(4, "F"))
        self.objectparentuid="0.0.0.0.0.0.0"
        self.objectparenthexuid="0000-0000-0000-0000-0000-0000-0000-0000"
        self.objectparentid="0000000000000000000000000000000000000000"
        self.controllertime=Test_HP_EVA_Controllertime()
        self.deviceadditionpolicy="manual"
        self.volumereplacementdelay="60"
        self.firmwareversion="3028"
        self.nscfwversion="CR0A3Evcsp-3028"
        self.basiclicensed="true"
        self.drmlicensed="true"
        self.snaplicensed="true"
        # Whatever a statestring is
        self.statestring="13,14,13,20,8,8,8,8,8,14,8,8"

def main():
#    ComLog.setLevel(logging.INFO)
    print "Testing HP_Object..."
    print "Creating an HP_EVA"
    eva=Test_HP_EVA_Storagecell_HSV110()
    print "Eva: %s" %(eva)
    print "Adding a Vdisk to the eva..."
    vdisk=HP_EVA_Virtualdisk(objectid="DC200".ljust(34,"F")+"1", objectname= "vdisk1")
    eva.addVdisk(vdisk)
    print "Eva:"
    print eva
    print "Vdisk:"
    print vdisk
    print "In XML: "
    from xml.dom.ext import PrettyPrint
    print "Eva:"
    PrettyPrint(eva.toXML())
    print "Vdisk:"
    PrettyPrint(vdisk.toXML())
    print "Delete Vdisk:"
    eva.delVdisk(vdisk)
    print "Eva:"
    PrettyPrint(eva.toXML())

    testHP_ObjectFromXML("./test/system_dump.xml")
    testHP_ObjectFromXML("./test/vdisk_dump.xml")
    testHP_ObjectFromXML("./test/snapshot_dump.xml")
    testHP_ObjectFromXML("./test/diskgroup_dump.xml")
    testHP_ObjectFromXML("./test/lun_dump.xml")
    testHP_ObjectFromXML("./test/presentations_dump.xml", False)
    print "Testing factory via map:"
    vdisk=HP_EVA_Object(classtype="vdisk", objectid="DC200".ljust(34,"F")+"2", objectname="vdisk2")
    print "Vdisk:"
    print vdisk
    param="objectid"
    print "hasattr(%s): %s" %(param, hasattr(vdisk, param))
    print "getattr(%s): %s" %(param, getattr(vdisk, param))
    print "Objectid: "+vdisk.objectid

def testHP_ObjectFromXML(filename, xml=True):
    from xml.dom.ext.reader import Sax2
    from xml.dom.ext import PrettyPrint
    reader=Sax2.Reader(validate=0)
    xml_dump=open(filename,"r")
    print "From XML(%s):" %(filename)
    document=reader.fromStream(xml_dump)
    xml_dump.close()
    print "The HP_Oject:"
    result=HP_EVA_Object.fromXML(document.documentElement)
    print "Class: %s" %(result.__class__)
    if xml:
        PrettyPrint(result.toXML())
    else:
        print result
    return result

if __name__ == '__main__':
    try:
        main()
    except ComExceptions.ComException, e:
        import sys
        sys.stderr.write(e.__str__())

########################
# $Log: ComHP_EVA.py,v $
# Revision 1.3  2007-04-04 12:37:07  marc
# MMG Backup Legato Integration :
# - extended testing
#
# Revision 1.2  2007/03/26 08:09:28  marc
# - removed some logging
# - fixed a bug for referencing Paths with "\"s instead of "/"s
#
# Revision 1.1  2007/02/09 11:36:16  marc
# initial revision
#