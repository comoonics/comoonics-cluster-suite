"""Comoonics cdsl object module


Module to create and modify cdsls on filesystem and commit changes to L{CdslRepository}. Represents 
cdsl as an L{DataObject}.
"""


__version__ = "$Revision: 1.23 $"

# @(#)$File$
#
# Copyright (c) 2001 ATIX GmbH, 2007 ATIX AG.
# Einsteinstrasse 10, 85716 Unterschleissheim, Germany
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import shutil
import time

from comoonics import ComSystem
from comoonics import ComLog
from comoonics.ComDataObject import DataObject
from comoonics.cdsl import dirtrim, getCdsl, CdslUnsupportedTypeException, CdslPrefixWithoutNodeidsException
from comoonics.cdsl import CdslDoesNotExistException, CdslAlreadyExists, CdslOfSameType, CdslHasChildren , CdslNodeidsRequired
from comoonics.cdsl import CDSL_HOSTDEPENDENT_TYPE, CDSL_SHARED_TYPE, CDSL_UNKNOWN_TYPE

class Cdsl(DataObject):
    """
    Represents a cdsl as an L{DataObject} and provides methods to commit changes or test cdsls.
    """
    HOSTDEPENDENT_TYPE=CDSL_HOSTDEPENDENT_TYPE
    SHARED_TYPE=CDSL_SHARED_TYPE
    UNKNOWN_TYPE=CDSL_UNKNOWN_TYPE
    def __init__(self, src, _type, cdslRepository, clusterinfo=None, nodes=None, timestamp=None, ignoreerrors=False):
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
        import xml.dom
        self.nodes=None
        self.src = dirtrim(src)
        self.type = _type
        self.cdslRepository = cdslRepository
        self.clusterinfo = clusterinfo
        self.logger = ComLog.getLogger("comoonics.cdsl.ComCdsl.Cdsl")
        
        if timestamp != None:
            self.timestamp = timestamp
        else:
            self.timestamp = time.time()
        
        #get nodes from clusterinfo if nodelist is not setgiven
        if (nodes == None or len(nodes)==0) and clusterinfo != None:
            self.node_prefix = cdslRepository.getNodePrefix()
            self.use_nodeids = cdslRepository.getUseNodeids()
            self.maxnodeidnum = cdslRepository.getMaxnodeidnum()
        
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
        elif (nodes != None):
            self.nodes = nodes
            
        #no nodelist or clusterinfo is given OR both is given
        elif cdslRepository and not self.nodes:
            self.nodes=[]
            for node in range(1, int(cdslRepository.getMaxnodeidnum())+1): self.nodes.append(str(node))
        else:
            raise TypeError("Cdsl constructor called with wrong parameters. Propably no cdslrepository given.")
        
        if not self.nodes or len(self.nodes) == 0:
            raise CdslNodeidsRequired("""No node identities specified for this cdsl %s. 
At least on node identity is specified. Either specify a default with with the maxnodeidnum option or add nodes at will.""" %self.src)
        
        #create DOM-Element
        doc = cdslRepository.getDocument()
        topelement=None
        child = doc.documentElement.firstChild
        while child:
            # Do we care about the timestamp?? I think no!
            if child.nodeType == xml.dom.Node.ELEMENT_NODE and child.getAttribute("src") == self.src and child.getAttribute("type") == self.type:
                topelement=child
                break
            child = child.nextSibling
        if not topelement:
            topelement=cdslRepository.getDocument().createElement("cdsl")
            topelement.setAttribute("src",self.src)
            topelement.setAttribute("type",self.type)
            topelement.setAttribute("timestamp",str(self.timestamp))
        
            nodes=doc.createElement("nodes")
            topelement.appendChild(nodes)
        
            for node in self.nodes:
                node1=self._createNoderefElement(node, document=doc)
                nodes.appendChild(node1)

        
        #self.XmlElement = doc
        #element = xpath.Evaluate('/cdsl', self.XmlElement)[0]
        
        #super(Cdsl,self).__init__(element,self.XmlElement)
        super(Cdsl,self).__init__(topelement,doc)
        self.parent=None
        self.parent=self.getParent()
        if self.parent and self.parent.type == self.type and not ignoreerrors:
            raise CdslOfSameType("Cannot create the cdsl %s of the same type then the already existing cdsl %s." %(self.src, self.parent.src))

    def __str__(self):
        return self.toString(detailed=False)
    
    def toString(self, detailed=False):
        if not detailed:
            if self.hasAttribute("child"):
                return "%s %s" %(self.getAttribute("child"), self.src)
            else:
                return self.src
        else:
            return "%s: CDSLSource: %s, Nodeids: %s, timestamp: %s" %(self.getAttribute("child", self.src), self.src, self.nodes, self.timestamp)
    def __eq__(self, othercdsl):
        """
        Two cdsls are equal if their sources they refer to are equal and their repository is equal
        """
        return othercdsl and isinstance(othercdsl, Cdsl) and self.src == othercdsl.src and self.cdslRepository == othercdsl.cdslRepository
    
    def setSource(self, src):
        self.src=src
        self.setAttribute("src", src)
    
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
        _path=Path()
        _path.pushd(self.getBasePath())
        if not os.path.exists(self.src):
            return False

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
            try:
                _exists=os.path.lexists(_destpath) and \
                    os.path.samefile(_destpath, _cdslpath) and \
                    os.path.samefile(_destpath, _cdsllinkpath)
                if _exists:
                    _exists_once=True
                if not os.path.lexists(_destpath):
                    _exists_everywhere=False
            except OSError:
                _exists_once=False
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
        from comoonics.cdsl import CdslNotFoundException
        stripsource=self.isStripped()
        if not _path:
            _path=self.src
            stripsource=False
        _subpath=os.path.dirname(_path)
        if _subpath=="":
            return False
        # check if in repository
        try:
            self.cdslRepository.getCdsl(_subpath, stripsource=stripsource)
            return True
        except CdslNotFoundException:
            # not in repository so try to build one and check then
            self.logger.debug("isNested: cdsl %s is not in cdsl repo guessing." %_subpath)
            _tmp=getCdsl(_subpath, guessType(_subpath, self.cdslRepository), self.cdslRepository, None, self.nodes, stripsource=stripsource)
            if _tmp and _tmp.exists():
                return True
        
            return self.isNested(_subpath)

    def getParent(self, _path=None):
        """
        This method gets the parent for this cdsl. If there is no parent None is returned.
        @param _path: if path is given the path is taken instead of this cdsl itself.
        @type _path: string  
        @return: eReturns the parent CDSL
        @rtype: ComoonicsCdsl
        """
        if not self.parent:
            self.parent=self.findParent(_path)
        return self.parent
        
    def getBasePath(self):
        """
        Returns the path where these cdls are relative to.
        @return: the full path of the "root" where the cdsls are related to
        @rtype: string
        @note: This is a virtual method that has to be implemented by the child classes
        """
        return ""

    def getDestPaths(self):
        """
        returns the real destinationpath of this cdsl relative to the mountpoint
        @return: the real destinationpath as string without leading "/"
        @rtype: string
        @note: This is a virtual method that has to be implemented by the child classes
        """
        return ""
    
    def getCDSLPath(self):
        """
        returns the path to the cdsl itself relative to the mountpoint
        @return: the cdslpath as string without leading "/"
        @rtype: string
        @note: This is a virtual method that has to be implemented by the child classes
        """
        return ""
    
    def getCDSLLinkPath(self):
        """
        returns the path of this cdsl in the cdsllink tree relative to mountpoint
        @return: the cdsllink path as string without leading "/"
        @rtype: string
        """
        return self.src
    
    def findParent(self, path):
        """
        This method finds the parent for this cdsl. If there is no parent None is returned.
        This method should find the next parent for this cdsl.
        Let's suppose var => hostdep and var/lib shared
        findParent("var/lib") should return the "var" cdsl.
        This method must be implemented by the child classes.
        Here it will just return None.
        @param _path: if path is given the path is taken instead of this cdsl itself.
        @type _path: string  
        @return: Returns the parent CDSL
        @rtype: ComoonicsCdsl
        """
        return None
                
    def _createNoderefElement(self, node, document=None):
        if not document:
            document=self.getDocument()
        node1=document.createElement("noderef")
        node1.setAttribute("ref",str(node))
        return node1

class ComoonicsCdsl(Cdsl):
    """
    Represents a comoonics cdsl as an xml-object and provides methods to 
    commit changes, delete or check existence of cdsl on filesystem.
    """
    
    default_node = "default"

    def __init__(self, src, _type, cdslRepository, clusterinfo=None, nodes=None, timestamp=None, ignoreerrors=False, realpath=True, stripsource=True):
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
        @param realpath: Should this src path be resolved to its realpath. Default: True.
        @type  realpath: L{Boolean}
        @param stripsource: Should this src path be stripped and checked or taken as is. 
                            This can be switched of if read from repo (speed up). Default: True.
        @type  stripsource: L{Boolean}
        """

        #set reldir to current path
        self.reldir = os.getcwd()
        # private attribute to store stripped state.
        self._stripped=False

        self.logger = ComLog.getLogger("comoonics.cdsl.ComCdsl.ComoonicsCdsl")
        
        if stripsource and not self._stripped:
            src=cdslRepository.stripsrc(src, realpath=realpath)
            cdslRepository=cdslRepository.getRepositoryForCdsl(src)
        #add default node to a special nodelist
        super(ComoonicsCdsl,self).__init__(src, _type, cdslRepository, clusterinfo, nodes, timestamp, ignoreerrors=ignoreerrors)
        self.nodesWithDefaultdir = self.nodes[:]
        self.nodesWithDefaultdir.append(self.default_node)
        if stripsource and not self._stripped:
            src=cdslRepository.stripsrc(src, join=False, realpath=realpath)
            self._stripped=True
        self.setSource(src)

        #get needed pathes from cdslrepository and normalize them
        self.cdsltree = dirtrim(cdslRepository.getTreePath())
        self.cdsltree_shared = dirtrim(cdslRepository.getSharedTreepath())    
        self.default_dir = dirtrim(cdslRepository.getDefaultDir())
        self.cdsl_link = dirtrim(cdslRepository.getLinkPath())

    def isStripped(self):
        """
        Returns true if the cdsl source has already been stripped.
        """
        return self._stripped

    def getNodenames(self):
        """
        Returns a list of all nodenames to be used as pathbases. Means no ugly id_ in the name but only
        the nodeid for cdsl with nodeids and the nodenames otherwise.
        @return: a list of nodenames/nodeids
        @rtype: list<string>
        """
        _nodes=list()
        for _node in self.nodesWithDefaultdir:
            if self.cdslRepository.getUseNodeids() == "True":
                _node=str(_node).replace("id_", "", 1)
            _nodes.append(str(_node))
        return _nodes

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
        from comoonics.cdsl import strippath, stripleadingsep
        _paths=list()
        _parent=self.getParent()
        if not _parent:
            _tail=self.src
            _path=self.src
        else:
            _tail=stripleadingsep(strippath(self.src, _parent.src))
            _path=os.path.join(self.cdslRepository.expandCdsl(_parent), _tail)
        if self.isShared():
            for _node in self.getNodenames():
                _paths.append(os.path.join(self.cdsltree, _node, _path))
        elif self.isHostdependent():
            if self.isNested():
                _paths.append(os.path.join(self.cdsltree_shared, _path))
            else:
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
        return os.path.realpath(os.path.join(self.cdslRepository.root,self.cdslRepository.getMountpoint()))
        
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
        
    def _removePath(self,path,onerror=None):
        """
        Removes given path or paths.
        @param path: Path to file or directory to delete
        @type path: string|list<string>
        """
        if isinstance(path, basestring):
            if os.path.exists(path) or os.path.islink(path):
                self.logger.debug("Remove " + path)
                if not os.path.islink(path) and os.path.isdir(path):
                    ComSystem.execMethod(shutil.rmtree, path)
                else:
                    ComSystem.execMethod(os.remove, path)
            else:
                if onerror:
                    onerror(path)
                else:
                    self.logger.debug("_removePath(%s) does not exist. Skipping." %path)
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
            self.logger.debug("CDSL already exists, chancel commit")
            raise CdslAlreadyExists("Cdsl %s is already existant." %self.src)
        if self.isShared() and (self.getParent() == None or self.getParent().isShared()):
            self.logger.debug("The cdsl %s to be shared back seems to recide already in a shared area." %self.src)
            raise CdslOfSameType("The cdsl %s to be shared seems to recide already in a shared area." %self.src)
        if self.isHostdependent() and self.getParent() != None and self.getParent().isHostdependent():
            self.logger.debug("The cdsl %s to be hostdependent seems to recide alreay in an hostdependent area." %self.src)
            raise CdslOfSameType("The cdsl %s to be hostdependent seems to recide alreay in an hostdependent area." %self.src)
        elif self.isShared():
            if isSubPath(self.src, self.cdsltree_shared):
                self.logger.debug("Given source is already part of a hostdependent CDSL")
                raise CdslAlreadyExists("Cdsl %s is already a hostdependent cdsl." %self.src)
        elif self.isHostdependent():
            if isSubPath(self.src, self.getCDSLLinkPath()):
                self.logger.debug("Given source is already part of a hostdependent CDSL")
                raise CdslAlreadyExists("Cdsl %s is already a shared cdsl." %self.src)

        _path=Path()
        _path.pushd(self.getBasePath())
        if not os.path.exists(self.src):
            raise CdslDoesNotExistException("File %s for cdsl does not exist (cwd: %s). Cannot create." %(self.src, self.getBasePath()))
        self.cdslRepository.updateInfrastructure(nodes=self.getNodenames())
                
#        _expanded=self.cdslRepository.expandCdsl(self)
#        parent=self.getParent()
#        if parent:
#            _tail=strippath(self.src, parent.src)
#            _expandedforparent=os.path.join(parent.cdslRepository.expandCdsl(parent), _tail)
#        else:
#            _expandedforparent=_expanded
        _depth = self._pathdepth(self.src) -1
        if _depth > 0:
            if self.isShared():
                _depth=_depth+self._pathdepth(self.cdsltree)+1 # 1 because we need to add the node
            elif self.isHostdependent() and self.getParent() != None:
                _depth=_depth+self._pathdepth(self.cdsltree_shared)
            _relativepath = _depth * "../"
        else:
            _relativepath = ""
        
        # First copy or move the files to the destpaths...
        for destpath in self.getDestPaths():
            
            # Create the parentdir if it does not already exist
            parentdir=os.path.dirname(destpath)
            if not os.path.exists(parentdir):
                self.logger.debug("Create Directory " + parentdir)
                os.makedirs(parentdir)
            
            # if symlink and relative adapt to the relativness.
            if os.path.islink(self.src) and not self.src.startswith(os.sep):
                self.logger.debug("Creating link from %s => %s" %(os.path.join(_relativepath, self.src), destpath))
                ComSystem.execMethod(os.symlink, os.path.join(self._pathdepth(self.getCDSLLinkPath())*"../", os.path.realpath(self.src)[1:]), destpath)
            else:
                # Let's copy the data
                self.logger.debug("Copy Files: " + self.src + " => " + destpath)
                ComSystem.execLocalStatusOutput("cp -a " + self.src + " " + destpath)
            # if cdsl is shared we need to copy only once.
            if self.isShared():
                break

        # createdefault destination
#        if self.isHostdependent():
#            self.logger.debug("Copy Files: " + self.src + " => " + os.path.join(self.cdslRepository.getTree(), self.cdslRepository.getDefaultPath()))
#            ComSystem.execLocalStatusOutput("cp -a " + self.src + " " + self.cdslRepository.getDefaultPath())

        if self.isHostdependent():
            if force:
                self.logger.debug("Removing oldfile %s" %self.src)
                ComSystem.execLocalStatusOutput("rm -rf %s" %self.src)
            elif not force:
                self.logger.debug("Moving %s => %s.orig" %(self.src, self.src))
                ComSystem.execLocalStatusOutput("mv %s %s.orig" %(self.src, self.src))
        
        # Now create the symlinks
        for sourcepath in self.getSourcePaths():
            if self.isShared():
                # Either backup or remove!
                if not force:
                    self.logger.debug("Backup Files: " + sourcepath + " => " + sourcepath + ".orig")
                    ComSystem.execLocalStatusOutput("mv " + sourcepath + " " + sourcepath + ".orig")
                else:
                    self.logger.debug("Remove Files: " + sourcepath)
                    if os.path.isdir(sourcepath):
                        ComSystem.execMethod(shutil.rmtree, sourcepath)
                    if os.path.exists(sourcepath):
                        ComSystem.execMethod(os.remove, sourcepath)
                src=os.path.join(_relativepath, self.cdslRepository.getSharedTreepath(), self.cdslRepository.expandCdsl(self))
                dest=sourcepath
            elif self.isHostdependent():
                src=os.path.join(_relativepath, self.cdslRepository.getLinkPath(), self.cdslRepository.expandCdsl(self))
                dest=sourcepath
            self.logger.debug("Creating Link: %s => %s, currentpath: %s" %(src, dest, _path))
            ComSystem.execMethod(os.symlink, src, dest)
        _path.popd()
                            
        return ComSystem.execMethod(self.cdslRepository.commit,self)
    
    def delete(self,recursive=True, symbolic=True, force=False):
        """
        Deletes cdsl from filesystem and inventoryfile
        @param recursive: if set delete subcdsls (e.g. /host/shared/host when removing /host/shared)
        @type  recursive: Boolean
        @param symbolic: If set remove only symbolic links, if not set also remove content, too. Default: True (means only symbolic)
        @type  symbolic: Boolean
        @param force: Removes the cdsl independent from if all contents can be found or not. Default: False
        @type  force: Boolean
        """
        from comoonics.ComPath import Path
        from comoonics.cdsl import getNodeFromPath, isSubPath, commonpath, subpathsto

        if not force and not self.exists():
            raise CdslDoesNotExistException("Cdsl with source " + self.src + " does not exist, cannot delete.")
        if not force and not self.isShared() and not self.isHostdependent():
            raise CdslUnsupportedTypeException(self.type + " is not a supported cdsl type.")         
        #verify if cdsl contains other cdsl, if true delete these first
        #assume completeness of inventoryfile
        if recursive == True:
            _tmp = self.getChilds()
            for cdsl in _tmp:
                cdsl.delete(recursive=recursive, force=force, symbolic=symbolic)
        
        if self.getChilds():
            raise CdslHasChildren("Cdsl %s has children but no recursive option specified." %self.src)
        _cwd=Path()
        _cwd.pushd(self.getBasePath())
        
        #delete or move cdsl from filesystem first is from second to if second=None it is removed
        _delpaths=list()
        _movepairs=dict()
        _delpaths2=list()
        for _path in self.getSourcePaths():
            # This one is always a link to be removed
            if os.path.lexists(_path):
                _delpaths.append(_path)

        for _path in self.getDestPaths():
            if not symbolic:
                _delpaths.append(_path)
            else:            
                self.logger.debug(".delete(%s): Skipping path %s" %(self.src, _path))
                if self.isShared():
                    _movepairs[_path]=self.src
                else:
                    _nodeid=getNodeFromPath(_path, self.cdslRepository, not force)
                    _movepairs[_path]="%s.%s" %(self.src, _nodeid)
#                _delpaths[_path]=self.
                
        # tidy up the rest
        # Means:
        # * if we have siblings: clean up to longest common path with all siblings
        prefixes=list()
        if self.isHostdependent():
            for nodename in self.getNodenames():
                prefixes.append(os.path.join(self.cdslRepository.getTreePath(), nodename))
        elif self.isShared():
            prefixes.append(self.cdslRepository.getSharedTreepath())
        
        # Let's find our parent of same type
#        parent2nd=None
#        if self.getParent()!=None and self.getParent().getParent() != None:
#            parent2nd=self.getParent().getParent()        parent2nd=None
        parent=self.getParent()
            
        subpaths=list()
        siblings=self.getSiblings()
        if len(siblings) > 0:
            longestcommon=""
            for sibling in siblings:
                common=commonpath(self.src, sibling.src)
#                while common and common != longestcommon:
                if isSubPath(common, longestcommon):
                    longestcommon=common
            for _path in subpathsto(longestcommon, self.src):
                subpaths.append(_path)
        # * if we have a parent of same type and no siblings:  clean up to parent
#        elif parent2nd != None:
#            for _path in subpathsto(parent2nd.src, self.src):
#                subpaths.append(_path)
        # * if we don't have a parent and no siblings:  clean up to root+mountpoint
        # * if we have a parent of same type and no siblings:  clean up to parent
        elif parent != None and parent.getParent() != None:
            for _path in subpathsto(parent.src, self.src):
                subpaths.append(_path)
        else:
            for _path in subpathsto("", self.src):
                subpaths.append(_path)
                
        for path in subpaths:
            if str(path) != str(self.src):
                for prefix in prefixes:
                    if os.path.lexists(os.path.join(prefix, path)):
                        _delpaths2.append(os.path.join(prefix, path))
            
        self.logger.debug("delpaths2: %s" %_delpaths2)
                        
        self.logger.debug("delete: cwd: %s" %_cwd)
        self._removePath(_delpaths)
        for _from, _to in _movepairs.items():
            if not _to:
                self._removePath(_from)
            else:
#                for _delpath in _delpaths:
#                    if os.path.samefile(_delpath, _to):
#                        _delpaths.remove(_delpath)
                if os.path.islink(_to):
                    self._removePath(_to)
                shutil.move(_from, _to)
                # We must remove paths from the delpaths that have been moved to as they are
#                for _delpath in _delpaths:
#                    if os.path.samefile(_to, _delpath):
#                        _delpaths.remove(_delpath)
        self._removePath(_delpaths2)
        _deleted=ComSystem.execMethod(self.cdslRepository.delete, self)
        _cwd.popd()
        self.logger.debug("Delete CDSL from Inventoryfile")
        #delete cdsl also from xml inventory file
        #self.cdslRepository.delete(self)
        return _deleted
        
    def findParent(self, path=None):
        """
        This method calls itself recursively on the dirpart of the cdsl until it finds a cdsl in the repo.
        This is returned and the "directest" parent.
        @param path: if path is given the path is taken instead of this cdsl itself.
        @type path: string  
        @return: eReturns the parent CDSL
        @rtype: ComoonicsCdsl
        """
        import os.path
        from comoonics.ComPath import Path
        from comoonics.cdsl import stripleadingsep
        from comoonics.cdsl.ComCdslRepository import CdslNotFoundException
        # getParent is always called from a already stripped cdsl!!
        stripsource=False
        if path == None:
            path=os.path.dirname(self.src)
#        self.logger.debug("getParent(path: %s)" %_path)
        if not path or path.strip() == "" or os.path.normpath(stripleadingsep(os.path.join(self.cdslRepository.root, self.cdslRepository.getMountpoint()))) == path:
            return None
        
        try:
            cwd=Path()
            cwd.pushd(self.cdslRepository.workingdir)
            cdsl=self.cdslRepository.getCdsl(src=path, repository=self.cdslRepository, stripsource=stripsource)
            cwd.popd()
            return cdsl
        except CdslNotFoundException:
            cwd.popd()
            return self.getParent(os.path.dirname(path))  
        
    def getChilds(self):
        """
        Returns child CDSLs
        @rtype: list of ComoonicsCdsl
        """
        from comoonics.cdsl import isSubPath
        _tmpcdsls = []
        #_parent=self.getParent()
        #compare which other cdsl sources contain the whole source of this cdsl
        for cdsl in self.cdslRepository.getCdsls():
            cdslparent=cdsl.getParent()
            if cdsl.src != self.src and cdslparent and self.src == cdslparent.src and isSubPath(cdsl.src, self.src):
                self.logger.debug("getChilds: + %s" %cdsl)
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
            if self.src != cdsl.src and cdsl.getParent() == self.getParent() :
                _tmpcdsls.append(cdsl)
        return _tmpcdsls

    def addNode(self, node):
        """
        Adds a new node (identification) to the nodes that go with this cdsl.
        @param node: the node identification
        @type node: L{String}
        @return: Nothing
        @raise CdslNodeIDInUse: if the specified node is already associated with the cdsl
        """
        from comoonics.cdsl import CdslNodeIDInUse
        if node in self.nodes:
            raise CdslNodeIDInUse("CDSL Node ID %s is already in use for this cdsl cannot add this node." %node)
        
        self.nodes.append(node)
        self.nodes.sort()
        self.nodesWithDefaultdir=list(self.nodes)
        self.nodesWithDefaultdir.append(self.default_dir)
        self._updateNodesElement()

    def removeNode(self, node):
        """
        Removes an existing node (identification) from the nodes that go with this cdsl.
        @param node: the node identification
        @type node: L{String}
        @return: Nothing
        """
        if not node in self.nodes:
            return
        
        self.nodes.remove(node)
        self.nodes.sort()
        self.nodesWithDefaultdir=list(self.nodes)
        self.nodesWithDefaultdir.append(self.default_dir)
        self._updateNodesElement()
        
    def _updateNodesElement(self, nodes=None):
        """
        Update the nodes element with the current nodes list or parameter.
        """
        if not nodes:
            nodes=self.nodes
            
        nodeselement=self.getElement().getElementsByTagName("nodes")[0]
        nodestmp=list(nodes)
        for noderef in nodeselement.getElementsByTagName("noderef"):
            ref=noderef.getAttribute("ref")
            ref=ref.replace("id_", "", 1)
            if not ref in nodestmp:
                nodeselement.removeChild(noderef)
            else:
                nodestmp.remove(ref)
        for node in nodestmp:
            nodeselement.appendChild(self._createNoderefElement(node))
