"""Comoonics clusterMetainfo object module


Manages needed Parameters which are not included 
in general clusterconfiguration and represents them 
as an L{DataObject}.

"""


# here is some internal information
# $Id: ComClusterMetainfo.py,v 1.1 2007-06-05 13:11:21 andrea2 Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/Attic/ComClusterMetainfo.py,v $

import os.path

from xml import xpath
from xml.dom.ext.reader import Sax2
from xml.dom.ext.reader.Sax2 import implementation

from comoonics.ComDataObject import DataObject

class ClusterMetainfo(DataObject):
    """
    Holds needed informations about cluster which are 
    not included in clusterrepository. Handels the informations  
    as an xml-object (implemented by inheritation of L{DataObject}).
    """
    def __new__(cls, *args, **kwds):
        """
        check type of given parameters or, if given, 
        content of metainfo to verify which type 
        of clustermetainfo must be created
        """
        if (type(args[0]).__name__ == "instance") and (len(args) <= 2) and args[0].getAttribute("node_prefix"):
            cls = ComoonicsClusterMetainfo
        elif (len(args) <= 3) and (type(args[0]).__name__ == ("str" or "int")):
            cls = ComoonicsClusterMetainfo
        return object.__new__(cls, *args, **kwds)
    
    def __init__(self,element,doc=None):
        super(ClusterMetainfo,self).__init__(element,doc)
        
class RedhatClusterMetainfo(ClusterMetainfo):
    """
    Extends L{ClusterMetainfo} with spezial informations 
    about a specific redhat cluster. Handels the informations  
    as an xml-object (implemented by inheritation of L{DataObject}).
    """
    def __init__(self,element,doc=None):
        super(RedhatClusterMetainfo,self).__init__(element,doc)
        
class ComoonicsClusterMetainfo(RedhatClusterMetainfo):
    """
    Extends L{RedhatClusterMetainfo} with spezial informations 
    about a specific comoonics cluster. Handels the informations  
    as an xml-object (implemented by inheritation of L{DataObject}).
    """
    def __init__(self,*params):
        if (type(params[0]).__name__ == "instance") and (len(params) <= 2) and (len(params) >= 1):
            #setting doc/element
            if (len(params) == 2):
                element = params[0]
                doc = params[1]
            else:
                element = params[0]
                doc = None
        elif len(params) <= 3:
            #using initializing via given parameters
            #defaultvalues, overwrite with given values
            node_prefix = "" #(node_prefix)
            use_nodeids = "False" #(use_nodeids)
            maxnodeidnum = "0" #(maxnodeidnum)
            if len(params) == 1:
                #only one parameter is given, use defaultvalues for others
                node_prefix = params[0]
            elif len(params) == 2:
                #two parameters are given, use defaultvalues for other
                node_prefix = params[0]
                use_nodeids = params[1]
            elif len(params) == 3:
                #three parameter are given, no need to use defaultvalues
                node_prefix = params[0]
                use_nodeids = params[1]
                maxnodeidnum = params[2]

            #create DOM-Element
            doc = implementation.createDocument(None,"clustermetainfo",None)
            topelement = doc.documentElement
            topelement.setAttribute("node_prefix",node_prefix)
            topelement.setAttribute("use_nodeids",use_nodeids)
            topelement.setAttribute("maxnodeidnum",maxnodeidnum)
            
            element = xpath.Evaluate('/clustermetainfo', doc)[0]
            
        else:
            raise IndexError('Index out of range for ComoonicsClusterMetainfo constructor (%u)' % len(params))
        
        super(ComoonicsClusterMetainfo,self).__init__(element,doc)
    
def main():
    parameter_Metainfo = ClusterMetainfo("Knoten_","True","11")
    print "node_prefix: " + str(parameter_Metainfo.getAttribute("node_prefix"))
    print "use_nodeids: " + str(parameter_Metainfo.getAttribute("use_nodeids"))
    print "maxnodeidnum: " + str(parameter_Metainfo.getAttribute("maxnodeidnum"))
    print parameter_Metainfo
    
    reader = Sax2.Reader()
    file = os.fdopen(os.open("test/metainfo.conf",os.O_RDONLY))
    doc = reader.fromStream(file)
    element = xpath.Evaluate('/clustermetainfo', doc)[0]
    file.close()
    
    elementDoc_Metainfo = ClusterMetainfo(element,doc)
    print "\nnode_prefix: " + str(elementDoc_Metainfo.getAttribute("node_prefix"))
    print "use_nodeids: " + str(elementDoc_Metainfo.getAttribute("use_nodeids"))
    print "maxnodeidnum: " + str(elementDoc_Metainfo.getAttribute("maxnodeidnum"))
    print elementDoc_Metainfo
    
    reader = Sax2.Reader()
    file = os.fdopen(os.open("test/metainfo2.conf",os.O_RDONLY))
    doc = reader.fromStream(file)
    element = xpath.Evaluate('/clustermetainfo', doc)[0]
    file.close()
    
    elementDoc_Metainfo2 = ClusterMetainfo(element,doc)
    try:
        print "\nnode_prefix: " + str(elementDoc_Metainfo2.getAttribute("node_prefix"))
    except NameError:
        print "\nnode_prefix: Value not set, OK!"
    try:
        print "use_nodeids: " + str(elementDoc_Metainfo2.getAttribute("use_nodeids"))
    except NameError:
        print "use_nodeids: Value not set, OK!"
    try:
        print "maxnodeidnum: " + str(elementDoc_Metainfo2.getAttribute("maxnodeidnum"))
    except NameError:
        print "maxnodeidnum: Value not set, OK!"
    print elementDoc_Metainfo

if __name__ == '__main__':
    main()

# $Log: ComClusterMetainfo.py,v $
# Revision 1.1  2007-06-05 13:11:21  andrea2
# *** empty log message ***
##
# Revision 0.1  2007/05/10 13:30:56  andrea
# inital version
#