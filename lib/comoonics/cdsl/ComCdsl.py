"""Comoonics cdsl object module


Module to create and modify cdsls on filesystem and commit changes to L{CdslRepository}. Represents 
cdsl as an L{DataObject}.
"""


__version__ = "$Revision: 1.11 $"

import re
import shutil
import time

from xml.dom.ext.reader.Sax2 import implementation

from comoonics import ComSystem
from comoonics import ComLog
from comoonics.ComExceptions import ComException
from comoonics.ComDataObject import DataObject
import comoonics.pythonosfix as os
from comoonics.cdsl import dirtrim

ComSystem.__EXEC_REALLY_DO = ""
log = ComLog.getLogger("comoonics.cdsl.ComCdsl")

class CdslInitException(ComException):pass
class CdslUnsupportedTypeException(ComException):pass
class CdslFileHandlingException(ComException):pass
class CdslPrefixWithoutNodeidsException(ComException):pass
class CdslDoesNotExistException(ComException):pass
class CdslSourcePathIsAlreadyCdsl(ComException): pass
class CdslAlreadyExists(ComException): pass
class CdslIsNoCdsl(ComException): pass

class Cdsl(DataObject):
    """
    Represents a cdsl as an L{DataObject} and provides methods to commit changes or test cdsls.
    """
    HOSTDEPENDENT_TYPE="hostdependent"
    SHARED_TYPE="shared"
    UNKNOWN_TYPE="unknown"
    
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
    
    def __init__(self, src, _type, cdslRepository, clusterinfo=None, nodes=None, timestamp=None):
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
        self.src = dirtrim(src)
        self.type = _type
        self.cdslRepository = cdslRepository
        self.clusterinfo = clusterinfo
        
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
        element = doc.documentElement
        
        #super(Cdsl,self).__init__(element,self.XmlElement)
        super(Cdsl,self).__init__(element,doc)

    def __str__(self):
        return self.src
    
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
        @return: Returns the deleted cdsl
        @rtype: L{Cdsl}
        """
        return self.cdslRepository.delete(self)
    
    def exists(self):
        """
        Checks if the destpath file exists (no dead end) and if destpath, cdslpath and cdsllinkpath are 
        the same file.
        This seems to be more complicated then expected ;-) . So here the current approach:
        Case 1 Not nested:
        If a CDSL is not nested it exists if the sourcepath, the cdsllinkpath and one destpath are exactly 
        the same file and all other destpaths just exist.
        Case 2 nested and hostdependent: 
        A CDSL exists if the resolved path is nested and the sourcepath is a cdsl shared path and the 
        link's destpath is a hostdependent path and one resolved destpaths is the same file then the 
        source and all other destpaths exist.
        Case 3 nested and shared:
        A CDSL exists if the resolved path is nested and the sourcepath is a cdsl hostdependent path and 
        the link's destpath is a cdsl shared path and the resolved destpath exists. Not sure about if 
        also all possible hostdependent sources should exist?. 
        @return: True if this cdsl exists
        @rtype: Boolean
        """
        from comoonics.ComPath import Path
        from comoonics.cdsl import ltrimDir, isHostdependentPath, isSharedPath
        _path=Path(self.getBasePath())
        _path.pushd()
        _exists=False
        _cdslpath=self.getCDSLPath()
        _cdsllinkpath=self.getCDSLLinkPath()
        if not os.path.islink(_cdslpath):
            _path.popd()
            return False
        _cdslreadpath=ltrimDir(os.readlink(_cdslpath))
        if self.isNested():
            # Now we start with all cases that hold for being nested
            if self.isShared():
                # Case 2 (Hostdependent and nested)
                if isHostdependentPath(_cdslreadpath, self.cdslRepository) or not isSharedPath(_cdslreadpath, self.cdslRepository):
                    _path.popd()
                    return False
            elif self.isHostdependent():
                # Case 3 (shared and nested)
                if not isHostdependentPath(_cdslreadpath, self.cdslRepository) or isSharedPath(_cdslreadpath, self.cdslRepository):
                    _path.popd()
                    return False
        _exists_once=False
        _exists_everywhere=True
        for _destpath in self.getDestPaths(): 
            _exists=os.path.exists(_destpath) and \
                os.path.samefile(_destpath, _cdslpath) and \
                os.path.samefile(_destpath, _cdsllinkpath)
            if _exists:
                _exists_once=True
            if not os.path.exists(_destpath):
                _exists_everywhere=False
        _path.popd()
        return _exists_once and _exists_everywhere
    
    def isHostdependent(self):
        """
        Checks if this cdsl is a hostdependent cdsl
        @return: True is this cdsl is hostdependent or False if it isn't
        @rtype: Boolean
        """
        return self.type == self.HOSTDEPENDENT_TYPE 
    
    def isShared(self):
        """
        Checks if this cdsl is a shared cdsl
        @return: True is this cdsl is shared or False if it isn't
        @rtype: Boolean
        """
        return self.type == self.SHARED_TYPE 

    def isUnknown(self):
        """
        Checks if this cdsl is a unknown cdsl
        @return: True is this cdsl is unknown or False if it isn't
        @rtype: Boolean
        """
        return self.type == self.UNKNOWN_TYPE 

    def isNested(self, _path=None):
        """
        Checks if this cdsl is a nested one if path given the path is taken into account.
        @param _path: if given this path is taken else the cdsl itself.
        @type _path: string|None  
        @return: True if the cdsl is e.g. a hostdependent shared one. Otherwise False
        @rtype: Boolean
        """
        from comoonics.cdsl import guessType
        if not _path:
            _path=self.src
        _subpath=os.path.dirname(_path)
        if _subpath=="":
            return False
        # check if in repository
        if self.cdslRepository.getCdsl(_subpath):
            return True
        else:
            # not in repository so try to build one and check then
            log.debug("isNested: cdsl %s is not in cdsl repo guessing." %_subpath)
            _tmp=Cdsl(_subpath, guessType(_subpath, self.cdslRepository), self.cdslRepository, None, self.nodes)
            if _tmp and _tmp.exists():
                return True
        
            return self.isNested(_subpath)

    def getBasePath(self):
        """
        Returns the path where these cdls are relative to.
        @return: the full path of the "root" where the cdsls are related to
        @rtype: string
        @note: This is a virtual method that has to be implemented by the child classes
        """
        pass

    def getDestPaths(self):
        """
        returns the real destinationpath of this cdsl relative to the mountpoint
        @return: the real destinationpath as string without leading "/"
        @rtype: string
        @note: This is a virtual method that has to be implemented by the child classes
        """
        pass
    
    def getCDSLPath(self):
        """
        returns the path to the cdsl itself relative to the mountpoint
        @return: the cdslpath as string without leading "/"
        @rtype: string
        @note: This is a virtual method that has to be implemented by the child classes
        """
        pass
    
    def getCDSLLinkPath(self):
        """
        returns the path of this cdsl in the cdsllink tree relative to mountpoint
        @return: the cdsllink path as string without leading "/"
        @rtype: string
        """
        return self.src

class ComoonicsCdsl(Cdsl):
    """
    Represents a comoonics cdsl as an xml-object and provides methods to 
    commit changes, delete or check existence of cdsl on filesystem.
    """
    
    default_node = "default"
    
    def __init__(self, src, _type, cdslRepository, clusterinfo=None, nodes=None, timestamp=None):
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
        super(ComoonicsCdsl,self).__init__(src, _type, cdslRepository, clusterinfo, nodes, timestamp)
        
        #set reldir to current path
        self.reldir = os.getcwd()
        
        #get needed pathes from cdslrepository and normalize them
        self.cdsltree = dirtrim(cdslRepository.getDefaultCdsltree())
        self.cdsltree_shared = dirtrim(cdslRepository.getDefaultCdsltreeShared())    
        self.default_dir = dirtrim(cdslRepository.getDefaultDefaultDir())
        self.cdsl_link = dirtrim(cdslRepository.getDefaultCdslLink())
        
        self.cdslRepository = cdslRepository
        self.clusterinfo = clusterinfo

        #add default node to a special nodelist
        self.nodesWithDefaultdir = self.nodes[:]
        self.nodesWithDefaultdir.append(self.default_node)

    def getNodenames(self):
        """
        Returns a list of all nodenames to be used as pathbases. Means no ugly id_ in the name but only
        the nodeid for cdsl with nodeids and the nodenames otherwise.
        @return: a list of nodenames/nodeids
        @rtype: list<string>
        """
        _nodes=list()
        for _node in self.nodesWithDefaultdir:
            if self.cdslRepository.getDefaultUseNodeids() == "True":
                _node=_node.replace("id_", "", 1)
            _nodes.append(str(_node))
        return _nodes

    def _getSubPathsToParent(self):
        """
        This method will return the subpaths to the parent. 
        If there is no parent the whole path will be returned
        """
        _parent=self.getParent()
        _paths=list()
        _src=self.src
        _expanded=self.cdslRepository.expandCdsl(self)
        if not _parent:
            _parent=""
        else:
            _parent=_parent.src
        _head, _tail=os.path.split(_src)
        _ehead, _tail=os.path.split(_expanded)
        while _head != _parent and _head != "":
            _paths.append(_ehead)
            _head, _tail=os.path.split(_head)
            _ehead, _tail=os.path.split(_ehead)
        
        return _paths

    def getDestPaths(self):
        """
        returns the real destinationpaths of this cdsl relative to the mountpoint. These might be one ore
        multiple paths. For a hostdependent cdsl these are all paths to the different destinations and for
        a shared cdsl only one path to the "shared" destination.
        @return: the real destinationpaths as list without leading "/"
        @rtype: list<string>
        """
        _paths=list()
        _path=self.cdslRepository.expandCdsl(self)
        if self.isShared():
            _paths.append(os.path.join(self.cdsltree_shared, _path))
        elif self.isHostdependent():
            for _node in self.getNodenames():
                _paths.append(os.path.join(self.cdsltree, _node, _path))
        return _paths
    
    def getSourcePaths(self):
        """
        Returns a list of paths pointing to the destination(s). These might be multiple paths when talking
        about a shared cdsl or just one when talking about a hostdependent one. This is the counterpart to
        getDestPaths. Means the source path leads to the destpath.
        @return: a list of paths (relative)
        @rtype: list<string> 
        """
        _paths=list()
        _path=self.cdslRepository.expandCdsl(self)
        if self.isShared():
            for _node in self.getNodenames():
                _paths.append(os.path.join(self.cdsltree, _node, _path))
        elif self.isHostdependent():
            if self.isNested():
                _paths.append(os.path.join(self.cdsltree_shared, _path))
            _paths.append(self.src)
        return _paths                  
    
    def getCDSLPath(self):
        """
        returns the path to the cdsl itself relative to the mountpoint
        @return: the cdslpath as string without leading "/"
        @rtype: string
        """
        return self.src
    
    def getCDSLLinkPath(self):
        """
        returns the path of this cdsl in the cdsllink tree relative to mountpoint
        @return: the cdsllink path as string without leading "/"
        @rtype: string
        """
        if self.isShared():
            return os.path.join(self.cdsltree_shared, self.cdslRepository.expandCdsl(self))
        else:
            return os.path.join(self.cdsl_link, self.cdslRepository.expandCdsl(self))

    def getBasePath(self):
        """
        Returns the path where these cdls are relative to.
        @return: the full path of the "root" where the cdsls are related to
        @rtype: string
        @note: This is a virtual method that has to be implemented by the child classes
        """
        return os.path.realpath(os.path.join(self.cdslRepository.root,self.cdslRepository.getDefaultMountpoint()))
        
    def _pathdepth(self,path):
        """
        Method to calculate the depth of a given path.
        @param path: Path
        @type path: string
        @return: Depth of given path
        @rtype: int
        """
        _path=dirtrim(os.path.normpath(path))
        if not _path or _path == "":
            return 0
        else:
            return _path.count(os.sep)+1
        
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
        
    def _removePath(self,path):
        """
        Removes given path or paths.
        @param path: Path to file or directory to delete
        @type path: string|list<string>
        """
        if isinstance(path, basestring):
            if os.path.exists(path):
                log.debug("Remove " + path)
                if not os.path.islink(path) and os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
        else:
            for _path in path:
                self._removePath(_path)

    def commit(self,force=False):
        """
        Commit new or changed cdsl to filesystem and inventoryfile
        @param force: skip Backup when set and overwrite existing files/directories/links
        @type force: Boolean
        """
        from comoonics.ComPath import Path
        from comoonics.cdsl import isSubPath
        #important pathes to work with cdsls
	    #####
        # Chancel creation of cdsl if it already exists
        # or a cdsl of another type with same src exists
        # or creation is insane because underlying structure 
        # is of same type as cdsl which should be created
        #####       
        if self.exists():
            log.debug("CDSL already exists, chancel commit")
            raise CdslAlreadyExists("Cdsl %s is already existant." %self.src)
        elif self.isShared():
            if isSubPath(self.src, self.cdsltree_shared):
                log.debug("Given source is already part of a hostdependent CDSL")
                raise CdslAlreadyExists("Cdsl %s is already a hostdependent cdsl." %self.src)
        elif self.isHostdependent():
            if isSubPath(self.src, self.getCDSLLinkPath()):
                log.debug("Given source is already part of a hostdependent CDSL")
                raise CdslAlreadyExists("Cdsl %s is already a shared cdsl." %self.src)

        _path=Path(self.getBasePath())
        _path.pushd()
                
        _expanded=self.cdslRepository.expandCdsl(self)
        _depth = self._pathdepth(self.src) -1
        if _depth > 0:
            if self.isShared():
                _depth=_depth+self._pathdepth(self.cdsltree)+1 # 1 because we need to add the node
            elif self.isHostdependent():
                _depth=_depth+self._pathdepth(self.cdsltree_shared)
            _relativepath = _depth * "../"
        else:
            _relativepath = ""
        if self.isShared():
            #####
            # Check if cdsl structure is nested (e.g. /hostdependent/shared/hostdependent/shared)
            # and check for value of /root/mountpoint/cdsltree_shared/src
            ##### 

            #####
            # If force is set: moves content of first node in array self.node[] to shared tree
            # If force is not set: copy content of first node
            # If src does not exist, create a file with this path
            #####
            
            # create unterlying directorystructure for cdsltree_shared/src (if not existing)
            _sharedsrc=os.path.join(self.cdsltree_shared, _expanded)
            _nodesrc=os.path.join(self.cdsltree, str(self.nodes[0]), _expanded)
            if not os.path.exists(os.path.dirname(_sharedsrc)):
                log.debug("Create Directory " + os.path.dirname(_sharedsrc))
                ComSystem.execMethod(os.makedirs,os.path.dirname(_sharedsrc))
             
            if os.path.exists(_nodesrc) and force == True:
                log.debug("Move Files to shared tree: " + self.src + " => " + os.path.dirname(_sharedsrc))
                #remove file if it is already existing (and force is set)
                if force:
                    ComSystem.execMethod(self._removePath,_sharedsrc)
                ComSystem.execMethod(shutil.move,self.src,_sharedsrc)      
            elif os.path.exists(_nodesrc) and force == False:
                log.debug("Copy Files to shared tree: " + self.src + " => " + os.path.dirname(_sharedsrc))
                if os.path.isdir(self.src):
                    #Cannot use copytree here because of problems when copying sockets
                    #log.debug("copytree " + _rootMountpointSrc + ".orig => " + _rootMountpointCdsltreesharedSrc)
                    #shutil.copytree(_rootMountpointSrc + ".orig", _rootMountpointCdsltreesharedSrc,True)
                    ComSystem.execLocalStatusOutput("cp -a " + self.src + " " + _sharedsrc)
                elif os.path.isfile(self.src):
                    log.debug("copyfile " + self.src + _sharedsrc)
                    ComSystem.execMethod(shutil.copy2,self.src, _sharedsrc)
                        
            else:
                #if force is set and file is already existing, remove it
                if force:
                    ComSystem.execMethod(self._removePath,_sharedsrc)
                #if given src is not a existing file/directory, create empty file with given path
                ComSystem.execMethod(self._createEmptyFile,_sharedsrc,force)
            
            #####
            # move (yet) hostdepedent directories to source.orig for every node if force is not set (create a backup)
            # remove (yet) hostdepedent directories of every node if force is set (skip backup)
            # if given source does not exist, skip both, because there is nothing to move or remove
            #####
            _relsharedsrc = os.path.join(_relativepath, _sharedsrc)
            
            for node in self.nodesWithDefaultdir:
                _nodesrc = os.path.join(self.cdsltree,str(node),_expanded)
                
                #if given source exists and force isn't set, move source to source.orig
                if os.path.exists(_nodesrc) and force == False:
                    log.debug("Backing up " + _nodesrc + " => " + _nodesrc + ".orig ...")
                    ComSystem.execMethod(shutil.move,_nodesrc , _nodesrc + ".orig")
                    
                #if given source exists and force is set, remove source from hostdependent cdsltree
                elif os.path.exists(_nodesrc) and force == True:
                    ComSystem.execMethod(self._removePath,_nodesrc)
                 
                #if given src does not exist, create underlying directories        
                elif  not os.path.exists(os.path.dirname(_nodesrc)):
                    ComSystem.execMethod(os.makedirs,os.path.dirname(_nodesrc))
                          
#                _path.pushd(os.path.dirname(self.src))
                log.debug("Creating needed symbolic link...")
                ComSystem.execMethod(os.symlink, _relsharedsrc, _nodesrc)
#                _path.popd()
                
        elif self.isHostdependent():
            #####
            # Copy source to hostdependent directory of every node
            # Use dummyfile is source does not exist
            #####
            log.debug("Creating/Copying the file to all hosts...")
            for node in self.nodesWithDefaultdir:
                _nodesrc = os.path.join(self.cdsltree,str(node), _expanded)
                
                if os.path.exists(self.src):
                    log.debug("Copying " + self.src + " => " + _nodesrc + "...")
                    #if force is set and target directory already exists, remove it
                    if force:
                        ComSystem.execMethod(self._removePath,_nodesrc)
                    if not os.path.exists(os.path.dirname(_nodesrc)):
                        ComSystem.execMethod(os.makedirs,os.path.dirname(_nodesrc))
                    if os.path.isdir(self.src):
                        #Cannot use copytree here because of problems when copying sockets
                        #log.debug("copytree " + _rootMountpointSrc + " => " + _rootMountpointCdsltreeNodeSrc)
                        #shutil.copytree(_rootMountpointSrc,_rootMountpointCdsltreeNodeSrc,True)
                        ComSystem.execLocalStatusOutput("cp -a " + self.src + " " + _nodesrc)
                        
                    elif os.path.isfile(self.src):                  
                        #copy given source to cdsl-directories
                        ComSystem.execMethod(shutil.copy2,self.src,_nodesrc)
                else:
                    #if given src is not a existing file/directory, create empty file with given path
                    ComSystem.execMethod(self._createEmptyFile,_nodesrc,force)
            
            #####
            # Backup source to source.orig
            # if force is not set and no dummyfile was created
            # remove source
            #####
            if os.path.exists(self.src):
                if force == False:
                    log.debug("Moving " + self.src + " => " + self.src + ".orig...")
                    ComSystem.execMethod(shutil.move,self.src,self.src + ".orig")
                else:
                    if force:
                        ComSystem.execMethod(self._removePath,self.src)
        
            #####
            # Update needed symbolic links
            #####
            log.debug("Creating needed symbolic links...")
            
#            _path.pushd(os.path.dirname(self.src))            
            _linkpath = os.path.join(_relativepath, self.cdsl_link,_expanded)
                
            ComSystem.execMethod(os.symlink, os.path.normpath(_linkpath), self.src)
#            _path.popd()
        #####_
        # if type of cdsl is wheater shared nor hostdependent, a error has been accured
        #####
        else:
            _path.popd()
            raise CdslUnsupportedTypeException(self.type + " is not a supported cdsl type.")
        
        #####
        # Update inventoryfile
        # same procedure for changed and new hostdependent/shared cdsls
        #####
        _path.popd()
        log.debug("Updating cdsl-inventoryfile")
        return ComSystem.execMethod(self.cdslRepository.commit,self)
    
    def delete(self,recursive=True,force=True):
        """
        Deletes cdsl from filesystem and inventoryfile
        @param force: If not set remove only symbolic links, if set remove content, too
        @type force: Boolean
        @param recursive: if set delete subcdsls (e.g. /host/shared/host when removing /host/shared)
        @type recursive: Boolean
        """
        from comoonics.ComPath import Path

        if not self.exists():
            raise CdslDoesNotExistException("Cdsl with source " + self.src + " does not exist, cannot delete.")
        if not self.isShared() and not self.isHostdependent():
            raise CdslUnsupportedTypeException(self.type + " is not a supported cdsl type.")         
        
        #verify if cdsl contains other cdsl, if true delete these first
        #assume completeness of inventoryfile
        if recursive == True:
            _tmp = self.getChilds()
            for cdsl in self.getChilds():
                cdsl.delete(recursive)
        
        _cwd=Path(self.getBasePath())
        _cwd.pushd()
        
        #delete cdsl from filesystem
        _delpaths=list()
        for _path in self.getSourcePaths():
            _delpaths.append(_path)

        if force:
            for _path in self.getDestPaths():
                _delpaths.append(_path)
                
            # tidy up the rest
            for _path in self._getSubPathsToParent():
                _delpaths.append(_path)
                
#            _parent=self.getParent()
#            if len(self.getSiblings())==0 and not _parent.isNested():
#                _expanded=self.cdslRepository.expandCdsl(self)
#                _delpaths.append(_expanded[:-len(self.src[len(_parent.src):])])
            
        self._removePath(_delpaths)
        
        _cwd.popd()
        log.debug("Delete CDSL from Inventoryfile")
        #delete cdsl also from xml inventory file
        #self.cdslRepository.delete(self)
        return ComSystem.execMethod(self.cdslRepository.delete,self)
        
    def getParent(self, _path=None):
        """
        This method calls itself recursively on the dirpart of the cdsl until it finds a cdsl in the repo.
        This is returned and the "directest" parent.
        @param _path: if path is given the path is taken instead of this cdsl itself.
        @type _path: string  
        @return: eReturns the parent CDSL
        @rtype: ComoonicsCdsl
        """
        if not _path:
            _path=os.path.dirname(self.src)
        if not _path or _path.strip() == "":
            return None
        
        _cdsl=self.cdslRepository.getCdsl(_path)
        if _cdsl:
            return _cdsl
        else:
            return self.getParent(os.path.dirname(_path))  
        
    def getChilds(self):
        """
        Returns child CDSLs
        @rtype: list of ComoonicsCdsl
        """
        from comoonics.cdsl import isSubPath
        _tmpcdsls = []
        _parent=self.getParent()
        #compare which other cdsl sources contain the whole source of this cdsl
        for cdsl in self.cdslRepository.getCdsls():
            if cdsl.src != self.src and _parent == cdsl.getParent() and isSubPath(cdsl.src, self.src):
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
