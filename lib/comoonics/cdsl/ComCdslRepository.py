"""Comoonics cdslrepository object module


Represents cdsl-inventoryfile as an L{DataObject} and holds list 
of cdsl objects. The cdsl-inventoryfile contains information about 
the created cdsls and default values which are needed for cdsl 
management (modifying, creating, deleting).

"""


__version__ = "$Revision: 1.12 $"

import fcntl # needed for filelocking
import re

import xml
from xml import xpath
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml.dom.ext.reader.Sax2 import implementation

from comoonics import ComLog
from comoonics.ComExceptions import ComException
from comoonics.ComDataObject import DataObject
from comoonics import ComSystem

from comoonics.cdsl import stripleadingsep

import comoonics.pythonosfix as os
import os.path

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

    def prettyprintUnlockClose(self,doc=None,simulate=False):
        """
        Writes given xml to file, unlock it via fcntl and close.
        @param doc: Content to write back to locked file (overwrites existing content!), if None only unlock and close
        @type doc: DOM-Object
        """
        
        if doc != None:
            if simulate:
                PrettyPrint(doc)
            else:
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
    """
    Represents cdsl-inventoryfile as L{DataObject}
    """
    DEFAULT_INVENTORY="/var/lib/cdsl/cdsl_inventory.xml"
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
        cls = ComoonicsCdslRepository
        return object.__new__(cls, *args, **kwds)
    
    def __init__(self, configfile=DEFAULT_INVENTORY, dtd=None, validate=True, *options, **keys):
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
        if not os.path.exists(configfile):
            raise IOError("Inventoryfile " + configfile + " not found.")
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
    
    def getCdsl(self,src):
        """
        Uses given source to return matching cdsl
        @param src: Path of searched cdsl
        @type src: string
        @return: cdsl-object belonging to given path
        @rtype: L{ComoonicsCdsl}
        """
        return None

    def getCdsls(self):
        """
        @rtype: ComoonicsCdsl
        """
        return None
    
    def delete(self,cdsl):
        """
        Deletes cdsl entry in inventoryfile if existing
        @param cdsl: cdsl to delete
        @type cdsl: L{ComoonicsCdsl}
        """
        pass

    def exists(self,cdsl):
        """
        Looks if a given cdsl already exists in inventoryfile
        @param cdsl: Cdsl to test existenz later 
        @type cdsl: L{ComoonicsCdsl}
        @rtype: Boolean
        """
        return False

    def commit(self,cdsl):
        """
        Adds or modifies cdsl entry in inventoryfile (depending on existing entry with the same src attribute like the given cdsl)
        @param cdsl: cdsl to commit
        @type cdsl: L{ComoonicsCdsl}
        """
        
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
    
    default_expand_string_attribute="expandstring"
    default_expand_string=".cdsl"
    
    #definde defaultvalues
    cdsltree_default = "cluster/cdsl"
    cdsltreeShared_default = "cluster/shared"
    cdslLink_default = "cdsl.local"
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

    EXPANSION_PARAMETER="cdsl_expansion"
    
    def __init__(self, configfile=CdslRepository.DEFAULT_INVENTORY, dtd=None, validate=True, *options, **keys):
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
        elif keys and keys.has_key("root"):
            self.root = keys["root"]
        else:
            self.root = "/"
        self.configfile = os.path.join(self.root,stripleadingsep(os.path.abspath(configfile)))
        
        #if noexecute mode is set, store inventoryfile at /tmp
        if ComSystem.execMethod((lambda n: n),True) != True and not os.path.exists(configfile):
            self.configfile = os.path.join("/tmp",os.path.basename(configfile))
                   
        self.cdsls = list()
        self.validate = validate
        from ComCdsl import Cdsl
        #maximum 9 parameters to set
        if not os.path.exists(self.configfile) and len(options) <= 9:
            if (len(options) != 0 and len(options) < 5) or not keys:
                raise AttributeError("Need at least none or 5-9 parameters to create inventoryfile")
            else:
                Lockfile = inventoryfileProcessing(self.configfile,dtd)
                doc = Lockfile.openLock(self.validate)
                
                topelement=doc.documentElement
                defaults=topelement.getElementsByTagName(self.defaults_element)
                if defaults and len(defaults)>0:
                    defaults=defaults[0]
                else:
                    defaults=doc.createElement(self.defaults_element)
                    topelement.appendChild(defaults)
                #if len(options) == 0:
                defaults.setAttribute(self.defaults_cdsltree_attribute,self.cdsltree_default)
                defaults.setAttribute(self.defaults_cdsltreeShared_attribute,self.cdsltreeShared_default)
                defaults.setAttribute(self.defaults_cdslLink_attribute,self.cdslLink_default)
                defaults.setAttribute(self.defaults_maxnodeidnum_attribute,self.maxnodeidnum_default)
                defaults.setAttribute(self.defaults_useNodeids_attribute,self.useNodeids_default)
                defaults.setAttribute(self.default_expand_string_attribute, self.default_expand_string)
                
                if keys.has_key("cdsltree"): 
                    defaults.setAttribute(self.defaults_cdsltree_attribute,stripleadingsep(keys["cdsltree"]))
                elif options and options[0] != None: 
                    defaults.setAttribute(self.defaults_cdsltree_attribute,stripleadingsep(options[0]))
                if keys.has_key("cdsltreeshared"): 
                    defaults.setAttribute(self.defaults_cdsltreeShared_attribute,stripleadingsep(keys["cdsltreeshared"]))
                elif options and options[1] != None: 
                    defaults.setAttribute(self.defaults_cdsltreeShared_attribute,stripleadingsep(options[1]))
                if keys.has_key("cdsllink"): 
                    defaults.setAttribute(self.defaults_cdslLink_attribute,stripleadingsep(keys["cdsllink"]))
                elif options and options[2] != None: 
                    defaults.setAttribute(self.defaults_cdslLink_attribute,stripleadingsep(options[2]))
                if keys.has_key("maxnodeidnum"): 
                    defaults.setAttribute(self.defaults_maxnodeidnum_attribute,keys["maxnodeidnum"])
                elif options and options[3] != None: 
                    defaults.setAttribute(self.defaults_maxnodeidnum_attribute,options[3])
                if keys.has_key("usenodeids"): 
                    defaults.setAttribute(self.defaults_useNodeids_attribute,keys["usenodeids"])
                elif options and options[4] != None: 
                    defaults.setAttribute(self.defaults_useNodeids_attribute,options[4])
                if keys.has_key("mountpoint"): 
                    defaults.setAttribute(self.defaults_mountpoint_attribute,stripleadingsep(keys["mountpoint"]))
                elif len(options) >= 7 and not (options[6] == "" or options[6] == None):
                    defaults.setAttribute(self.defaults_mountpoint_attribute,stripleadingsep(options[6]))
                if keys.has_key("defaultdir"): 
                    defaults.setAttribute(self.defaults_defaultDir_attribute,stripleadingsep(keys["defaultdir"]))
                elif len(options) >= 8 and not (options[7] == "" or options[7] == None):
                    defaults.setAttribute(self.defaults_defaultDir_attribute,stripleadingsep(options[7]))
                if keys.has_key("nodeprefix"): 
                    defaults.setAttribute(self.defaults_nodePrefix_attribute,keys["nodeprefix"])
                elif len(options) == 9 and not (options[8] == "" or options[8] == None):
                    defaults.setAttribute(self.defaults_nodePrefix_attribute,options[8])
                if keys.has_key(self.default_expand_string_attribute):
                    defaults.setAttribute(self.default_expand_string_attribute, keys[self.default_expand_string_attribute])
            
                #write changes of doc to file, unlock and close it
                Lockfile.prettyprintUnlockClose(doc)
        elif not os.path.exists(self.configfile):
            raise AttributeError("Need at least existing configfile or file to create and none or 5-9 parameters to create inventoryfile")
        
        super(ComoonicsCdslRepository,self).__init__(self.configfile,dtd,self.validate)
        
        _cdsls = self.getElement().getElementsByTagName(self.cdsl_element)
        if _cdsls and len(_cdsls) > 0:
            for _elcdsl in _cdsls:
                _src = _elcdsl.getAttribute(self.cdsl_src_attribute)
                _type = _elcdsl.getAttribute(self.cdsl_type_attribute)
                _timestamp = _elcdsl.getAttribute(self.cdsl_time_attribute)
            
                #get nodes from cdsl-inventoryfile
                nodes = []
                _tmp1 = _elcdsl.getElementsByTagName(self.nodes_element)
                if _tmp1 and len(_tmp1) > 0:
                    _tmp=_tmp1[0].getElementsByTagName(self.noderef_element)
                    useNodeids = self.getDefaultUseNodeids()
                    nodePrefix = self.getDefaultNodePrefix()
                    for _node in _tmp:
                        if useNodeids == "True" and nodePrefix == "False":
                            nodes.append(_node.replace("id_",""))
                        else:
                            nodes.append(_node)
            
                self.cdsls.append(Cdsl(_src, _type, self, nodes=nodes,timestamp=_timestamp))
    
    def realpath(self, src):
        """
        Returns the realpath of a src. What it does it joins root, mountpath and src and gets the realpath
        from it
        @param src: the path to resolve to a realpath
        @type src: string
        @return: the resolved path of this src 
        @rtype: string
        """
        if self.getDefaultMountpoint().startswith(os.sep):
            _path=os.path.join(self.root, self.getDefaultMountpoint()[1:], src)
        else:
            _path=os.path.join(self.root, self.getDefaultMountpoint(), src)
        return os.path.realpath(_path)
            
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
            # modify cdsl-entry if cdsl already exists and there are changes to commit"""
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
            # create new cdsl-entry in inventory-file"""
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
        return cdsl
    
    def delete(self,cdsl):
        """
        Deletes cdsl entry in inventoryfile if existing
        @param cdsl: cdsl to delete
        @type cdsl: L{ComoonicsCdsl}
        """
        _deleted=None
        if self.exists(cdsl):
            # delete cdsl-entry if existing"""
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
            for _cdsl in self.cdsls:
                if (_cdsl.src == cdsl.src) and (_cdsl.type == cdsl.type) and (_cdsl.nodes == cdsl.nodes):
                    _deleted=_cdsl
                    self.cdsls.remove(_cdsl)        
        else:
            # raise exeption if cdsl to delete is not existing"""
            raise CdslRepositoryCdslNotFoundException("Cannot find given Cdsl to delete")
        return _deleted
        
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
            raise IOError(2, "Mount point " + _rootMountpoint + " does not exist.")
            
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
        
        # Create the shared directory
        cdslSharedDir= os.path.join(_rootMountpoint,re.sub('^/','', cdsltree_shared))
        if not os.path.exists(cdslSharedDir):
            log.debug("Creating shareddir " + cdslSharedDir)
            ComSystem.execMethod(os.makedirs, cdslSharedDir)
        
        #set relpath
        relpath = cdsl_link
                    
        # Create directories root_variable/relpath_variable if not already existing
        if not os.path.exists(os.path.join(_rootMountpoint,re.sub('^/','', relpath))):
            log.debug("Creating local directory " + os.path.join(_rootMountpoint,re.sub('^/','', relpath)))
            #os.makedirs(os.path.join(_rootMountpoint,re.sub('^/','', relpath)))
            ComSystem.execMethod(os.makedirs,os.path.join(_rootMountpoint,re.sub('^/','', relpath)))

    def expandCdsl(self, _cdsl):
        """
        expand this cdsl if need be. This is the case when this cdsl is nested. The nested path needs to 
        be expanded with subdirs in order to allow a hostdependent cdsl of a shared path.
        Algorithm is roughly as follows:
          We walk through the path of this cdsl from root to leaf.
          If subpath is a hostdep cdsl add the expansion_string from cdslrepository to this directory.
        Examples:
          hostdep => hostdep (hostdepdepth=_ignoredepth is skipped)
          hostdep/shared => hostdep/shared (hostdepdepth=1 is skipped)
          hostdep/shared/hostdep => hostdep.cdsl/shared/hostdep
          hostdep/shared/hostdep/shared => hostdep.cdsl/shared/hostdep/shared
          hostdep/shared/hostdep/shared/hostdep => hostdep.cdsl/shared/hostdep/shared/hostdep
          ..
        @param _cdsl: the cdsl.
        @type _cdsl: comoonics.cdsl.ComCdsl.Cdsl|string
        @return: returns the expanded path of the cdsl without either cdsltreeShared, cdsllink, ..
        @rtype: string 
        """ 
        from comoonics.cdsl import guessType
        from comoonics.cdsl.ComCdsl import Cdsl
        if isinstance(_cdsl, basestring):
            _cdsl=Cdsl(_cdsl, self)
        _tmppath=""
        _exp_empty={self.EXPANSION_PARAMETER: ""}
        _expanded_cdsl=False
        _expansions=_exp_empty
        if _cdsl.src.find(os.sep) > 0: 
            _subpaths=_cdsl.src.split(os.sep)
            for _subpath in _subpaths[:-1]:
                _tmppath=os.path.join(_tmppath, _subpath)
                _tmpcdsl=self.getCdsl(_tmppath %_exp_empty)
                if not _tmpcdsl:
                    _nodes=None
                    if _cdsl.clusterinfo == None:
                        _nodes=_cdsl.nodes
                    _tmpcdsl=Cdsl(_tmppath %_exp_empty, guessType(_tmppath, self), self, _cdsl.clusterinfo, _nodes, _cdsl.timestamp)
                    if _tmpcdsl and _tmpcdsl.exists():
                        log.warning("The cdsl %s seems not to be in the repository. Please rebuild database.")
                    else:
                        _tmpcdsl=None
                if _tmpcdsl and not _expanded_cdsl:
                    _expanded_cdsl=_tmpcdsl
                    _tmppath="%s%%(%s)s" %(_tmppath, self.EXPANSION_PARAMETER)
                elif _tmpcdsl and _expanded_cdsl:
                    _expansions={self.EXPANSION_PARAMETER: self.getDefaultExpandString()}

            _tmppath=os.path.join(_tmppath, _subpaths[-1])
        else:
            _tmppath=_cdsl.src

        return _tmppath %_expansions          

    def getCdsls(self):
        """
        @rtype: ComoonicsCdsl
        """
        return self.cdsls
    
    def getDefaultCdsltree(self, realpath=False):
        """
        @rtype: string
        """
        if not realpath:
            return xpath.Evaluate("%s/@%s" %(self.defaults_path,self.defaults_cdsltree_attribute),self.getElement())[0].value
        else:
            return self.realpath(self.getDefaultCdsltree(False))

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
    
    def getDefaultExpandString(self):
        """
        @rtype: string
        """
        try:
            return xpath.Evaluate("%s/@%s" %(self.defaults_path,self.default_expand_string_attribute),self.getElement())[0].value
        except IndexError:
            return self.default_expand_string
    
    def addNode(self,node,cdslfilter=None,addtofilesystem=False,simulate=False):
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
            cdsltree = self.getDefaultCdsltree()
        
            _rootMountpoint = os.path.normpath(os.path.join(root,re.sub('^/','', mountpoint)))
            if not os.path.exists(_rootMountpoint):
                raise IOError(2, "Mount point " + _rootMountpoint + " does not exist.")
            
            cdslDefaultdir = os.path.join(_rootMountpoint,re.sub('^/','', cdsltree),"default")
            nodedir = os.path.join(_rootMountpoint,re.sub('^/','', cdsltree),node)
            if not os.path.exists(cdslDefaultdir):
                raise IOError(2, "Needed default directory " + cdslDefaultdir + " does not exist")
            
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
            
        Lockfile.prettyprintUnlockClose(doc,simulate=simulate)
        
        #adds node to defaults part if not already existing there
        self.addDefaultNode(node,simulate=simulate,mydoc=doc)
    
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
        
        for _node in _nodes:
            _tmp = _node.parentNode.removeChild(_node)
            
        Lockfile.prettyprintUnlockClose(doc)
    
    def addDefaultNode(self,node,validate=False,simulate=False,mydoc=None):
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
        
        if simulate and mydoc:
            doc = mydoc
        
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
            
        Lockfile.prettyprintUnlockClose(doc,simulate=simulate)

        
    def update(self,src,clusterInfo,_onlyvalidate=False,chroot=""):
        """
        Updates inventoryfile for given source. Add entry for associated cdsl to inventoryfile 
        if src is a cdsl on filesystem, but not already listed in inventoryfile. Deletes entry 
        from inventoryfile if cdsl exists in inventoryfile but is not present on filesystem.
        If cdsl is neither present in inventoryfile nor in filesystem change nothing.
        @param src: Sourcepath to check (incl. Root/Mountpoint)
        @type src: string
        @param clusterInfo: Clusterinfo object belonging to cdsl infrastructure
        @type clusterInfo: L{ComoonicsClusterInfo}
        @param _onlyvalidate: returns the lists but does not change the database
        @type _onlyvalidate: Boolean (default False)  
        @return: if the cdsl was added the cdsl as first and if it was removed as second return value. 
                 None either. 
        @rtype: Cdsl, Cdsl
        """
        from comoonics.cdsl.ComCdsl import Cdsl
        
        _deleted=None
        _added=None
        
        if chroot and chroot == "":
            chroot=self.root
        if chroot and chroot == "":
            chroot="/"
        
        _src = src.replace(self.getDefaultCdslLink(),'',1)
        _cdsl = self.getCdsl(_src)
        
        #check if cdsl exists in cdslrepository
        if _cdsl:
            #check if cdsl exists also in filesystem
            if not _cdsl.exists():
                log.debug("Deleted entry of not existing cdsl with source " + _src + " from inventoryfile")
                if not _onlyvalidate:
                    self.delete(_cdsl)
                _deleted=_cdsl
            else:
                log.debug("CDSL " + _src + " does already exist in inventoryfile and filesystem")
     
        else:
            #create hostdependent and shared cdsl-object and test if one of these is existing
            _cdslHostdependent = Cdsl(_src, "hostdependent", self, clusterInfo)
            _cdslShared = Cdsl(_src, "shared", self, clusterInfo)
                       
            if _cdslShared.exists():
                log.debug("Added shared CDSl with source " + _src + " to inventoryfile.")
                if not _onlyvalidate:
                    self.commit(_cdslShared)
                _added=_cdslShared
            elif _cdslHostdependent.exists():
                log.debug("Added hostdependent CDSL with source " + _src + " to inventoryfile.")
                if not _onlyvalidate:
                    self.commit(_cdslHostdependent)
                _added=_cdslHostdependent
            else:
                log.debug("CDSL with source " + src + " does neither exist in inventoryfile nor in filesystem, no need to update inventoryfile")
        return _added, _deleted
        
    def setRoot(self,root):
        """
        Set chroot of cdsl, needed e.g. when a cdsl is picked out from inventoryfile
        and you work in an environment which is prepared for chroot
        @param root: chroot-path to set
        @type root: string
        """
        self.root = root
