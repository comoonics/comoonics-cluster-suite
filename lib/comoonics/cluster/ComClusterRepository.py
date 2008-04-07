"""Comoonics clusterRepository object module


Represents a given clusterconfiguration as an 
L{DataObject} and Maps of L{ClusterNode}. Also 
includes some methods for simple queries and 
provides generall query functionality by been 
inherited from L{DataObject}.

"""


# here is some internal information
# $Id: ComClusterRepository.py,v 1.8 2008-04-07 09:45:22 andrea2 Exp $
#


__version__ = "$Revision: 1.8 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/ComClusterRepository.py,v $

import os

from xml import xpath
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml.dom.ext.reader.Sax2 import implementation

from comoonics.cluster.ComClusterNode import ClusterNode

from comoonics.ComDataObject import DataObject
from comoonics import ComLog
from comoonics.ComExceptions import ComException

class ClusterMacNotFoundException(ComException): pass

def searchDict(myhash,searchedElement):
    """
    Searches for a given key in a nested dictionary
    @param myhash: Dictionary to seach in
    @type myhash: L{dict}
    @param searchedElement: key to search for
    """
    for (key, value) in myhash.items():
        if key == searchedElement:
            return True
        else:
            #dicts are used to represent the different layers in the (later) xml
            if type(value) == dict:
                if searchDict(value,searchedElement) == True: return True
            #list are used to define more than one element with same name
            elif type(value) == list:
                for element in value:
                    if searchDict(element,searchedElement) == True: return True
    return False

def applyDefaults(hash,defaults,clusternodeelement=None,numberofnodes=None):
    """
    Applies default values to a given hash. Hash and default values 
    has to be available as a dict with the same structure.
    @param hash: hash to apply defaults to
    @type hash: L{dict}
    @param defaults: defaults to apply
    @type defaults: L{dict}
    """
    for (key,value) in defaults.items():
        # if hash does not contain any value for a key defined in default, use 
        # key/value pair from defaults
        if not hash.has_key(key):
            hash[key] = value
        # if a nested structure is found, continue recursively
        elif type(defaults[key]) == dict and type(hash[key]) == dict:
            hash[key] = applyDefaults(hash[key],defaults[key],clusternodeelement,numberofnodes)
        # a special nested structure, used to handle elements whose names appear 
        # several times on the same level
        # split list and for each continue recursively
        elif type(defaults[key]) == list and type(hash[key]) == list:
            if len(hash[key]) < numberofnodes and key == clusternodeelement:
                for i in range(numberofnodes - len(hash[key])):
                    hash[key].append(defaults[key][0])
            for i in range(len(hash[key])):
                hash[key][i] = applyDefaults(hash[key][i],defaults[key][0],clusternodeelement,numberofnodes)
        # if hash already contains a value which is defined in defaults, pass default 
        # value and keep hash value
        elif type(defaults[key]) == type(hash[key]):
            pass
        # if type(defaults[key]) == type(hash[key]) which was queried above is false, 
        # the structure of hash and defaults differ - this is not allowed!
        else:
            raise AttributeError("Structure of given hash " + str(hash) + " and defaults " + str(defaults) + " differs, could not proceed")
            
    return hash
        
                
class ClusterRepository(DataObject):
    """
    Provides generall functionality for a clusterrepository instance
    """

    log = ComLog.getLogger("comoonics.cluster.ComClusterRepository")

    def __new__(cls, *args, **kwds):
        """
        Decides by type of given clustermetainfo which 
        instance of clusterrepository (general, redhat 
        or comoonics) has to be created.
        args = (element,doc,options)
        """
        if len(args) >= 2:
            if (args[0] != None):                
                if xpath.Evaluate("/cluster/clusternodes/clusternode/com_info", args[0]) or len(args[2]) == 0:
                    cls = ComoonicsClusterRepository
                elif xpath.Evaluate("/cluster/clusternodes/clusternode", args[0]):
                    cls = RedhatClusterRepository
                    
            elif type(args[2]) == dict:                
                if searchDict(args[2],"com_info"):
                    cls = ComoonicsClusterRepository
                elif searchDict(args[2],"clusternode"):
                    cls = RedhatClusterRepository
                
                                    
        return object.__new__(cls, *args, **kwds)
    
    def __init__(self, element=None, doc=None, *options):
        #node dictionaries depend on clustertype, setting later!
        self.nodeNameMap = {}
        self.nodeIdMap = {}
        
        super(ClusterRepository, self).__init__(element, doc)
        
    
class RedhatClusterRepository(ClusterRepository):
    """
    Represents the clusterconfiguration file of an redhat 
    cluster as an L{DataObject}. Extends generall 
    clusterrepository by special queries for this cluster 
    type.
    """
    
    defaultcluster_path = "/cluster"
    defaultclusternode_path = defaultcluster_path + "/clusternodes/clusternode"
    
    def __init__(self, element=None, doc=None, *options):
        if ((element == None) and (len(options) == 0)) or ((element != None) and (len(options) != 0)):
            raise AttributeError("You have to specify element OR options to create a new element")
        elif element == None:
            """
            if no element is given create a "default" cluster.conf is generated from given hash
            """
            if len(options) == 2:
                doc = self.createDomFromHash(options[0],defaults=options[1])
            if len(options) == 3:
                doc = self.createDomFromHash(options[0],defaults=options[1],numberofnodes=options[2])
            else:
                doc = self.createDomFromHash(options[0])
            element = xpath.Evaluate("/cluster", doc)[0]

        super(RedhatClusterRepository, self).__init__(element, doc)
        
        #fill dictionaries with nodename:nodeobject, nodeid:nodeobject and nodeident:nodeobject
        _nodes = xpath.Evaluate(self.defaultclusternode_path, self.getElement())
        for i in range(len(_nodes)):
            _node = ClusterNode(_nodes[i], self.getElement())
            self.nodeNameMap[_node.getName()] = _node
            self.nodeIdMap[_node.getId()] = _node
            
    def setClusterName(self,name):
        """
        @param: new clustername
        @type: string
        """
        self.log.debug("set name attribute to: " + str(name))
        #no try-except construct because name ist an obligatory object
        return self.setAttribute("name",name)

    def getClusterName(self):
        """
        @return: clustername
        @rtype: string
        """
        _clustername =  xpath.Evaluate(self.defaultcluster_path, self.getElement())[0]
        return _clustername.getAttribute("name")


    def getNodeName(self, mac):
        """
        @param mac: Macaddress of node
        @type mac: L{string}  
        @return: Nodename
        @rtype: string
        @raise ClusterMacNotFoundException: Raises Exception if search for node with given mac failed.
        """
        for node in self.nodeIdMap.values():
            try:
                self.log.debug("get clusternodenic belonging to given mac: " + str(mac))
                node.getNic(mac)
                self.log.debug("get name belonging to searched clusternodenic: " + node.getName())
                return node.getName()
            except KeyError:
                continue
        raise ClusterMacNotFoundException("Cannot find device with given mac: " + str(mac))

    def setConfigVersion(self,version):
        """
        @param: new clustername
        @type: string
        """
        self.log.debug("set version attribute to: " + str(version))
        #no try-except construct because name ist an obligatory object
        return self.setAttribute("config_version",version)

    def getConfigVersion(self):
        """
        @return: clustername
        @rtype: string
        """
        self.log.debug("get version attribute: " + self.getAttribute("config_version"))
        #no try-except construct because name ist an obligatory object
        return self.getAttribute("config_version")
    
    def getNodeId(self, mac):
        """
        @return: Nodeid
        @rtype: int
        @raise ClusterMacNotFoundException: Raises Exception if search for node with given mac failed.
        """
        for node in self.nodeIdMap.values():
            #if node does not match given mac, test next node
            try:
                self.log.debug("get clusternodenic belonging to given mac: " + mac)
                node.getNic(mac)
                self.log.debug("get id belonging to searched clusternodenic: " + node.getName())
                return node.getId()
            except KeyError:
                continue
        raise ClusterMacNotFoundException("Cannot find device with given mac: " + mac)
    
    def createDomFromHash(self,hash,doc=None,element=None,defaults=None,clusternodeelementname="clusternode",numberofnodes=None):
        """
        Creates or manipulates a DOM (cluster.conf) from given hash.
        @param hash: Hash to create DOM
        @type hash: L{dict}
        @param doc: if given, expand with content from hash
        @type doc: L{DOM}
        @param element: element in doc to work on
        @param clusternodeelementname: define element which includes clusternodes, default is clusternodes
        @type clusternodeelementname: L{string}
        @return: XML-Dom-Element created from hash
        @rtype: L{DOM}
        """
        if defaults != None:
            hash = applyDefaults(hash, defaults, clusternodeelementname, numberofnodes)
          
        if doc==None:            
            doc = implementation.createDocument(None,hash.keys()[0],None)
            newelement = doc.documentElement                
        else:
            newelement = doc.createElement(hash.keys()[0])                    
            element.appendChild(newelement)
            
        _tmp = hash[hash.keys()[0]]
        for i in _tmp.keys():
            #if i == clusternodeselementname:
            #    nodeselement = doc.createElement(clusternodeselementname)                    
            #    newelement.appendChild(nodeselement)
            #    nodes = self.createClusterNodesElement(_tmp[i],doc,nodeselement)
            #    for node in nodes:
            #        nodeselement.appendChild(node)
            #elif (type(_tmp[i]) != dict) and (type(_tmp[i]) != list):
            if (type(_tmp[i]) != dict) and (type(_tmp[i]) != list):
                newelement.setAttribute(str(i),str(_tmp[i]))
            elif type(_tmp[i]) == list:
                for element in _tmp[i]:
                    self.createDomFromHash({i:element},doc,newelement)
            else:
                _tmp2 = {i: _tmp[i]}
                self.createDomFromHash(_tmp2,doc,newelement)
        
        return doc
    
    def createClusterNodesElement(self,myhash,doc=None,element=None,initial=True):
        """
        Creates or manipulates a Nodeelement from given hash to include in a DOM (cluster.conf)
        @param myhash: Hash to create DOM
        @type myhash: L{dict}
        @param doc: if given, expand with content from hash
        @type doc: L{DOM}
        @param element: element in doc to work on
        @param clusternodeelementname: define element which includes clusternodes, default is clusternodes
        @type clusternodelementname: L{string} 
        """
        for key, value in myhash.items():
            # if initial is set, create the clusternode "root"element and use it as initial point
            if initial:
                newelement = doc.createElement(key)
            # if initial is not set use the given element as initial point
            else:
                newelement = element

            # if value is no dict (=> subordinate element) or 
            # list (=> subordinate element with multiple apereance)
            # assume that value must be an attribute of the actuall element            
            if (type(value) != dict) and (type(value) != list):
                newelement.setAttribute(key,str(value))
            # if value is of type dict and initial is not set
            # create and append a subordinate element with name value
            # if initial is true the element has been already created
            elif not initial and (type(value) == dict):
                # nodeelement will be the "working-on" element for the next recursion level
                # if value is of type dict it must be an new element with name key
                nodeelement = doc.createElement(key)                    
                newelement.appendChild(nodeelement)
            else:
                # nodeelement will be the "working-on" element for the next recursion level
                # if type of value is not dict or initial is set use the actual working-on 
                # element as nodeelement
                nodeelement = newelement
                
            _tmp = []
            # if more than one clusternode are defined, build them in rotation
            if (type(value) == list) and initial:
                for i in value:
                    _tmp.append(self.createClusterNodesElement({key:i},doc,element,True))
                return _tmp
            # if an element of the clusternode has multiple apereance, build the elements in rotation
            elif type(value) == list and not initial:
                for i in value:
                    self.createClusterNodesElement({key:i},doc,element,False)
            elif type(value) == dict:
                self.createClusterNodesElement(value,doc,nodeelement,False)
        
        return newelement

class ComoonicsClusterRepository(RedhatClusterRepository):
    """
    Represents the clusterconfiguration file of an 
    comoonics cluster as an L{DataObject}.
    """
    def __init__(self, element=None, doc=None, *options):
        if ((element == None) and (len(options) == 0)) or ((element != None) and (len(options) != 0)):
            raise AttributeError("You have to specify element OR filename attribute")
        else:
            super(ComoonicsClusterRepository, self).__init__(element, doc, *options)
        
                    
def main2():
    ComLog.setLevel(ComLog.logging.INFO)
    
    defaults = {"cluster":{"config_version":"1", "name":"clurhel5",
                                    "cman":{"expected_votes":"1", "two_node":"0"},
                                    "clusternodes":
                                     {"clusternode":[
                                       {"nodeid":"1", "name":"gfs-node1", "votes":"1",
                                          "com_info":{
                                            "syslog":{"name":"gfs-node1"},
                                            "rootvolume":{"name":"/dev/VG_SHAREDROOT/LV_SHAREDROOT"},
                                            "eth":[{"ip":"10.0.0.1", "murks":"bla", "gateway":"192.168.1.1", "name":"eth0", "mac":"00:00:00:00:00:00", "mask":"255.255.255.0"}],
                                            "fenceackserver":{"passwd":"XXX", "user":"root"}},
                                          "fence":{"method":{"name":"1"}}}]},
                                    "fencedevices":{},
                                    "rm":{"failoverdomains":{},"resources":{}}}}
    
    hash = {"cluster":{"name":"myCluster",
                                    "cman":{"expected_votes":"2", "two_node":"0"},
                                    "clusternodes":
                                     {"clusternode":[
                                       {"nodeid":"1", "name":"gfs-node1", "votes":"2",
                                          "com_info":{
                                            "syslog":{"name":"gfs-node1"},
                                            "rootvolume":{"name":"/dev/VG_SHAREDROOT/LV_SHAREDROOT"},
                                            "eth":[
                                              {"ip":"10.0.0.1", "gateway":"1.2.3.4", "name":"eth0", "mac":"00:0C:29:3B:XX:XX", "mask":"255.255.255.0"},
                                              {"ip":"10.0.0.9", "gateway":"", "name":"eth1", "mac":"01:0C:29:3B:XX:XX", "mask":"255.255.255.0"}],
                                            "fenceackserver":{"passwd":"XXX", "user":"root"}},
                                          "fence":{"method":{"name":"1"}}},
                                       {"nodeid":"2", "name":"gfs-node2", "votes":"2",
                                          "com_info":{
                                            "syslog":{"name":"gfs-node1"},
                                            "rootvolume":{"name":"/dev/VG_SHAREDROOT/LV_SHAREDROOT"},
                                            "eth":[
                                              {"ip":"10.0.0.2", "gateway":"1.2.3.4", "name":"eth0", "mac":"00:1C:29:3B:XX:XX", "mask":"255.255.255.0"},
                                              {"ip":"10.0.0.3", "gateway":"", "name":"eth1", "mac":"01:2C:29:3B:XX:XX", "mask":"255.255.255.0"}],
                                            "fenceackserver":{"passwd":"XXX", "user":"root"}},
                                          "fence":{"method":{"name":"1"}}}]},
                                    "fencedevices":{},
                                    "rm":{"failoverdomains":{},"resources":{}}}}
    
    _tmp = ClusterRepository(None,None,hash,defaults)
    
    
    #print str(searchDict(hash,"nodeid"))
    
    print str(type(_tmp))
    PrettyPrint(_tmp.getDocument())
    
    import fcntl
    filename = "test/test.conf"
    conf = file(filename,"w+")
    fcntl.lockf(conf,fcntl.LOCK_EX)
    PrettyPrint(_tmp.getDocument(), conf)
    fcntl.lockf(conf,fcntl.LOCK_UN)
    conf.close()    
    
    print
    
    _tmp2 = {"cluster":{"config":"1"},"clusternodes":[{"node1":"node1"}],"default":"default"}
    _tmp1 = {"cluster":{"config":"2","name":"myName"},"clusternodes":[{"mynode1":"mynode1"},{"mynode2":"mynode2"}],"extra":"extra"}
    
    print "\n" + str(applyDefaults(_tmp1, _tmp2))
    
def main():
    """
    Method to test module. Creates a ClusterRepository object, prints defined hashmaps 
    and test getting of nodename and nodeid of nodes defined in a example cluster.conf.
    """
    # create Reader object
    reader = Sax2.Reader()

    #parse the document and create clusterrepository object
    my_file = os.fdopen(os.open("test/cluster2.conf", os.O_RDONLY))
    doc = reader.fromStream(my_file)
    my_file.close()
    element = xpath.Evaluate("/cluster", doc)[0]

    #create clusterRepository Object
    clusterRepository = ClusterRepository(element, doc)
    
    print "Dictionary Nodeid:Nodeobject"
    print clusterRepository.nodeIdMap
    print "\nDictionary Nodename:Nodeobject"
    print clusterRepository.nodeNameMap
    
    print "\nclusterRepository\n" + str(clusterRepository)
    print "Repositorytype Comoonics?: " + str(isinstance(clusterRepository, ComoonicsClusterRepository))
    
    for node in clusterRepository.nodeNameMap.values():
        print "Node " + str(node.getName())
        for nic in node.getNics():
            try:
                print "\tNic " + nic.getName() + ", mac " + nic.getMac()
                mac = nic.getMac()
                print "\tgetNodeName(mac): " + clusterRepository.getNodeName(mac)
                print "\tgetNodeId(mac): " + clusterRepository.getNodeId(mac) + "\n"
            except ClusterMacNotFoundException:
                print "\tNic " + nic.getName()
                print "\tVerify that no mac-address is specified for this nic"

if __name__ == '__main__':
    #main2()
    main()

# $Log: ComClusterRepository.py,v $
# Revision 1.8  2008-04-07 09:45:22  andrea2
# added searchDict, applyDefaults(apply defaultvalues to a hash), setConfigVersion, createDomFromHash, adds posibility to hand over a hash over to ClusterRepository
#
# Revision 1.7  2008/02/27 09:16:40  mark
# added getClusterName support
#
# Revision 1.6  2007/09/19 06:42:28  andrea2
# adapted source code in dependence on Python Style Guide, removed not used imports and statements
#
# Revision 1.5  2007/09/04 07:52:25  andrea2
# Removed unused variable
#
# Revision 1.4  2007/08/06 12:09:27  andrea2
# Added more Docu, removed ClusterMetainfo
#
# Revision 1.1  2007/06/05 13:11:21  andrea2
# *** empty log message ***
##
# Revision 0.1  2007/05/02 13:30:56  andrea
# inital version
#
