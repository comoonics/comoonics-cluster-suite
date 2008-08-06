"""Comoonics clusterRepository object module


Represents a given clusterconfiguration as an 
L{DataObject} and Maps of L{ClusterNode}. Also 
includes some methods for simple queries and 
provides generall query functionality by been 
inherited from L{DataObject}.

"""


# here is some internal information
# $Id: ComClusterRepository.py,v 1.16 2008-08-06 11:18:28 marc Exp $
#


__version__ = "$Revision: 1.16 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/ComClusterRepository.py,v $

import os

from xml import xpath
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2

import comoonics.cluster

from ComClusterNode import ClusterNode
from ComClusterInfo import ClusterObject

from comoonics import ComLog
from comoonics.ComExceptions import ComException
from comoonics.DictTools import searchDict, applyDefaults, createDomFromHash

log = ComLog.getLogger("comoonics.cdsl.ComClusterRepository")

class ClusterMacNotFoundException(ComException): pass
class ClusterIdNotFoundException(ComException): pass
class ClusterRepositoryConverterNotFoundException(ComException): pass
                
class ClusterRepository(ClusterObject):
    """
    Provides generall functionality for a clusterrepository instance
    """
    log = ComLog.getLogger("comoonics.cdsl.ComClusterRepository")
    CONVERTERS=dict()

    def __new__(cls, *args, **kwds):
        """
        Decides by type of given clustermetainfo which 
        instance of clusterrepository (general, redhat 
        or comoonics) has to be created.
        args = (element,doc,options)
        """
        if len(args) >= 1 and isinstance(args[0], basestring):
            reader = Sax2.Reader()
            _xml=open(args[0])
            doc = reader.fromStream(_xml)
            _xml.close()
            x=xpath.Evaluate("/cluster/clusternodes/clusternode/com_info", doc.documentElement)
            if len(xpath.Evaluate("/cluster/clusternodes/clusternode/com_info", doc.documentElement)) > 0:
                cls = ComoonicsClusterRepository
            elif len(xpath.Evaluate("/cluster/clusternodes/clusternode", doc.documentElement)) > 0:
                cls = RedhatClusterRepository
        if len(args) >= 2:
            if (args[0] != None):                
                if xpath.Evaluate(comoonics.cluster.cominfo_path %"", args[0]) or len(args[2]) == 0:
                    cls = ComoonicsClusterRepository
                elif xpath.Evaluate(comoonics.cluster.clusternode_path %"", args[0]):
                    cls = RedhatClusterRepository
                    
            elif type(args[2]) == dict:                
                if searchDict(args[2],comoonics.cluster.cominfo_name):
                    cls = ComoonicsClusterRepository
                elif searchDict(args[2],comoonics.cluster.clusternode_name):
                    cls = RedhatClusterRepository
                
        return object.__new__(cls, *args, **kwds)
    
    def __init__(self, *params, **kwds):
        #node dictionaries depend on clustertype, setting later!
        self.nodeNameMap = {}
        self.nodeIdMap = {}
        
        super(ClusterRepository, self).__init__(*params, **kwds)
        
    def convert(self, _type="ocfs2"):
        if self.CONVERTERS.has_key(_type):
            return self.CONVERTERS[_type](self)
        else:
            raise ClusterRepositoryConverterNotFoundException("Could not find converter of clusterrepository for type %s" %_type)
            
class RedhatClusterRepository(ClusterRepository):
    """
    Represents the clusterconfiguration file of an redhat 
    cluster as an L{DataObject}. Extends generall 
    clusterrepository by special queries for this cluster 
    type.
    """
    
    defaultcluster_conf = "/etc/cluster/cluster.conf"
    defaultcluster_path = "/cluster"
    defaultclusternode_path = defaultcluster_path + "/clusternodes/clusternode"
    
    def __init__(self, element=None, doc=None, *options):
        if ((element == None) and (len(options) == 0)) or ((element != None) and (len(options) != 0)):
            raise AttributeError("You have to specify element OR options to create a new element")
        elif element == None:
            """
            if no element is given create a "default" cluster.conf is generated from given hash
            """
            if (len(options) == 2) or (len(options) == 3):
                doc = createDomFromHash(options[0],defaults=options[1])
            else:
                doc = createDomFromHash(options[0])
            element = xpath.Evaluate(comoonics.cluster.cluster_path, doc)[0]

        super(RedhatClusterRepository, self).__init__(element, doc)
        
        #fill dictionaries with nodename:nodeobject, nodeid:nodeobject and nodeident:nodeobject
        _nodes = xpath.Evaluate(comoonics.cluster.clusternode_path, self.getElement())
        for i in range(len(_nodes)):
            _node = ClusterNode(_nodes[i], doc)
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
        _clustername =  xpath.Evaluate(comoonics.cluster.cluster_path, self.getElement())[0]
        return _clustername.getAttribute("name")


    def getNodeName(self, mac):
        """
        @param mac: Macaddress of node
        @type mac: L{string}  
        @return: Nodename
        @rtype: string
        @raise ClusterMacNotFoundException: Raises Exception if search for node with given mac failed.
        """
        self.log.debug("get clusternodenic belonging to given mac: " + str(mac))
        for node in self.nodeIdMap.values():
            try:
                node.getNic(mac)
                self.log.debug("get name belonging to searched clusternodenic: " + node.getName())
                return node.getName()
            except KeyError:
                continue
        raise ClusterMacNotFoundException("Cannot find device with given mac: " + str(mac))

    def getNodeNameById(self, _id):
        """
        @param id: id of node
        @type int
        @return: Nodename
        @rtype: string
        @raise ClusterIdNotFoundException: Raises Exception if search for node with given mac failed.
        """
        if self.nodeIdMap.has_key(_id):
            return self.nodeIdMap.get(_id).getName()
        
        raise ClusterIdNotFoundException("Cannot find node with id " + str(id))

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
        #FIXME: config_version hardcoded
        self.log.debug("get version attribute: " + self.getAttribute("config_version"))
        #no try-except construct because name is an obligatory object
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

    def createOCFS2ClusterConf(clusterRepository):
        """
        returns a string containing a valid OCFS2 cluster configuration
        """
        __NODE_TMPL__="""
node:
        ip_port = %(tcp_port)u
        ip_address = %(ip_address)s
        number = %(nodeid)s
        name = %(name)s
        cluster = %(clustername)s
"""
        __CL_TMPL__="""
cluster:
        node_count = %(nodecount)u
        name = %(clustername)s
"""
        import StringIO

        output = StringIO.StringIO()

        _nodehash=dict()
        for _node in clusterRepository.nodeIdMap.values():
            _nodehash.clear()
            _nodehash["tcp_port"]=int(_node.getAttribute("tcp_port", "7777"))
            _nodehash["clustername"]=clusterRepository.getClusterName()
            _nodehash["nodeid"]=_node.getId()
            _nodehash["name"]=_node.getName()
            _nodehash["ip_address"]=_node.getIPs()[0]
            #for _nic in _node.getNics():
            #    _ip=_nic.getIP()
            #    if _ip != "":
            #        _nodehash["ip_address"]=_ip
            output.write(__NODE_TMPL__ %_nodehash)
        _clusterhash=dict()
        _clusterhash["nodecount"]=len(clusterRepository.nodeIdMap.keys())
        _clusterhash["clustername"]=clusterRepository.getClusterName()
        output.write(__CL_TMPL__ %_clusterhash)
        
        return output.getvalue()
    
    createOCFS2ClusterConf=staticmethod(createOCFS2ClusterConf)

ClusterRepository.CONVERTERS["ocfs2"]=ComoonicsClusterRepository.createOCFS2ClusterConf
                    
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
    
    print "type should be comoonicsClusterRepository: " + str(type(_tmp))
    PrettyPrint(_tmp.getDocument())
    
    import fcntl
    filename = "test/test.conf"
    conf = file(filename,"w+")
    fcntl.lockf(conf,fcntl.LOCK_EX)
    PrettyPrint(_tmp.getDocument(), conf)
    fcntl.lockf(conf,fcntl.LOCK_UN)
    conf.close()
    
    _tmp2 = {"cluster":{"config":"1"},"clusternodes":[{"node1":"node1"}],"default":"default"}
    _tmp1 = {"cluster":{"config":"2","name":"myName"},"clusternodes":[{"mynode1":"mynode1"},{"mynode2":"mynode2"}],"extra":"extra"}
    
    print "Test applyDefaults, should contain default and extra: " + str(applyDefaults(_tmp1, _tmp2))
    print "End of main2()"
    
def main():
    """
    Method to test module. Creates a ClusterRepository object, prints defined hashmaps 
    and test getting of nodename and nodeid of nodes defined in a example cluster.conf.
    """
    
    # create Reader object
    reader = Sax2.Reader()

    #parse the document and create clusterrepository object
    my_file = os.fdopen(os.open("test/cluster3.conf", os.O_RDONLY))
    doc = reader.fromStream(my_file)
    my_file.close()
    element = xpath.Evaluate(comoonics.cluster.cluster_path, doc)[0]

    #create clusterRepository Object
    clusterRepository = ClusterRepository(element, doc)
    nodevalues = {"clusternode":{"name":"mynode","nodeid:":"3","com_info":{"eth":[{"name":"eth5"}]}}}
    clusterRepository.addClusterNode(nodevalues)
    PrettyPrint(clusterRepository.element)
    return
    
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
                
    print "Generating ocfs2 configuration"
    print clusterRepository.convert("ocfs2")

if __name__ == '__main__':
    import logging
    ComLog.setLevel(logging.DEBUG)
    main2()
    main()

# $Log: ComClusterRepository.py,v $
# Revision 1.16  2008-08-06 11:18:28  marc
# - fixed more bugs with xpath
#
# Revision 1.15  2008/08/05 18:28:18  marc
# more bugfixes
#
# Revision 1.14  2008/08/05 13:09:40  marc
# - fixed bugs with constants
# - optimized imports
# - added nonstatic attributes
# - added helper class
#
# Revision 1.13  2008/07/08 07:34:30  andrea2
# Improved imports (no imports with *), sourced out dict-tools, sourced out validate_xml to xmltools, use constants (xpath, filenames) from __init__
#
# Revision 1.12  2008/06/17 16:22:55  mark
# added support for query nodenamebyid. This is needed for passing the nodeid as boot parameter.
#
# Revision 1.11  2008/06/10 10:16:15  marc
# - added ClusterConf conversion
#
# Revision 1.10  2008/06/04 10:28:28  marc
# - added ocfs2config creation
#
# Revision 1.9  2008/05/20 11:14:39  marc
# - Error better readable
#
# Revision 1.8  2008/04/07 09:45:22  andrea2
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
