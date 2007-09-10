"""Comoonics cdsl object module


Module to create and modify cdsls on filesystem and commit changes to L{CdslRepository}. Represents 
cdsl as an L{DataObject}.
"""


__version__ = "$Revision: 1.5 $"

import re
import sys
import shutil
import mimetypes
import operator

from xml import xpath
from xml.dom.ext.reader import Sax2
from xml.dom.ext.reader.Sax2 import implementation

from ComCdslRepository import *

from comoonics import ComSystem
from comoonics.ComLog import *
from comoonics.ComExceptions import *
from comoonics.ComDataObject import DataObject

from comoonics.cluster.ComClusterInfo import *
from comoonics.cluster.ComClusterRepository import *

import comoonics.pythonosfix as os

ComSystem.__EXEC_REALLY_DO = ""
log = ComLog.getLogger("comoonics.cdsl.ComCdsl")

class CdslInitException(ComException):pass
class CdslUnsupportedTypeException(ComException):pass
class CdslFileHandlingException(ComException):pass
class CdslPrefixWithoutNodeidsException(ComException):pass
class CdslDoesNotExistException(ComException):pass

class Cdsl(DataObject):
    """
    Represents a cdsl as an L{DataObject} and provides methods to commit changes or test cdsls.
    """
    def __new__(cls, *args, **kwds):
        """
        Decide which type of Cdsl is needed to create by verifying the type of 
        given Repository. Can deal with L{ComoonicsCdslRepository}. If an not known type is given, a instance of the 
        default class L{cdsl} will be created.
        @return: a new cdsl object 
        @rtype: depending on type of repository
        """
        if type(args[2]).__name__ == "ComoonicsCdslRepository":
            cls = ComoonicsCdsl
        return object.__new__(cls, *args, **kwds)
    
    def __init__(self, src, type, cdslRepository, clusterinfo=None, nodes=None, timestamp=None):
        """
        Constructs a new cdsl-xml-object from given L{CdslRepository} and nodes. The constructor 
        gets the needed nodes either from list (nodes) or from a given L{ClusterInfo} but never 
        from both! You can optional assign the creation timestamp manually.
        @param src: source of cdsl to create
        @type src: string
        @param type: type of cdsl to create, could be hostdependent or shared
        @type type: string
        @param cdslRepository: cdslRepository to use
        @type cdslRepository: L{CdslRepository}
        @param clusterinfo: clusterinfo with information about used nodes (Default: None)
        @type clusterinfo: L{ClusterInfo}
        @param nodes: Array of nodes to use for cdsl (Default: None)
        @type nodes: Array of strings
        @param timestamp: Timestamp to set to cdsl (Default: None), if not set create timestamp from systemtime
        @type timestamp: string
        """
        self.src = src
        self.type = type
        self.cdslRepository = cdslRepository
        
        if timestamp != None:
            self.timestamp = timestamp
        else:
            self.timestamp = time.time()
        
        #get nodes from clusterinfo if nodelist is not setgiven
        if (nodes == None) and (clusterinfo != None):
            self.node_prefix = cdslRepository.getDefaultNodePrefix()
            self.use_nodeids = cdslRepository.getDefaultUseNodeids()
            self.maxnodeidnum = cdslRepository.getDefaultMaxnodeidnum()
        
            if ((self.use_nodeids == "True") and (self.maxnodeidnum == "0")): #maxnodidnum is not set but use_nodeid is set
                self.nodes = clusterinfo.getNodeIdentifiers("id")
            elif (self.maxnodeidnum == "0"): #maxnodidnum is set but use_nodeid is not set
                self.nodes = clusterinfo.getNodeIdentifiers("name")
                
            else: #use_nodeids and maxnodeidnum are set
                self.nodes = range(1,(int(self.maxnodeidnum)+1))
            
            #value of node_prefix matters if use_nodeids is set
            if ((self.node_prefix) and (self.use_nodeids == "True")):
                for i in range(len(self.nodes)):
                    self.nodes[i] = str(self.node_prefix) + str(self.nodes[i])
            elif (self.node_prefix) and not (self.use_nodeids == "True"):
                raise CdslPrefixWithoutNodeidsException("Prefix could only be used together with use_nodeids")
                
        #set given nodelist
        elif (nodes != None) and (clusterinfo == None):
            self.nodes = nodes
            
        #no nodelist or clusterinfo is given OR both is given
        else:
            raise CdslInitException("Cannot use nodeslist and clusterinfo object together or none of these.")
        
        #create DOM-Element
        doc = implementation.createDocument(None,"cdsl",None)
        topelement=doc.documentElement
        topelement.setAttribute("src",self.src)
        topelement.setAttribute("type",self.type)
        topelement.setAttribute("timestamp",str(self.timestamp))
        
        nodes=doc.createElement("nodes")
        topelement.appendChild(nodes)
        
        for node in self.nodes:
            node1=doc.createElement("noderef")
            #If nodeids without prefix are used, use prefix id_ to get a valid xml-file
            _isDigit=re.match('^[0-9]*$',str(node))
            if _isDigit != None:
                node = "id_" + str(node)
            node1.setAttribute("ref",str(node))
            nodes.appendChild(node1)
        
        #self.XmlElement = doc
        #element = xpath.Evaluate('/cdsl', self.XmlElement)[0]
        element = xpath.Evaluate('/cdsl', doc)[0]
        
        #super(Cdsl,self).__init__(element,self.XmlElement)
        super(Cdsl,self).__init__(element,doc)

    def commit(self):
        """
        Commit new or changed cdsl to inventoryfile, Placeholder for 
        commiting method of specialized classes (there it should add 
        the cdsl to filesystem too)
        """
        self.cdslRepository.commit(self)
    
    def delete(self):
        """
        Delete cdsl from inventoryfile, Placeholder for deleting method 
        of specialized classes (there it should delete the cdsl to 
        filesystem too)
        """
        self.cdslRepository.delete(self)
    
    def exists(self):
        """
        Placeholder for specialized classes, should contain a method to 
        check the existence of a cdsl on filesystem.
        """
        pass
    
class ComoonicsCdsl(Cdsl):
    """
    Represents a comoonics cdsl as an xml-object and provides methods to 
    commit changes, delete or check existence of cdsl on filesystem.
    """
    
    default_node = "default"
    
    def __init__(self, src, type, cdslRepository, clusterinfo=None, nodes=None, timestamp=None, root="/"):
        """
        Constructs a new com.oonics cdsl from given L{ComoonicsCdslRepository} and nodes. 
        The constructor gets the needed nodes either from list (nodes) or from a given 
        L{ComoonicsClusterInfo} but never from both! You can optional assign the creation 
        timestamp manually.
        
        Additional the constructor is setting the default values from
        L{ComoonicsCdslRepository} to variables which can easily be accessed during cdsl 
        processing.
        
        @param src: source of cdsl to create
        @type src: string
        @param type: type of cdsl to create, could be hostdependent or shared
        @type type: string
        @param cdslRepository: cdslRepository to use
        @type cdslRepository: L{ComoonicsCdslRepository}
        @param clusterinfo: clusterinfo with information about used nodes (Default: None)
        @type clusterinfo: L{ComoonicsClusterInfo}
        @param nodes: Array of nodes to use for cdsl (Default: None)
        @type nodes: Array of strings
        @param timestamp: Timestamp to set to cdsl (Default: None), if not set create timestamp from systemtime
        @type timestamp: string
        """
        super(ComoonicsCdsl,self).__init__(src, type, cdslRepository, clusterinfo, nodes, timestamp)
        
        #set reldir to current path
        self.reldir = os.getcwd()
        
        #get needed pathes from cdslrepository and normalize them
        self.cdsltree = os.path.normpath(cdslRepository.getDefaultCdsltree())
        self.cdsltree_shared = os.path.normpath(cdslRepository.getDefaultCdsltreeShared())    
        self.default_dir = os.path.normpath(cdslRepository.getDefaultDefaultDir())
        self.cdsl_link = os.path.normpath(cdslRepository.getDefaultCdslLink())
        self.root = root
        self.mountpoint = cdslRepository.getDefaultMountpoint()
        
        self.cdslRepository = cdslRepository
        self.clusterinfo = clusterinfo

        #add default node to a special nodelist
        self.nodesWithDefaultdir = self.nodes[:]
        self.nodesWithDefaultdir.append(self.default_node)

    def _pathdepth(self,path):
        """
        Method to calculate the depth of a given path.
        @param path: Path
        @type path: string
        @return: Depth of given path
        @rtype: int
        """
        deepth = 0
        while path != "/":
            deepth = deepth + 1
            path = os.path.dirname(os.path.normpath(path))
        return deepth
        
    def _createEmptyFile(self,path,force=False):
        """
        Method to create an empty file at a given path.
        Overwrites Existing file or directory if force is set
        @param path: Path of file to create
        @type path: string
        @param force: Set if path should be overwritten if already existing
        @type force: Boolean
        """
        log.debug("Creating " + path)
        try:
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            if force == True and os.path.exists(path):
                log.debug("rm -rf " + path)
                shutil.rmtree(path)
            #if source does not exist, use a blank dummyfile instead
            if not os.path.isdir(path):
                _tmpFile = file(path,"w")
                _tmpFile.write("")
                _tmpFile.flush()
                _tmpFile.close()
        except:
            raise CdslFileHandlingException("Cannot create blank file " + path)
        
    def _removePath(self,path,force=False):
        """
        Removes given path if force is true by keep in mind the type of given path (directory or file)
        @param path: Path to file or directory to delete
        @type path: string
        @param force: Set if path should be deleted
        @type force: Boolean
        """
        if os.path.exists(path) and force == True:
            log.debug("Remove " + path)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

    def commit(self,force=False):
        """
        Commit new or changed cdsl to filesystem and inventoryfile
        @param force: skip Backup when set and overwrite existing files/directories/links
        @type force: Boolean
        """
        #important pathes to work with cdsls
        _rootMountpoint = os.path.normpath(os.path.join(self.root,re.sub('^/','', self.mountpoint)))
        _rootMountpointSrc = os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','', self.src)))
        _rootMountpointCdsltreesharedSrc = os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree_shared),re.sub('^/','', self.src)))
        
	    #####
        # Chancel creation of cdsl if it already exists
        # or a cdsl of another type with same src exists
        # or creation is insane because underlying structure 
        # is of same type as cdsl which should be created
        #####       
        if self.exists():
            log.debug("CDSL already exists, chancel commit")
            sys.exit()
        elif self.type=="shared":
            _tmpCdsl = Cdsl(self.src, "hostdependent", self.cdslRepository, self.clusterinfo, None)
            if (os.path.realpath(_rootMountpointSrc)).find(self.cdsltree_shared) != -1:
                log.debug("Given source is already part of a shared CDSL")
                sys.exit()
            elif _tmpCdsl.exists():
                log.debug("A hostdependent CDSL with given source already exists, chancel commit")
                sys.exit()
        elif self.type=="hostdependent":
            _tmpCdsl = Cdsl(self.src, "shared", self.cdslRepository, self.clusterinfo, None)
            if (os.path.realpath(_rootMountpointSrc)).find(self.cdsl_link) != -1:
                log.debug("Given source is already part of a hostdependent CDSL")
                sys.exit()
            elif _tmpCdsl.exists():
                log.debug("A shared CDSL with given source already exists, chancel commit")
                sys.exit()
           
        if self.type=="shared":
            #####
            # Check if cdsl structure is nested (e.g. /hostdependent/shared/hostdependent/shared)
            # and check for value of /root/mountpoint/cdsltree_shared/src
            ##### 
            _tmp = _rootMountpointSrc
            _nested = False
            
            while _tmp != "" and _tmp != "/":
                if os.path.islink(_tmp):
                    if os.path.realpath(_tmp).find(self.cdsl_link) != -1:
                        _nested = True
                        _tmp = os.path.realpath(_rootMountpointSrc).replace(os.path.join(os.path.realpath(_rootMountpoint),re.sub('^/','', self.cdsl_link)), "", 1)
                        _rootMountpointCdsltreesharedSrc = os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree_shared),re.sub('^/','', _tmp)))
                        break
                _tmp = os.path.dirname(_tmp)

            #####
            # If force is set: moves content of first node in array self.node[] to shared tree
            # If force is not set: copy content of first node
            # If src does not exist, create a file with this path
            #####
            _rootMountpointCdsltreeNodeSrc = os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree),str(self.nodes[0]),re.sub('^/','', _tmp)))
            
            # create unterlying directorystructure for /root/mountpoint/cdsltree_shared/src (if not existing)
            if not os.path.exists(os.path.dirname(_rootMountpointCdsltreesharedSrc)):
                    log.debug("Create Directory " + os.path.dirname(_rootMountpointCdsltreesharedSrc))
                    #os.makedirs(os.path.dirname(_rootMountpointCdsltreesharedSrc))
                    ComSystem.execMethod(os.makedirs,os.path.dirname(_rootMountpointCdsltreesharedSrc))
             
            if os.path.exists(_rootMountpointCdsltreeNodeSrc) and force == True:
                log.debug("Move Files to shared tree: " + _rootMountpointSrc + " => " + os.path.dirname(_rootMountpointCdsltreesharedSrc))
                #remove file if it is already existing (and force is set)
                ComSystem.execMethod(self._removePath,_rootMountpointCdsltreesharedSrc,force)
                ComSystem.execMethod(shutil.move,_rootMountpointSrc,_rootMountpointCdsltreesharedSrc)      
            elif os.path.exists(_rootMountpointCdsltreeNodeSrc) and force == False:
                log.debug("Copy Files to shared tree: " + _rootMountpointSrc + " => " + os.path.dirname(_rootMountpointCdsltreesharedSrc))
                if os.path.isdir(_rootMountpointSrc):
                    #Cannot use copytree here because of problems when copying sockets
                    #log.debug("copytree " + _rootMountpointSrc + ".orig => " + _rootMountpointCdsltreesharedSrc)
                    #shutil.copytree(_rootMountpointSrc + ".orig", _rootMountpointCdsltreesharedSrc,True)
                    ComSystem.execLocalStatusOutput("cp -a " + _rootMountpointSrc + " " + _rootMountpointCdsltreesharedSrc)
                elif os.path.isfile(_rootMountpointSrc):
                    log.debug("copyfile " + _rootMountpointSrc + _rootMountpointCdsltreesharedSrc)
                    ComSystem.execMethod(shutil.copy2,_rootMountpointSrc, _rootMountpointCdsltreesharedSrc)
                        
            else:
                #if force is set and file is already existing, remove it
                ComSystem.execMethod(self._removePath,_rootMountpointCdsltreesharedSrc,force)
                #if given src is not a existing file/directory, create empty file with given path
                ComSystem.execMethod(self._createEmptyFile,_rootMountpointCdsltreesharedSrc,force)
            
            #####
            # move (yet) hostdepedent directories to source.orig for every node if force is not set (create a backup)
            # remove (yet) hostdepedent directories of every node if force is set (skip backup)
            # if given source does not exist, skip both, because there is nothing to move or remove
            #####
            for node in self.nodesWithDefaultdir:
                _rootMountpointCdsltreeNodeSrc = os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree),str(node),re.sub('^/','', _tmp)))
                
                #if given source exists and force isn't set, move source to source.orig
                if os.path.exists(_rootMountpointCdsltreeNodeSrc) and force == False:
                    log.debug("Backing up " + _rootMountpointCdsltreeNodeSrc + " => " + _rootMountpointCdsltreeNodeSrc + ".orig ...")
                    ComSystem.execMethod(shutil.move,_rootMountpointCdsltreeNodeSrc , _rootMountpointCdsltreeNodeSrc + ".orig")
                    
                #if given source exists and force is set, remove source from hostdependent cdsltree
                elif os.path.exists(_rootMountpointCdsltreeNodeSrc) and force == True:
                    ComSystem.execMethod(self._removePath,_rootMountpointCdsltreeNodeSrc,force)
                 
                #if given src does not exist, create underlying directories        
                elif  not os.path.exists(os.path.dirname(_rootMountpointCdsltreeNodeSrc)):
                    ComSystem.execMethod(os.makedirs,os.path.dirname(_rootMountpointCdsltreeNodeSrc))
                          
            #####
            # Create needed symbolic links
            #####
            os.chdir(os.path.dirname(_rootMountpointSrc))
            
            _tmpDeepth = self._pathdepth(_rootMountpointCdsltreesharedSrc)
            _rootMountpointCdsltreeNodeSrc = os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree),str(node),re.sub('^/','', _tmp)))
            deepthNeeded = self._pathdepth(os.path.normpath(_rootMountpointSrc)) - self._pathdepth(os.path.normpath(_rootMountpoint))
            relativRoot = deepthNeeded * "../"
            
            _relRootMountpointCdsltreesharedSrc = os.path.normpath(_rootMountpointCdsltreesharedSrc.replace(_rootMountpoint,relativRoot,1))
            
            log.debug("Creating needed symbolic links...")
            for node in self.nodesWithDefaultdir:
                _rootMountpointCdsltreeNodeSrc = os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree),str(node),re.sub('^/','', _tmp)))
                if not _nested:
                    ComSystem.execLocalStatusOutput("ln -sf " + _relRootMountpointCdsltreesharedSrc + " " + _rootMountpointCdsltreeNodeSrc)
                else:
                    ComSystem.execLocalStatusOutput("ln -sf " + _relRootMountpointCdsltreesharedSrc + " " + os.path.dirname(_rootMountpointCdsltreeNodeSrc))
        
        elif self.type=="hostdependent":
            ######
            # Check if cdsl structure is nested (e.g. /hostdependent/shared/hostdependent)
            # by checking for shared cdsltree in realpath of source
            # If structure is nested, _nested and _tmpPartAfterNode are set
            ######
            _tmp = _rootMountpointSrc
            _tmp2 = os.path.realpath(_rootMountpointSrc).replace(os.path.normpath(os.path.join(os.path.realpath(_rootMountpoint),re.sub('^/','', self.cdsltree_shared))), "",1)
            _nested = False
            
            while _tmp != "" and _tmp != "/":
                if os.path.islink(_tmp):
                    if os.path.realpath(_tmp).find(self.cdsl_link) != -1:
                        _nested = True
                        _tmp1 = os.path.realpath(_tmp).replace(os.path.normpath(os.path.join(os.path.realpath(_rootMountpoint),re.sub('^/','', self.cdsl_link))),"",1)
                        _tmp = _tmpPartAfterNode = _tmp2.replace(_tmp1,_tmp1+".cdsl",1)
                        break
                _tmp = os.path.dirname(_tmp)

            #####
            # Copy source to hostdependent directory of every node
            # Use dummyfile is source does not exist
            #####
            log.debug("Creating/Copying the file to all hosts...")
            for node in self.nodesWithDefaultdir:
                if _nested == True:
                    _rootMountpointCdsltreeNodeSrc = os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree),str(node),re.sub('^/','', _tmpPartAfterNode)))
                else:
                    _rootMountpointCdsltreeNodeSrc = os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree),str(node),re.sub('^/','', self.src)))
                
                if os.path.exists(_rootMountpointSrc):
                    log.debug("Copying " + _rootMountpointSrc + " => " + _rootMountpointCdsltreeNodeSrc + "...")
                    #if force is set and target directory already exists, remove it
                    ComSystem.execMethod(self._removePath,_rootMountpointCdsltreeNodeSrc,force)
                    if not os.path.exists(os.path.dirname(_rootMountpointCdsltreeNodeSrc)):
                        ComSystem.execMethod(os.makedirs,os.path.dirname(_rootMountpointCdsltreeNodeSrc))
                    if os.path.isdir(_rootMountpointSrc):
                        #Cannot use copytree here because of problems when copying sockets
                        #log.debug("copytree " + _rootMountpointSrc + " => " + _rootMountpointCdsltreeNodeSrc)
                        #shutil.copytree(_rootMountpointSrc,_rootMountpointCdsltreeNodeSrc,True)
                        ComSystem.execLocalStatusOutput("cp -a " + _rootMountpointSrc + " " + _rootMountpointCdsltreeNodeSrc)
                        
                    elif os.path.isfile(_rootMountpointSrc):                  
                        #copy given source to cdsl-directories
                        ComSystem.execMethod(shutil.copy2,_rootMountpointSrc,_rootMountpointCdsltreeNodeSrc)
                else:
                    #if given src is not a existing file/directory, create empty file with given path
                    ComSystem.execMethod(self._createEmptyFile,_rootMountpointCdsltreeNodeSrc,force)
            
            #####
            # Backup source to source.orig
            # if force is not set and no dummyfile was created
            # remove source
            #####
            if os.path.exists(_rootMountpointSrc):
                if force == False:
                    log.debug("Moving " + _rootMountpointSrc + " => " + _rootMountpointSrc + ".orig...")
                    ComSystem.execMethod(shutil.move,_rootMountpointSrc,_rootMountpointSrc + ".orig")
                else:
                    ComSystem.execMethod(self._removePath,_rootMountpointSrc,force)
        
            #####
            # Update needed symbolic links
            #####
            log.debug("Creating needed symbolic links...")
            
            os.chdir(os.path.dirname(_rootMountpointSrc))
            
            os.path.normpath(_rootMountpoint)
            if _nested == True:
                _path1 = os.path.join(_rootMountpoint,re.sub('^/','', self.cdsl_link),re.sub('^/','', _tmpPartAfterNode))
            else:
                _path1 = os.path.join(_rootMountpoint,re.sub('^/','', self.cdsl_link),re.sub('^/','', self.src))
                
            deepthNeeded = self._pathdepth(os.path.normpath(os.path.realpath(_rootMountpointSrc))) - self._pathdepth(os.path.normpath(os.path.realpath(_rootMountpoint)))
            relativRoot = (deepthNeeded-1) * "../"
            _path1 = _path1.replace(_rootMountpoint,relativRoot,1)
            if deepthNeeded-1 == 0:
                _path1 = re.sub('^/','', _path1)
                
            ComSystem.execLocalStatusOutput("ln -s " + os.path.normpath(_path1) + " " + os.path.dirname(_rootMountpointSrc))
            
        #####
        # if type of cdsl is wheater shared nor hostdependent, a error has been accured
        #####
        else:
            raise CdslUnsupportedTypeException(self.type + " is not a supported cdsl type.")
        
        #####
        # Update inventoryfile
        # same procedure for changed and new hostdependent/shared cdsls
        #####
        log.debug("Updating cdsl-inventoryfile")
        ComSystem.execMethod(self.cdslRepository.commit,self)
    
    def delete(self,recursive=True,force=True,root=None):
        """
        Deletes cdsl from filesystem and inventoryfile
        @param force: If not set remove only symbolic links, if set remove content, too
        @type force: Boolean
        @param recursive: if set delete subcdsls (e.g. /host/shared/host when removing /host/shared)
        @type recursive: Boolean
        """
        if root!=None:
            self.setRoot(root)
            
        if not self.exists():
            raise CdslDoesNotExistException("Cdsl with source " + self.src + " does not exist, cannot delete.")
        
        #when using nodeids in cdslrepository, these have got a suffix "id_" to 
        #get valid xml. Remove that "id_" here, because its not used to build 
        #the directories.
        if self.cdslRepository.getDefaultUseNodeids() == "True":
            _tmpNodes = []
            for node in self.nodesWithDefaultdir:
                _tmpNodes.append(node.replace("id_","",1))               
        else:
            _tmpNodes = self.nodesWithDefaultdir
            
        #verify if cdsl contains other cdsl, if true delete these first
        #assume completeness of inventoryfile
        if recursive == True:
            subcdsls = []
            _tmp = self.getChilds()
            for cdsl in _tmp:
                subcdsls.append([self._pathdepth(cdsl.src),cdsl])
            #sort cdsls by pathdeepth (ascending) and delete cdsls whith deepest path first
            #sorted was first intruduced with python 2.4
            #subcdsls = sorted(subcdsls)[::-1]
            subcdsls.sort()
            subcdsls.reverse()
            for cdsl in subcdsls:
                cdsl[1].delete(False)
        
        _rootMountpoint = os.path.normpath(os.path.join(self.root,re.sub('^/','', self.mountpoint)))
        _rootMountpointSrc = os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','', self.src)))
        _nested = False
        
        #test if cdsl has got two or more parents
        if self.getParent() != None:
            if self.getParent().getParent() != None:
                _nested = True
        
        #delete cdsl from filesystem
        if self.type == "hostdependent":
            log.debug("Delete hostdependent CDSL " + _rootMountpointSrc)
            #must be a link, otherwise something wents wrong by cdsl-creation
            if os.path.islink(_rootMountpointSrc):
                if force == True:
                    for node in _tmpNodes:
                        _rootMountpointCdsltreeNodeSrc = os.path.realpath(_rootMountpointSrc).replace(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsl_link)),os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree),node),1)
                        #self._removePath(_rootMountpointCdsltreeNodeSrc,True)
                        ComSystem.execMethod(self._removePath,_rootMountpointCdsltreeNodeSrc,True)
                    _rootMountpointCdsltreeSharedSrc = os.path.realpath(_rootMountpointSrc).replace(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsl_link)),os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree_shared)),1)
                    #self._removePath(_rootMountpointCdsltreeSharedSrc,True)
                    ComSystem.execMethod(self._removePath,_rootMountpointCdsltreeSharedSrc,True)
                    
                    if _nested == True and len(self.getSiblings()) == 0:
                        #self._removePath(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree),node,re.sub('^/','', self.getParent().getParent().src+".cdsl")),True)
                        ComSystem.execMethod(self._removePath,os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree),node,re.sub('^/','', self.getParent().getParent().src+".cdsl")),True)
        
                log.debug("Remove symbolic link " + _rootMountpointSrc)
                #os.remove(_rootMountpointSrc)
                ComSystem.execMethod(os.remove,_rootMountpointSrc)
            else:
                log.debug("Cannot remove CDSL because " + _rootMountpointSrc + " is not a symbolic link")
                sys.exit(1)
                
        elif self.type == "shared":
            log.debug("Delete shared CDSL " + _rootMountpointSrc)
            #Delete Files if force is True
            if force == True and os.path.islink(_rootMountpointSrc):
                #self._removePath(os.path.realpath(_rootMountpointSrc),True)
                ComSystem.execMethod(self._removePath,os.path.realpath(_rootMountpointSrc),True)
                #self._removePath(os.path.realpath(_rootMountpointSrc.replace(_rootMountpoint,os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree_shared)))),True)
                ComSystem.execMethod(self._removePath,os.path.realpath(_rootMountpointSrc.replace(_rootMountpoint,os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree_shared)))),True)
            
            #Delete Symbolic Links
            _tmp = os.path.realpath(_rootMountpointSrc)
            for node in _tmpNodes:
                _rootMountpointCdsltreeNodeSrc = _tmp.replace(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree_shared)),os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree),node),1)
                #must be a link, otherwise something wents wrong by cdsl-creation
                if os.path.islink(_rootMountpointCdsltreeNodeSrc):
                    log.debug("Remove symbolic link " + _rootMountpointCdsltreeNodeSrc)
                    #os.remove(_rootMountpointCdsltreeNodeSrc)
                    ComSystem.execMethod(os.remove,_rootMountpointCdsltreeNodeSrc)
                else:
                    log.debug("Cannot remove CDSL because " + _rootMountpointCdsltreeNodeSrc + " is not a symbolic link")
                    sys.exit(1)
                
            if _nested == True and len(self.getSiblings()) == 0 and force==True:
                #self._removePath(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree_shared),re.sub('^/','', self.getParent().getParent().getParent().src + ".cdsl")),True)
                ComSystem.execMethod(self._removePath,os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree_shared),re.sub('^/','', self.getParent().getParent().getParent().src + ".cdsl")),True)
                
        else:
            raise CdslUnsupportedTypeException(self.type + " is not a supported cdsl type.") 
        
        log.debug("Delete CDSL from Inventoryfile")
        #delete cdsl also from xml inventory file
        #self.cdslRepository.delete(self)
        ComSystem.execMethod(self.cdslRepository.delete,self)
        
    def getParent(self):
        """
        Returns parent CDSL
        @rtype: list of ComoonicsCdsl
        """
        _tmpcdsls = []
        for cdsl in self.cdslRepository.getCdsls():
            #search cdsls whose sources are part of this cdsls source
            if re.compile("^"+cdsl.src+"[\w/]+").match(self.src):
                _tmpcdsls.append([self._pathdepth(cdsl.src),cdsl])
        #if some cdsls where found, sort them after pathdeepth and return the one with the longest 
        #equivalent path compared to this cdsl
        if len(_tmpcdsls) > 0:
            #sorted was first intruduced with python 2.4
            #_tmp2 = sorted(_tmpcdsls)[::-1]
            _tmpcdsls.sort()
            _tmpcdsls.reverse()
            
            return _tmpcdsls[0][1]
        
    def getChilds(self):
        """
        Returns child CDSLs
        @rtype: list of ComoonicsCdsl
        """
        _tmpcdsls = []
        from xml.dom.ext import PrettyPrint
        #compare which other cdsl sources contain the whole source of this cdsl
        for cdsl in self.cdslRepository.getCdsls():
            if re.compile("^"+self.src+"[\w/]+").match(cdsl.src):
                _tmpcdsls.append(cdsl)
        return _tmpcdsls
        
    def getSiblings(self):
        """
        Returns siblings of CDSLs.
        @rtype: list of ComoonicsCdsl
        """
        _tmpcdsls = []
        for cdsl in self.cdslRepository.getCdsls():
            #compare which cdsls have got a different source, but the same parent
            if ( self.src != cdsl.src ) and ( cdsl.getParent() == self.getParent() ):
                _tmpcdsls.append(cdsl)
        return _tmpcdsls
        
    def exists(self,root=None):
        """
        Verify if cdsl exists in filesystem. Verifies shared cdsl by testing symbolic 
        links
        @rtype: Boolean
        """
        if root != None:
            self.root = root
        _rootMountpoint = os.path.normpath(os.path.join(self.root,re.sub('^/','', self.mountpoint)))
        _rootMountpointSrc = os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','', self.src)))
        _rootMountpointCdsltreesharedSrc = os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree_shared),re.sub('^/','', self.src)))
        _rootMountpointCdsllinkSrc = os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsl_link),re.sub('^/','', self.src)))
        
        _olddir = os.getcwd()
        if os.path.exists(_rootMountpointSrc):
            os.chdir(os.path.dirname(_rootMountpointSrc))
            
        if os.path.islink(_rootMountpointSrc):
            # needed because os.path.realpath follows more than one symbolic link level
            _realpath = os.path.abspath(ComSystem.execLocalStatusOutput("ls -la " + _rootMountpointSrc)[1].split()[-1])
            if os.path.realpath(_rootMountpointSrc) != _realpath:
                log.debug("Given source only a ordinary symbolic link, but not a cdsl")
                os.chdir(_olddir)
                return False
        else:
            log.debug("Source " + _rootMountpointSrc + " is not a " + self.type + " CDSL, missing symbolic Link")
            os.chdir(_olddir)
            return False
         
        if self.type=="shared":
            # if cdsltree_shared is part of sources realpath but not of the overlying directory, it must be a shared cdsl!
            if os.path.realpath(_rootMountpointSrc).find(self.cdsltree_shared) != -1 and os.path.realpath(os.path.dirname(_rootMountpointSrc)).find(self.cdsltree_shared) == -1:
                _rootMountpointCdsltreesharedSrc = os.path.realpath(_rootMountpointSrc).replace(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsl_link)), "", 1)
                if not os.path.exists(_rootMountpointCdsltreesharedSrc):
                    log.debug("Needed directory " + _rootMountpointCdsltreesharedSrc + " does not exist.")
                    os.chdir(_olddir)
                    return False
                else:
                    os.chdir(_olddir)
                    return True
            else:
                log.debug("Source is part of an underlying CDSL, but its not a CDSL itself.")
                os.chdir(_olddir)
                return False
            
        elif self.type == "hostdependent":
            # if cdsl_link is part of sources realpath but not of the overlying directory, it must be a hostdependent cdsl!
            if os.path.realpath(_rootMountpointSrc).find(self.cdsl_link) != -1 and os.path.realpath(os.path.dirname(_rootMountpointSrc)).find(self.cdsl_link) == -1:
                _rootMountpointCdsllinkSrc = os.path.realpath(_rootMountpointSrc).replace(os.path.normpath(os.path.join(_rootMountpoint,re.sub('^/','', self.cdsltree_shared))), "",1)
                if not os.path.exists(_rootMountpointCdsllinkSrc):
                    log.debug("Needed directory " + _rootMountpointCdsllinkSrc + " does not exist.")
                    os.chdir(_olddir)
                    return False
                else:
                    os.chdir(_olddir)
                    return True
            else:
                log.debug("Source is part of an underlying CDSL, but its not a CDSL itself.")
                os.chdir(_olddir)
                return False
            
        else:
            log.debug("CDSL has got an illegal Type: " + self.type)
            os.chdir(_olddir)
            return False
        
    def setRoot(self,root):
        """
        Set chroot of cdsl, needed e.g. when a cdsl is picked out from inventoryfile
        and you work in an environment which is prepared for chroot
        @param root: chroot-path to set
        @type root: string
        """
        self.root = root

def main():
    """
    Method to check if Module handels nested cdsls correctly. Creates a nested 
    cdsl-structure and check every single cdsl for existance. Creates a cdsl-object 
    without commiting it to filesystem to check if exists()-method fails correctly.
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

    #create cluster objects
    clusterRepository = ClusterRepository(doc.documentElement,doc)
    clusterinfo = ClusterInfo(clusterRepository)
    
    # create cdsl objects
    cdslRepository = CdslRepository("test/cdsl5.xml")
    
    cdsl_1 = Cdsl("/hostdependent", "hostdependent", cdslRepository, clusterinfo, None)
    cdsl_2 = Cdsl("/hostdependent/shared", "shared", cdslRepository, clusterinfo, None)
    cdsl_3 = Cdsl("/hostdependent/shared/hostdependent_subdir", "hostdependent", cdslRepository, clusterinfo, None)
    cdsl_4 = Cdsl("/hostdependent/shared/hostdependent_subdir/shared_subdir", "shared", cdslRepository, clusterinfo, None)
    cdsl_5 = Cdsl("/hostdependent/shared/hostdependent_file", "hostdependent", cdslRepository, clusterinfo, None)
    cdsl_6 = Cdsl("/hostdependent/shared/hostdependent_subdir/shared_file", "shared", cdslRepository, clusterinfo, None)
       
    cdsl_1.commit(force=True)
    cdsl_2.commit(force=True)
    cdsl_3.commit(force=True)
    cdsl_4.commit(force=True)
    cdsl_5.commit(force=True)
    cdsl_6.commit(force=True)
    
    print "cdsl_1 exists(True): " + str(cdsl_1.exists())
    print "cdsl_2 exists(True): " + str(cdsl_2.exists())
    print "cdsl_3 exists(True): " + str(cdsl_3.exists())
    print "cdsl_4 exists(True): " + str(cdsl_4.exists())
    print "cdsl_5 exists(False): " + str(cdsl_5.exists())
    print "cdsl_6 exists(False): " + str(cdsl_6.exists())
    
    ComLog.setLevel(logging.DEBUG)
    cdsl_5.delete()
    
if __name__ == '__main__':
    ComLog.setLevel(logging.INFO)
    main()