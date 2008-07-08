"""Comoonics cdslrepository object module


Represents cdsl-inventoryfile as an L{DataObject} and holds list 
of cdsl objects. The cdsl-inventoryfile contains information about 
the created cdsls and default values which are needed for cdsl 
management (modifying, creating, deleting).

"""


__version__ = "$Revision: 1.7 $"

import fcntl # needed for filelocking
import time  # needed for creation of timestamp
import logging
import re

import xml
from xml import xpath
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml.dom.ext.reader.Sax2 import implementation

from ComCdsl import Cdsl

from comoonics import ComLog
from comoonics.ComExceptions import ComException
from comoonics.ComDataObject import DataObject
from comoonics import ComSystem

from comoonics.cluster.ComClusterInfo import ClusterInfo
from comoonics.cluster.ComClusterRepository import ClusterRepository

import comoonics.pythonosfix as os

log = ComLog.getLogger("comoonics.cdsl.ComCdslRepository")

class CdslRepositoryCdslNotFoundException(ComException):pass
class CdslRepositoryNotConfigfileException(ComException):pass

class inventoryfileProcessing:
    """
    Provides funcionality for easy using filelocking with xml-files. Helps to provide 
    files from getting inconsitence because they are modified from more than one source 
    at the same time.
    
    """
    def __init__(self, filename, dtd=None):
        """
        Sets used filename, because it must be available for all methods
        @param dtd: Sets DTD to given path if a new xml-document has to be created. 
        No consequence if file to open already exists. Default None
        @type dtd: String
        """
        self.filename = filename
        self.dtd = dtd
        
    def openLock(self,validate=True):
        """
        Open and locks given xml-file with fcntl. If file does not already exist, create it.
        @param validate: Uses validation for xml-document if True, default True
        @type validate: Boolean
        @return: Dom-Object of locked file
        @rtype: Dom-Object
        """
        cdsls_path = "cdsls"
        configVersion = "1"
          
        #create minimal cdsl-configfile if it doesn't exist
        #use exclusive filelocking to avoid competively access to file
        if not os.path.isfile(self.filename):
            #create xml and include path to dtd
            if self.dtd!=None and os.path.exists(self.dtd):
                doct=implementation.createDocumentType(cdsls_path,None,os.path.abspath(self.dtd))
                doc=implementation.createDocument(None,cdsls_path,doct) 
            else:
            #create xml without specifying dtd
                doc = implementation.createDocument(None,cdsls_path,None)
            topelement=doc.documentElement
            topelement.setAttribute("config_version",configVersion)

            #save generated DOM to inventoryfile
            if not os.path.exists(os.path.dirname(self.filename)):
                log.debug("Create needed directories for inventoryfile: " + os.path.dirname(self.filename))
                os.makedirs(os.path.dirname(self.filename))
            conf = file(self.filename,"w+")
            fcntl.lockf(conf,fcntl.LOCK_EX)
            PrettyPrint(doc, conf)
            fcntl.lockf(conf,fcntl.LOCK_UN)
            conf.close()
            
            #Set validate to False, because created file cannot accomplish the 
            #requirements for validation.
            validate = False
        
        reader = Sax2.Reader(validate)
        
        #use exclusive filelocking to avoid competively access to file
        self.conf = file(self.filename,"r+")
        fcntl.lockf(self.conf ,fcntl.LOCK_EX)
        
        try:
            doc = reader.fromStream(self.conf)
        except xml.sax._exceptions.SAXParseException, arg:
            log.critical("Problem while reading XML: " + str(arg))
            raise
        
        return doc

    def prettyprintUnlockClose(self,doc=None):
        """
        Writes given xml to file, unlock it via fcntl and close.
        @param doc: Content to write back to locked file (overwrites existing content!), if None only unlock and close
        @type doc: DOM-Object
        """
        
        if doc != None:
            #prepare file for writing (delete content)
            self.conf.truncate(0)
            self.conf.seek(0)
        
            #write new xml to file
            PrettyPrint(doc,self.conf)
        
            #flush conf to avoid problems if file is changed between unlocking and closing
            self.conf.flush()
        
        fcntl.lockf(self.conf,fcntl.LOCK_UN)        
        self.conf.close()

class CdslRepository(DataObject):
    DEFAULT_INVENTORY="/var/lib/cdsl/cdsl_inventory.xml"
    """
    Represents cdsl-inventoryfile as L{DataObject}
    """
    #duplicate definition at __new__, because there self.* could not be used
    cdsls_path = "/cdsls"
    cdslDefaults_path = cdsls_path + "/defaults"
    cdsltree = "cdsltree"
    
    log = ComLog.getLogger("comoonics.cdsl.ComCdslRepository")

    def __new__(cls, *args, **kwds):
        """
        Decide which type of CdslRepository is needed to create by verifying 
        the type of given inventoryfile or number of given options.
        If an not known type is given, a instance of the default class 
        L{CdslRepository} will be created.
        @return: a new CdslRepository object 
        @rtype: depending on defind defaults of configfile
        """
        #duplicate definition at beginn of class, because self.* could not be used here
        cdsls_path = "/cdsls"
        cdslDefaults_path = cdsls_path + "/defaults"
        cdsltree = "cdsltree"
        
        #concate root & given filename
        if len(args) >= 7 and args[8] != None:
            filename = os.path.join(args[8],re.sub('^/','', args[0]))
        else:
            filename = args[0]
        
        if os.path.exists(filename):
            reader = Sax2.Reader(validate=False)
            file = os.fdopen(os.open(filename,os.O_RDONLY))
            try:
                _tmp = reader.fromStream(file)
            except xml.sax._exceptions.SAXParseException, arg:
                log.critical("Problem while reading XML: " + str(arg))
                raise
        
        #if configfile is set but options is not specified
        if len(args) >= 1 and len(args) <= 3 and os.path.exists(filename):
            if xpath.Evaluate("%s[@%s]" %(cdslDefaults_path,cdsltree), _tmp):
                cls = ComoonicsCdslRepository
            elif not xpath.Evaluate(cdsls_path , _tmp):
                raise CdslRepositoryNotConfigfileException("Given file " + filename + " could not be a valid inventory, because xpath " + cdsls_path + " could not be found.")
        #if options are used it must be a comoonics cdsl
        elif len(args) >= 4:
            if os.path.exists(filename):
                if not xpath.Evaluate("%s[@%s]" %(cdslDefaults_path,cdsltree), _tmp):
                    raise CdslRepositoryNotConfigfileException("Given file " + filename + " could not be a valid ComoonicsInventory, because xpath " + cdslDefaults_path + "[@" + cdsltree + "] could not be found.")
            #look for com.oonics specific arguments
            cls = ComoonicsCdslRepository
        
        return object.__new__(cls, *args, **kwds)
    
    def __init__(self, configfile=DEFAULT_INVENTORY, dtd=None, validate=True, *options):
        """
        Constructs a new CdslRepository from given configfile. Creates 
        a list of cdsls from configfile to provide an easy access to them.
        @param configfile: path to configfile, should be created if it does not already exist (Default: /var/lib/cdsl/cdsl_inventory.xml)
        @type configfile: string
        @param dtd: path to dtd used with configfile (Default: None)
        @type dtd: string
        @param validate: set to false to skip validation of configfile (Default: True)
        @type validate: Boolean
        @param options: not used yet
        """       
        self.configfile = configfile
        self.cdsls = []
        self.validate = validate
        import xml
        reader = Sax2.Reader(self.validate)
        file = os.fdopen(os.open(self.configfile,os.O_RDONLY))
        try:
            doc = reader.fromStream(file)
        except xml.sax._exceptions.SAXParseException, arg:
            log.critical("Problem while reading XML: " + str(arg))
            raise
        element = xpath.Evaluate(self.cdsls_path, doc)[0]
        file.close()
        
        super(CdslRepository,self).__init__(element, doc)
        
    def buildInfrastructure(self,clusterinfo):
        """
        Placeholder for Method to prepare cluster 
        to handle cdsls
        @param clusterinfo: Clusterinfo with needed attributes
        @type clusterinfo: L{ComoonicsClusterInfo}
        """
        pass
        
class ComoonicsCdslRepository(CdslRepository):
    """
    Represents cdsl-inventoryfile and provides methods to add, modify or delete 
    entries. Theres also the possibility to check if an given cdsl is included in 
    the inventoryfile and some methods to return the default values which are 
    defined at the bottom of the file.

    Additional a method provides the functionality to build the needed 
    infrastructure which is needed to create cdsls.
    """
    
    cdsls_element = "cdsls"
    
    cdsl_element = "cdsl"
    cdsl_type_attribute = "type"
    cdsl_src_attribute = "src"
    cdsl_time_attribute = "timestamp"
    
    defaults_element = "defaults"
    defaults_cdsltree_attribute = "cdsltree"
    defaults_cdsltreeShared_attribute = "cdsltree_shared"
    defaults_cdslLink_attribute = "cdsl_link"
    defaults_maxnodeidnum_attribute = "maxnodeidnum"
    defaults_useNodeids_attribute = "use_nodeids"
    #defaults_root_attribute = "root"
    defaults_mountpoint_attribute = "mountpoint"
    defaults_defaultDir_attribute = "default_dir"
    defaults_nodePrefix_attribute = "node_prefix"
    
    #definde defaultvalues
    cdsltree_default = "cluster/cdsl"
    cdsltreeShared_default = "cluster/shared"
    cdslLink_default = "/cdsl.local"
    maxnodeidnum_default = "0"
    useNodeids_default = "False"
    
    nodes_element = "nodes"
    noderef_element = "noderef"
    noderef_ref_attribute = "ref"
    
    nodesdefault_element = "nodesdefault"
    
    nodedefault_element = "nodedefault"
    nodedefault_id_attribute = "id"
    
    #define needed pathes
    cdsls_path = "/" + cdsls_element
    cdsl_path = cdsls_path + "/" + cdsl_element
    defaults_path = cdsls_path + "/" + defaults_element
    noderef_path_part = "nodes/noderef/@ref"
    
    
    def __init__(self, configfile=CdslRepository.DEFAULT_INVENTORY, dtd=None, validate=True, *options):
        """
        Constructs a new comoonicsCdslRepository from given configfile. Creates 
        a list of cdsls from configfile to provide an easy access to them.
        @param configfile: path to configfile, should be created if it does not already exist
        @type configfile: L{string}
        @param dtd: path to dtd used with configfile (Default: None)
        @type dtd: L{string}
        @param validate: set to false to skip validation of configfile (Default: True)
        @type validate: L{Boolean}
        @param options: options could contain: cdsltree (cluster/cdsl), cdsltreeShared (cluster/shared), cdslLink (cdsl.local), maxnodeidnum (0), useNodeids (False), root, mountpoint, defaultDir, nodePrefix
        If you want to use options you MUST set the first fifth, if you do not want to use all other options, set the one you don't want to "None"
        @type options: L{list}
        """
        if len(options) > 4 and options[5] != None:
            self.root = options[5]
            self.configfile = os.path.join(self.root,re.sub('^/','', os.path.abspath(configfile)))
        else:
            self.root = "/"
            self.configfile = os.path.abspath(configfile)
        
        #if noexecute mode is set, store inventoryfile at /tmp
        if ComSystem.execMethod((lambda n: n),True) != True and not os.path.exists(configfile):
            self.configfile = os.path.join("/tmp",os.path.basename(configfile))
                   
        self.cdsls = []
        self.validate = validate
        from ComCdsl import Cdsl
        #maximum 9 parameters to set
        if not os.path.exists(self.configfile) and len(options) <= 9:
            if len(options) != 0 and len(options) < 5:
                raise AttributeError("Need at least none or 5-9 parameters to create inventoryfile")
            else:
                Lockfile = inventoryfileProcessing(self.configfile,dtd)
                doc = Lockfile.openLock(self.validate)
                
                topelement=doc.documentElement
                defaults=doc.createElement(self.defaults_element)
                #if len(options) == 0:
                if True:
                    defaults.setAttribute(self.defaults_cdsltree_attribute,self.cdsltree_default)
                    defaults.setAttribute(self.defaults_cdsltreeShared_attribute,self.cdsltreeShared_default)
                    defaults.setAttribute(self.defaults_cdslLink_attribute,self.cdslLink_default)
                    defaults.setAttribute(self.defaults_maxnodeidnum_attribute,self.maxnodeidnum_default)
                    defaults.setAttribute(self.defaults_useNodeids_attribute,self.useNodeids_default)
                #if len(options) >= 5:
                    if options[0] != None: defaults.setAttribute(self.defaults_cdsltree_attribute,options[0])
                    if options[1] != None: defaults.setAttribute(self.defaults_cdsltreeShared_attribute,options[1])
                    if options[2] != None: defaults.setAttribute(self.defaults_cdslLink_attribute,options[2])
                    if options[3] != None: defaults.setAttribute(self.defaults_maxnodeidnum_attribute,options[3])
                    if options[4] != None: defaults.setAttribute(self.defaults_useNodeids_attribute,options[4])
                #if len(options) >= 6 and not (options[5] == "" or options[5] == None):
                #    defaults.setAttribute(self.defaults_root_attribute,options[5])
                if len(options) >= 7 and not (options[6] == "" or options[6] == None):
                    defaults.setAttribute(self.defaults_mountpoint_attribute,options[6])
                if len(options) >= 8 and not (options[7] == "" or options[7] == None):
                    defaults.setAttribute(self.defaults_defaultDir_attribute,options[7])
                if len(options) == 9 and not (options[8] == "" or options[8] == None):
                    defaults.setAttribute(self.defaults_nodePrefix_attribute,options[8])
                topelement.appendChild(defaults)
            
                #write changes of doc to file, unlock and close it
                Lockfile.prettyprintUnlockClose(doc)
        elif not os.path.exists(self.configfile):
            raise AttributeError("Need at least existing configfile or file to create and none or 5-9 parameters to create inventoryfile")
        
        super(ComoonicsCdslRepository,self).__init__(self.configfile,dtd,self.validate)
        
        _cdsls = xpath.Evaluate(self.cdsl_path, self.getElement())        
        for i in range(len(_cdsls)):
            src = xpath.Evaluate("@%s" %(self.cdsl_src_attribute),_cdsls[i])[0].value
            type = xpath.Evaluate("@%s" %(self.cdsl_type_attribute),_cdsls[i])[0].value
            timestamp = xpath.Evaluate("@%s" %(self.cdsl_time_attribute),_cdsls[i])[0].value
            
            #get nodes from cdsl-inventoryfile
            nodes = []
            _tmp = xpath.Evaluate(self.noderef_path_part,_cdsls[i])
            useNodeids = self.getDefaultUseNodeids()
            nodePrefix = self.getDefaultNodePrefix()
            for i in range(len(_tmp)):
                if useNodeids == "True" and nodePrefix == "False":
                    nodes.append((_tmp[i].value).replace("id_",""))
                else:
                    nodes.append(_tmp[i].value)
            
            self.cdsls.append(Cdsl(src, type, self, nodes=nodes,timestamp=timestamp))
            
    def getCdsl(self,src):
        """
        Uses given source to return matching cdsl
        @param src: Path of searched cdsl
        @type src: string
        @return: cdsl-object belonging to given path
        @rtype: L{ComoonicsCdsl}
        """
        src = os.path.normpath(src)
        for i in range(len(self.cdsls)):
            if (self.cdsls[i].src == src):
                return self.cdsls[i]
            else:
                # check next cdsl-entry
                continue
            
    def exists(self,cdsl):
        """
        Looks if a given cdsl already exists in inventoryfile
        @param cdsl: Cdsl to test existenz later 
        @type cdsl: L{ComoonicsCdsl}
        @rtype: Boolean
        """
        for i in range(len(self.cdsls)):
            if (self.cdsls[i].src == cdsl.src) and (self.cdsls[i].type == cdsl.type) and (self.cdsls[i].nodes == cdsl.nodes):
		return True
            else:
                # check next cdsl-entry
                continue
	return False
    
    def commit(self,cdsl):
        """
        Adds or modifies cdsl entry in inventoryfile (depending on existing entry with the same src attribute like the given cdsl)
        @param cdsl: cdsl to commit
        @type cdsl: L{ComoonicsCdsl}
        """
        if self.exists(cdsl):
            """modify cdsl-entry if cdsl already exists and there are changes to commit"""
            log.debug("cdsl exists")
            #Open and lock XML-file and return DOM
            Lockfile = inventoryfileProcessing(self.configfile)
            doc = Lockfile.openLock(self.validate)
    
            #locate existing node entry
            oldnode = xpath.Evaluate("%s[@%s='%s']" %(self.cdsl_path,self.cdsl_src_attribute,cdsl.src),doc)[0]

            #modify existing cdsl-entry
            _tmp = xpath.Evaluate(self.cdsls_path, doc)
            _node = doc.importNode(cdsl.getElement(),True)
            _tmp[0].replaceChild(_node,oldnode)
        
            #write changes of doc to file, unlock and close it
            Lockfile.prettyprintUnlockClose(doc)
            
            #modify cdsls of cdslRepository instance
            self.cdsls.remove(self.getCdsl(cdsl.getAttribute(self.cdsl_src_attribute)))
            self.cdsls.append(cdsl)
            
        else:
            """create new cdsl-entry in inventory-file"""
            log.debug("cdsl does not exists")
            #Open and lock XML-file and return DOM
            Lockfile = inventoryfileProcessing(self.configfile)
            doc = Lockfile.openLock(self.validate)
            log.debug("file sucessfully opened and locked")
            
            #locate defaults element
            default = xpath.Evaluate(self.defaults_path,doc)[0]
    
            #modify existing cdsl-entry
            _tmp = xpath.Evaluate(self.cdsls_path, doc)
            _node = doc.importNode(cdsl.getElement(),True)            
            _tmp[0].insertBefore(_node,default)
        
            #write changes of doc to file, unlock and close it
            Lockfile.prettyprintUnlockClose(doc)
            
            #add new cdsl to instance of cdslRepository
            self.cdsls.append(cdsl)
        
        #adds nodes to defaults part
        for node in cdsl.nodes:
            self.addDefaultNode(node)
    
    def delete(self,cdsl):
        """
        Deletes cdsl entry in inventoryfile if existing
        @param cdsl: cdsl to delete
        @type cdsl: L{ComoonicsCdsl}
        """
        if self.exists(cdsl):
            """delete cdsl-entry if existing"""
            #Open and lock XML-file and return DOM
            Lockfile = inventoryfileProcessing(self.configfile)
            doc = Lockfile.openLock(self.validate)
    
            #locate node entry (already checking existing of cdsl, check of src is enough, because there cannot be more than one element with the same src)
            oldnode = xpath.Evaluate("%s[@%s='%s']" %(self.cdsl_path,self.cdsl_src_attribute,cdsl.src),doc)[0]

            #delete existing cdsl-entry
            _tmp = xpath.Evaluate(self.cdsls_path, doc)
            _tmp[0].removeChild(oldnode)
        
            #write changes of doc to file, unlock and close it
            Lockfile.prettyprintUnlockClose(doc)
            
            #delete cdsl from cdslrepository object
            for i in range(len(self.cdsls) - 1):
                if (self.cdsls[i].src == cdsl.src) and (self.cdsls[i].type == cdsl.type) and (self.cdsls[i].nodes == cdsl.nodes):
                    del self.cdsls[i]
                else:
                    # check next cdsl-entry
                    continue
        
        else:
            """raise exeption if cdsl to delete is not existing"""
            raise CdslRepositoryCdslNotFoundException("Cannot find given Cdsl to delete")
        
    def buildInfrastructure(self,clusterinfo):
        """
        Creates cdsl infrastructure, includes creating of needed directories and symbolic links 
        and keep in mind the exposure with a maybe given default directory (copy to every node, 
        link)
        @param clusterinfo: Clusterinfo with needed attributes
        @type clusterinfo: L{ComoonicsClusterInfo}
        """
        if clusterinfo:
            node_prefix = self.getDefaultNodePrefix()
            use_nodeids = self.getDefaultUseNodeids()
            maxnodeidnum = self.getDefaultMaxnodeidnum()
        
            if ((use_nodeids == "True") and (maxnodeidnum == "0")): #maxnodidnum is not set but use_nodeid is set
                nodes = clusterinfo.getNodeIdentifiers("id")
            elif (maxnodeidnum == "0"): #maxnodidnum is set but use_nodeid is not set
                nodes = clusterinfo.getNodeIdentifiers("name")           
            else: #use_nodeids and maxnodeidnum are set
                nodes = range(1,(int(maxnodeidnum)+1))
            
            #value of node_prefix matters only if use_nodeids is set
            #if node_prefix in inventoryfile is "", then getAttr gets "True" instead
            if ((node_prefix != "True") and (use_nodeids == "True")):
                for i in range(len(nodes)):
                    nodes[i] = str(node_prefix) + str(nodes[i])
            elif ((node_prefix != "True") and (node_prefix != "")) and not (use_nodeids == "True"):
                log.info("Prefix could only be used together with use_nodeids")
                
        root = self.root
        mountpoint = self.getDefaultMountpoint()
        default_dir = self.getDefaultDefaultDir()
        cdsltree_shared = self.getDefaultCdsltreeShared()
        cdsl_link = self.getDefaultCdslLink()
        cdsltree = self.getDefaultCdsltree()
        
        _rootMountpoint = os.path.normpath(os.path.join(root,re.sub('^/','', mountpoint)))
        if not os.path.exists(_rootMountpoint):
            raise CdslFileHandlingException("Mount point " + _rootMountpoint + " does not exist.")
            
        cdslDefaultdir = os.path.join(_rootMountpoint,re.sub('^/','', cdsltree),"default")
        if not os.path.exists(cdslDefaultdir):
            log.debug("Creating default_dir " + cdslDefaultdir)
            #os.makedirs(cdslDefaultdir)
            ComSystem.execMethod(os.makedirs,cdslDefaultdir)
            
        #if default_dir is set, copy it recursively to mountdir/root/cdsltree/default
        if default_dir:
            default_dir = os.path.normpath(default_dir)
            #Cannot use copytree here because of problems when copying sockets
            #log.debug("Copy files of " + default_dir + " to default directory")
            #shutil.copytree(os.path.abspath(default_dir), os.path.join(cdslDefaultdir,os.path.basename(default_dir)), True)
            ComSystem.execLocalStatusOutput("cp -a " + os.path.abspath(default_dir) + " " + os.path.join(cdslDefaultdir,os.path.basename(default_dir)))
        
        #Create basedirectory for every node
        for node in nodes:
            log.debug("Creating hostdirectory " + os.path.join(_rootMountpoint,re.sub('^/','', cdsltree),str(node),".."))
            #os.makedirs(os.path.join(_rootMountpoint,re.sub('^/','', cdsltree),str(node)))
            ComSystem.execMethod(os.makedirs,os.path.join(_rootMountpoint,re.sub('^/','', cdsltree),str(node)))
            if default_dir:
                #Cannot use copytree here because of problems when copying sockets
                #log.debug("Copy content of default_dir to node " + str(os.path.join(cdslDefaultdir,os.path.basename(default_dir))) + " => " + os.path.join(_rootMountpoint,re.sub('^/','', cdsltree),str(node),os.path.basename(default_dir)))
                #shutil.copytree(os.path.join(cdslDefaultdir,os.path.basename(default_dir)),os.path.join(_rootMountpoint,re.sub('^/','', cdsltree),str(node),os.path.basename(default_dir)),True)
                ComSystem.execLocalStatusOutput("cp -a " + os.path.join(cdslDefaultdir,os.path.basename(default_dir)) + " " + os.path.basename(default_dir)),os.path.join(_rootMountpoint,re.sub('^/','', cdsltree),str(node),os.path.basename(default_dir))
        
        #set relpath
        relpath = cdsl_link
                    
        # Create directories root_variable/relpath_variable if not already existing
        if not os.path.exists(os.path.join(_rootMountpoint,re.sub('^/','', relpath))):
            log.debug("Creating local directory " + os.path.join(_rootMountpoint,re.sub('^/','', relpath)))
            #os.makedirs(os.path.join(_rootMountpoint,re.sub('^/','', relpath)))
            ComSystem.execMethod(os.makedirs,os.path.join(_rootMountpoint,re.sub('^/','', relpath)))

    def getCdsls(self):
        """
        @rtype: ComoonicsCdsl
        """
        return self.cdsls
    
    def getDefaultCdsltree(self):
        """
        @rtype: string
        """
        return xpath.Evaluate("%s/@%s" %(self.defaults_path,self.defaults_cdsltree_attribute),self.getElement())[0].value

    def getDefaultCdsltreeShared(self):
        """
        @rtype: string
        """
        return xpath.Evaluate("%s/@%s" %(self.defaults_path,self.defaults_cdsltreeShared_attribute),self.getElement())[0].value

    def getDefaultCdslLink(self):
        """
        @rtype: string
        """
        return xpath.Evaluate("%s/@%s" %(self.defaults_path,self.defaults_cdslLink_attribute),self.getElement())[0].value

    def getDefaultMountpoint(self):
        """
        @rtype: string
        """
        _tmp = xpath.Evaluate("%s/@%s" %(self.defaults_path,self.defaults_mountpoint_attribute),self.getElement())
        try:
            return _tmp[0].value
        except (NameError, IndexError):
            return ""

    def getDefaultDefaultDir(self):
        """
        @rtype: string
        """
        _tmp = xpath.Evaluate("%s/@%s" %(self.defaults_path,self.defaults_defaultDir_attribute),self.getElement())
        try:
            return _tmp[0].value
        except (NameError, IndexError):
            return ""
    
    def getDefaultMaxnodeidnum(self):
        """
        @rtype: string
        """
        return xpath.Evaluate("%s/@%s" %(self.defaults_path,self.defaults_maxnodeidnum_attribute),self.getElement())[0].value
 
    def getDefaultNodePrefix(self):
        """
        @rtype: string
        """
        _tmp = xpath.Evaluate("%s/@%s" %(self.defaults_path,self.defaults_nodePrefix_attribute),self.getElement())
        try:
            return _tmp[0].value
        except (NameError, IndexError):
            return ""
    
    def getDefaultUseNodeids(self):
        """
        @rtype: string
        """
        return xpath.Evaluate("%s/@%s" %(self.defaults_path,self.defaults_useNodeids_attribute),self.getElement())[0].value
    
    def addNode(self,node,cdslfilter=None,addtofilesystem=False):
        """
        Adds node to all defined cdsls in inventoryfile (does not consider directories of cdsl in filesystem) 
        @param node: ID of node which should be added to cdsls, needed type of ID (nodeID, name or prefix & ID) 
        depends on values of used inventoryfile
        @type node: string
        @param addtofilesystem: If true, add new node to filesystem, uses copy of default-directory for cdsl-directorys. (Default: False)
        @type addtofilesystem: Boolean
        """
        #prepare filesystem for new node
        if addtofilesystem == True:
            root = self.root
            mountpoint = self.getDefaultMountpoint()
            default_dir = self.getDefaultDefaultDir()
            cdsltree = self.getDefaultCdsltree()
        
            _rootMountpoint = os.path.normpath(os.path.join(root,re.sub('^/','', mountpoint)))
            if not os.path.exists(_rootMountpoint):
                raise CdslFileHandlingException("Mount point " + _rootMountpoint + " does not exist.")
            
            cdslDefaultdir = os.path.join(_rootMountpoint,re.sub('^/','', cdsltree),"default")
            nodedir = os.path.join(_rootMountpoint,re.sub('^/','', cdsltree),node)
            if not os.path.exists(cdslDefaultdir):
                raise CdslFileHandlingException("Needed default directory " + cdslDefaultdir + " does not exist")
            
            #create needed directories if they are not existing
            if not os.path.exists(os.path.dirname(nodedir)):
                ComSystem.execMethod(os.makedirs,os.path.dirname(nodedir))
            #copy content of defaultnode-directory to newnode-directory
            ComSystem.execLocalStatusOutput("cp -a " + cdslDefaultdir + " " + nodedir)
        
        #Open and lock XML-file and return DOM
        Lockfile = inventoryfileProcessing(self.configfile)
        doc = Lockfile.openLock(self.validate)
        
        #find noderef and remove element
        #_nodes = xpath.Evaluate("/cdsls/cdsl/nodes[noderef/@ref != '%s']" %(node),doc)
        _nodes = xpath.Evaluate("%s/%s[%s/@%s != '%s']" %(self.cdsl_path,self.nodes_element,self.noderef_element,self.noderef_ref_attribute,self.noderef_path_part),doc)
        for _node in _nodes:
            _newref = doc.createElement(self.noderef_element)
            _newref.setAttribute(self.noderef_ref_attribute,node)
            _tmp = _node.appendChild(_newref)
            
        Lockfile.prettyprintUnlockClose(doc)
            
        #adds node to defaults part if not already existing there
        self.addDefaultNode(node)
    
    def removeNode(self,node,cdslfilter=None):
        """
        Remove node to all defined cdsls in inventoryfile (does not consider directories of cdsl in filesystem)
        @param node: ID of node which should be added to cdsls, needed type of ID (nodeID, name or prefix & ID) 
        depends on values of used inventoryfile
        @type node: string
        """
        #Open and lock XML-file and return DOM
        Lockfile = inventoryfileProcessing(self.configfile)
        doc = Lockfile.openLock(self.validate)
        
        #find noderef and remove element
        #_noderef = xpath.Evaluate("/cdsls/cdsl/nodes/noderef[@ref='%s']" %(node),doc)
        _nodes = xpath.Evaluate("%s/%s/%s[@%s = '%s']" %(self.cdsl_path,self.nodes_element,self.noderef_element,self.noderef_ref_attribute,self.noderef_path_part),doc)
        
        for _node in _noderef:
            _tmp = _node.parentNode.removeChild(_node)
            
        Lockfile.prettyprintUnlockClose(doc)
    
    def addDefaultNode(self,node,validate=False):
        """
        Adds DefaultNode to defaults part of inventoryfile.
        @param node: ID of node which should be added to defaults section, needed type of ID (nodeID, name or 
        prefix & ID) depends on values of used inventoryfile
        @type node: string
        @param validate: Use validation of inventoryfile if set to True, default False, because often this method 
        is used to "repair" a inventoryfile which would not pass a validation.
        """
        log.debug("Add node " + str(node) + " to defaultnodes")
        _isDigit=re.match('^[0-9]*$',str(node))
        if _isDigit != None:
            node = "id_" + str(node)
        
        #Open and lock XML-file and return DOM
        Lockfile = inventoryfileProcessing(self.configfile)
        doc = Lockfile.openLock(validate)
        
        #if not xpath.Evaluate("/cdsls/defaults/nodesdefault/nodedefault[@id='%s']" %(node),doc):
        if not xpath.Evaluate("%s/%s/%s[@%s='%s']" %(self.defaults_path,self.nodesdefault_element,self.nodedefault_element,self.nodedefault_id_attribute,node),doc):
            nodesdefault = doc.getElementsByTagName(self.nodesdefault_element)
            if not nodesdefault:
                default = doc.getElementsByTagName(self.defaults_element)[0]
                nodesdefault = doc.createElement(self.nodesdefault_element)
                default.appendChild(nodesdefault)
            else:
                nodesdefault = nodesdefault[0]
                
            nodedefault = doc.createElement(self.nodedefault_element)
            nodedefault.setAttribute(self.nodedefault_id_attribute,node)
            nodesdefault.appendChild(nodedefault)
            
        Lockfile.prettyprintUnlockClose(doc)

        
    def update(self,src,clusterInfo,chroot="/"):
        """
        Updates inventoryfile for given source. Add entry for associated cdsl to inventoryfile 
        if src is a cdsl on filesystem, but not already listed in inventoryfile. Deletes entry 
        from inventoryfile if cdsl exists in inventoryfile but is not present on filesystem.
        If cdsl is weather present in inventoryfile nor in filesystem change nothing.
        @param src: Sourcepath to check (incl. Root/Mountpoint)
        @type src: string
        @param clusterInfo: Clusterinfo object belonging to cdsl infrastructure
        @type clusterInfo: L{ComoonicsClusterInfo}
        """
        from ComCdsl import Cdsl
        
        _rootMountpoint = os.path.normpath(os.path.join(chroot,re.sub('^/','', self.getDefaultMountpoint())))
        _rootMountpointCdsllink = os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','',self.getDefaultCdslLink())))
        _rootMountpointCdslShared =  os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','',self.getDefaultCdsltreeShared())))
        
        # needed to become correct realpathes even with relativ symbolic links
        if _rootMountpoint == "":
            os.chdir("/")
        else:
            os.chdir(_rootMountpoint)       
            
        _srcLink = os.path.realpath(os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','',src))))
        _srcShared = _srcLink.replace(_rootMountpointCdslShared,'',1)
        _srcHostdependent = _srcLink.replace(_rootMountpointCdsllink,'',1)
        _src = src.replace(self.getDefaultCdslLink(),'',1)
        _cdsl = self.getCdsl(_src)
        
        #check if cdsl exists in cdslrepository
        if not type(_cdsl).__name__ == "NoneType":
            #check if cdsl exists also in filesystem
            if not _cdsl.exists(root=chroot):
                self.delete(_cdsl)
                log.debug("Deleted entry of not existing cdsl with source " + _src + " from inventoryfile")
            else:
               log.info("CDSL " + _src + " does already exist in inventoryfile and filesystem")
     
        else:
            #create hostdependent and shared cdsl-object and test if one of these is existing
            _cdslHostdependent = Cdsl(_src, "hostdependent", self, clusterInfo, root=chroot)
            _cdslShared = Cdsl(_src, "shared", self, clusterInfo, root=chroot)
                       
            if _cdslShared.exists():
                self.commit(_cdslShared)
                log.debug("Added shared CDSl with source " + _srcShared + " to inventoryfile.")
            elif _cdslHostdependent.exists():
                self.commit(_cdslHostdependent)
                log.debug("Added hostdependent CDSL with source " + _srcHostdependent + " to inventoryfile.")
            else:
                log.info("CDSL with source " + src + " does neither exist in inventoryfile nor in filesystem, no need to update inventoryfile")
   
def main():
    """
    Method to test module with nested cdsls. Does not modify inventoryfile directly, only create needed 
    infrastructure.
    """
    #set behaviour of comsystem, could be ask, simulate or continue
    ComSystem.__EXEC_REALLY_DO="continue"
    
    # create Reader object
    reader = Sax2.Reader(validate=True)

    #parse the document and create clusterrepository object
    file = os.fdopen(os.open("test/cluster.conf",os.O_RDONLY))
    try:
        doc = reader.fromStream(file)
    except xml.sax._exceptions.SAXParseException, arg:
        log.critical("Problem while reading XML: " + str(arg))
        raise
    file.close()
    element = xpath.Evaluate('/cluster', doc)[0]
    file.close()

    #create cluster objects
    clusterRepository = ClusterRepository(element,doc)
    clusterinfo = ClusterInfo(clusterRepository)

    #__init__(self, configfile="/var/lib/cdsl/cdsl_inventory.xml", dtd=None, validate=True, *options):
    cdslrepository = CdslRepository("test/cdsl5.xml","test/cdsl.dtd",False,"cluster/cdsl","cluster/shared","/cdsl.local","0","False",None,"/tmp")
    
    #print cdslrepository (xml) and build infrastructure
    cdslrepository.buildInfrastructure(clusterinfo)

if __name__ == '__main__':
    ComLog.setLevel(logging.INFO)
    main()
