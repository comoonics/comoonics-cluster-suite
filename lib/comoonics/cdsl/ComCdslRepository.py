"""Comoonics cdslrepository object module


Represents cdsl-inventoryfile as an L{DataObject} and holds list 
of cdsl objects. The cdsl-inventoryfile contains information about 
the created cdsls and default values which are needed for cdsl 
management (modifying, creating, deleting).

"""

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

__version__ = "$Revision: 1.23 $"

import fcntl # needed for filelocking
import re

import xml.dom

from comoonics import ComLog
from comoonics.ComExceptions import ComException
from comoonics.ComDataObject import DataObject
from comoonics import ComSystem
from comoonics.ComPath import Path

from comoonics.cdsl import stripleadingsep, dirtrim

import os
import os.path

log = ComLog.getLogger("comoonics.cdsl.ComCdslRepository")

class CdslNotFoundException(ComException):
    def __init__(self, src, repository=None):
        ComException.__init__(self, src)
        self.repository=repository
    def __str__(self):
        return "Could not find Cdsl \"%s\" in repository %s" %(self.value, self.repository)
class CdslRepositoryNotConfigfileException(ComException):pass
class CdslVersionException(ComException): pass

class CdslRepository(DataObject):
    """
    Represents cdsl-inventoryfile as L{DataObject}
    """
    cdsls_path = "/cdsls"
    cdslDefaults_path = cdsls_path + "/defaults"
    cdsltree = "cdsltree"
    
    log = ComLog.getLogger("comoonics.cdsl.ComCdslRepository")

    def __init__(self, **kwds):
        """
        __init__(resource=string, validate=bool)
        __init__(doc=xml.dom.Document, resource=string, element=xml.dom.Element)
        Constructs a new CdslRepository from given resource. Creates 
        a list of cdsls from resource to provide an easy access to them.
        @param resource: path to resource, should be created if it does not already exist.
        @type resource: string
        @param validate: set to false to skip validation of resource (Default: True)
        @type validate: Boolean
        @param document: the preparsed document.
        @type xml.dom.Document
        @param element: the preparsed element. Defaults to dom.getDocumentElement()
        @type xml.dom.Element
        """     
        import stat  
        element=None
        doc=None
        self.cdsls = dict()
        self.resource=kwds.get("resource")
        if kwds.has_key("resource") and kwds.has_key("document"):
            doc=kwds.get("document")
            element=kwds.get("element", doc.documentElement)
        elif kwds.has_key("resource"):
            self.validate = kwds.get("validate", False)
            from comoonics import XmlTools
            if self.resource and os.path.exists(self.resource):
                if os.stat(self.resource)[stat.ST_SIZE] <= 0:
                    raise IOError("Repository %s has zero size. Cannot read. Try to reconstruct or restore the repository (com-cdsllinvchk)." %self.resource)
                _file = os.fdopen(os.open(self.resource,os.O_RDONLY))
                try:
                    doc=XmlTools.createDOMfromXML(_file, None, self.validate)
                except Exception, arg:
                    log.critical("Problem while reading XML: " + str(arg))
                    raise
                _file.close()
            else:
                doc=self._createEmptyDocumentStructure(**kwds)
#                raise IOError(2, "Could not find cdsl repository file to parse %s" %self.resource)
            if not element:
                element = doc.documentElement
        else:
            raise TypeError("Constructor for ComoonicsCDSLRepository was not called with parameters resource or rootelement and resource.")
        
        super(CdslRepository,self).__init__(element, doc)
        self._updateFromElement(self.getElement(), self.getDocument())
        
    def _createEmptyDocumentStructure(self, **kwds):
        """
        Abstract method that should create an empty xml.dom.Document that represents and initial document for the cdslrepository implementation
        @param kwds: map of keyword value pairs that might be needed for creating this structure. Ususally the params from the constructor are given.
        @type kwds:  double star map.
        @return: the empty document that was created
        @rtype:  xml.dom.Document
        """
        return None
    
    def _updateFromElement(self, element, document):
        """
        Updates the internal structures from the given element und document.
        """
        pass
        
    def __str__(self):
        return "%s(%u cdsls, resource: %s)" %(self.__class__.__name__, len(self.cdsls.keys()), self.getResource())
                                   
    def buildInfrastructure(self,clusterinfo):
        """
        Placeholder for Method to prepare cluster 
        to handle cdsls
        @param clusterinfo: Clusterinfo with needed attributes
        @type clusterinfo: L{ComoonicsClusterInfo}
        """
        pass
    
    def hasCdsl(self, src):
        """
        Uses given source to return True if their is a cdsl with that name
        @param src: Path of searched cdsl
        @type src: string
        @return: True if cdsl is found, False otherwise
        @rtype: Boolean
        """
        try:
            self.getCdsl(src)
            return True
        except CdslNotFoundException:
            return False
    def getCdsl(self,src):
        """
        Uses given source to return matching cdsl
        @param src: Path of searched cdsl
        @type src: string
        @return: cdsl-object belonging to given path
        @rtype: L{ComoonicsCdsl}
        @raise CdslRepositoryNotFound: if the cdsl could not be found in the repository 
        """
        src = dirtrim(os.path.normpath(src))
        if self.cdsls.has_key(src):
            return self.cdsls[src]
        else:
            for cdsl in self.cdsls.values():
                if (cdsl.src == src):
                    return cdsl
        raise CdslNotFoundException(src,self)
            
    def getCdsls(self):
        """
        @rtype: ComoonicsCdsl
        """
        return self.cdsls.values()
    
    def getResource(self):
        """
        Return the resource as filename where the underlying database can be found
        """
        return self.resource
    
    def walkCdsls(self, clusterinfo=None, cdsls=None, onerror=None):
        """
        Only walks through the repository cdsl by cdsl as generator to be used by for
        """
        if not cdsls or len(cdsls)==0:
            for cdsl in self.getCdsls():
                yield cdsl
        else:
            for cdsl in cdsls:
                try:
                    yield self.getCdsl(cdsl)
                except CdslNotFoundException, e:
                    self.log.debug("walkCdsls: Skipping %s because it does not exists." %cdsl)
                    if onerror:
                        yield onerror(self, e.value, clusterinfo)
                    else:
                        raise
                     

    def delete(self,cdsl):
        """
        Deletes cdsl entry in inventoryfile if existing
        @param cdsl: cdsl to delete
        @type cdsl: L{ComoonicsCdsl}
        """
        _tmp=self.getCdsl(cdsl)
        del self.cdsls[cdsl]
        return _tmp

    def exists(self,cdsl):
        """
        Looks if a given cdsl already exists in inventoryfile
        @param cdsl: Cdsl to test existenz later 
        @type cdsl: L{ComoonicsCdsl}
        @rtype: Boolean
        """
        return self.hasCdsl(cdsl.src)

    def commit(self,cdsl):
        """
        Adds or modifies cdsl entry in inventoryfile (depending on existing entry with the same src attribute like the given cdsl)
        @param cdsl: cdsl to commit
        @type cdsl: L{ComoonicsCdsl}
        """
        pass
    
    def expandCdsl(self, cdsl):
        """
        expand this cdsl if need be.
        @param _cdsl: the cdsl.
        @type _cdsl: comoonics.cdsl.ComCdsl.Cdsl|string
        @return: returns the expanded path of the cdsl without either cdsltreeShared, cdsllink, ..
        @rtype: string 
        """
        from ComCdsl import Cdsl
        if isinstance(Cdsl, cdsl):
            return cdsl.src
        else:
            return cdsl
    
    def unexpand(self, path):
        """
        unexpands the given path.
        @param path: the path that should be cleared of all cdsl expansions
        @type path: L{String}
        @return: returns the unexpanded path
        @rtype: L{String}
        """
        return path
    
    def isExpandedDir(self, src):
        """
        Returns True if this path is and expanded path
        """
        return False
        
class ComoonicsCdslRepository(CdslRepository):
    """
    Represents cdsl-inventoryfile and provides methods to add, modify or delete 
    entries. Theres also the possibility to check if an given cdsl is included in 
    the inventoryfile and some methods to return the default values which are 
    defined at the bottom of the file.

    Additional a method provides the functionality to build the needed 
    infrastructure which is needed to create cdsls.
    """
    
    version="2.0"
    
    cdsls_element = "cdsls"
    cdsls_version_attribute="config_version"
    cdsls_tree_attribute = "tree"
    cdsls_sharedtree_attribute = "sharedtree"
    cdsls_link_attribute = "link"
    cdsls_maxnodeidnum_attribute = "maxnodeidnum"
    cdsls_usenodeids_attribute = "use_nodeids"
    #defaults_root_attribute = "root"
    cdsls_mountpoint_attribute = "mountpoint"
    cdsls_defaultdir_attribute = "default_dir"
    cdsls_nodeprefix_attribute = "node_prefix"
    cdsls_expand_string_attribute="expandstring"
    
    cdsl_element = "cdsl"
    cdsl_type_attribute = "type"
    cdsl_src_attribute = "src"
    cdsl_time_attribute = "timestamp"
    
    default_expand_string=".cdsl"
    
    repositories_element="repositories"
    repository_element="repository"
    repository_resource_attribute="resource"
    repository_path_attribute="path"

    #definde defaultvalues
    cdsltree_default = ".cluster/cdsl"
    cdslsharedtree_default = ".cluster/shared"
    cdsllink_default = ".cdsl.local"
    defaultdir_default = "default"
    maxnodeidnum_default = "0"
    usenodeids_default = str(True)
    default_resources=[ ".cdsl_inventory.xml", "var/lib/cdsl/cdsl_inventory.xml" ]
    
    nodes_element = "nodes"
    noderef_element = "noderef"
    noderef_ref_attribute = "ref"
    
    #define needed pathes
    cdsls_path = "/" + cdsls_element
    cdsl_path = cdsls_path + "/" + cdsl_element

    EXPANSION_PARAMETER="cdsl_expansion"
    
    def __init__(self, **keys):
        """
        Constructs a new comoonicsCdslRepository from given resource. Creates 
        a list of cdsls from resource to provide an easy access to them.
        @param resource: path to resource, should be created if it does not already exist
        @type  resource: L{string}
        @param dtd: path to dtd used with resource (Default: None)
        @type  dtd: L{string}
        @param validate: set to false to skip validation of resource (Default: True)
        @type  validate: L{Boolean}
        @param path|mountpoint: the path or mountpoint this repository belongs to
        @type  path|mountpoint: L{String}
        @param root: the root|chroot this repository is relative to
        @type  root: L{String}
        @param parent: the parent repository if any
        @type  parent: L{comoonics.cdsl.ComCdslRepository.CdslRepository}
        @param cdsltree: the cdsltree where hostdependent files should be stored. Default: .cluster/cdsl
        @type  cdsltree: L{String}
        @param cdsltreeshared: the cdsltree where reshared files should be stored. Default: .cluster/shared
        @type  cdsltreeshared: L{String}
        @param cdsllink: Where should the link to the hostdependent path be related to. Default .cdsl.local
        @type  cdsllink: L{String}
        @param maxnodeidnum: You might want to overwrite the the max nodeids. Default is to query the underlying cluster.
        @type  maxnodeidnum: L{Integer}
        @param usenodeids: Flag that either uses nodenames or nodeids. Default: True which means use nodeids
        @type  usenodeids: L{Boolean} 
        @param defaultdir: Directory where the default path should be stored. Default: default
        @type  defaultdir: L{String}
        @param nodeprefix: Should there be a string prefixed to every node directory? Default: ""
        @type  nodeprefix: L{String}
        @param expandstring: How should reshared or rehostdeps be suffixed. Default: ".cdsl"
        @type  expandstring: L{String}
        @param nocreate: Not create a repository if it does not exist but fail with an exception.
        @type  nocreate: L{Boolean}
        
        """
        self.logger = ComLog.getLogger("comoonics.cdsl.ComCdsl.ComoonicsCdslRepository")
        self.cdsls=dict()
        self.repositories=dict()
        self.parent=None
        self.dtd=None
        self.resourcehandle=None
        self.resourcehandlelock=0
        if not keys:
            raise TypeError("comoonics.cdsl.ComCdslRepository.ComoonicsCDSLRepository can only be instanciated with keywords not otherwise.")
        self.root = keys.get("root", "/")
                           
        self.workingdir=os.path.join(self.root, stripleadingsep(keys.get("mountpoint", "")))
        if not os.path.exists(self.workingdir):
            raise IOError(2, "Mount point %s does not exist." %self.workingdir)
#        self.workingdir.pushd()
        path=Path()
        path.pushd(self.workingdir)
        resource=None
        try:
            resource=keys.get("resource", ComoonicsCdslRepository.guessresource())
            if resource==None:
                resource=ComoonicsCdslRepository.guessresource()
            open(resource)
        except IOError:
            if keys.get("nocreate", False):
                raise
            elif resource == None:
                resource=self.default_resources[0]
        self.log.debug("CdslRepository: resource %s" %resource)
        keys["resource"]=resource
        # Change to path in order to find resource (resource is read relatively from parentclass. So we need to 
        # change to workingdir
        super(ComoonicsCdslRepository,self).__init__(**keys)
        path.popd()
        
        if self.getVersion() != self.version:
            raise CdslVersionException("""
Wrong version of cdsl repository %s. 
Version must be %s but is %s. 
Please first migrate to appropriate version.
For this use com-mkcdslinfrastructur --migrate""" %(os.path.join(self.workingdir, self.resource), self.getVersion(), self.version))
        self.setMountpoint(stripleadingsep(keys.get("mountpoint", "")))
        self.writeresource(False)

    def __str__(self):
        buf=super(ComoonicsCdslRepository, self).__str__()
        buf=buf[:-1]+", root: %s, mountpoint: %s)" %(self.root, self.getMountpoint())
        return buf

    def _updateFromElement(self, element, document):
        self._readCdslsElement(element, True)

    def getWriteResourceName(self):
        return os.path.join(os.path.dirname(self.resource), os.path.basename(self.resource)+".tmp")

    def lockresourceRO(self):
        self.lockresource()
        
    def lockresourceRW(self):
        if os.path.exists(os.path.join(self.workingdir, self.resource)):
            self.lockresource("r+")
        else:
            self.lockresource("w+")

    def lockresource(self, mode="r"):
        if mode == "r":
            lockmode=fcntl.LOCK_SH
        else:
            lockmode=fcntl.LOCK_EX
        if not self.resourcehandle:
            self.resourcehandle = file(os.path.join(self.workingdir, self.resource), mode)
        fcntl.lockf(self.resourcehandle,lockmode)
        self.resourcehandlelock=lockmode

    def unlockresource(self):
        if self.resourcehandle:
            fcntl.lockf(self.resourcehandle,fcntl.LOCK_UN)
            self.resourcelock=0
            self.resourcehandle.close()
            self.resourcehandle = None

    def refresh(self, nolock=True):
        if not nolock:
            self.lockresourceRO()
        cwd=Path()
        cwd.pushd(self.workingdir)
        self._parseresourceFP(True)
        self._updateFromElement(self.getElement(), self.getDocument())
        if not nolock:
            self.unlockresource()
        cwd.popd()
        
    def _parseresourceFP(self, nolock=True):
        from xml.dom.ext.reader import Sax2
        if not nolock:
            self.lockresourceRO()
            _resourcehandle=self.resourcehandle
        else:
            _resourcehandle = file(os.path.join(self.workingdir, self.resource))
            
        _resourcehandle.seek(0)
        reader = Sax2.Reader(self.validate)
        self.setDocument(reader.fromStream(_resourcehandle))
        element=self.getDocument().documentElement
        self.setElement(element)
        if not nolock:
            self.unlockresource()
        else:
            _resourcehandle.close()

    def writeresource(self, nolock=True):
        from xml.dom.ext import PrettyPrint
        import shutil
        log.debug("ComoonicsCdslRepository writing resource %s/%s" %(self.workingdir, self.resource))
        if not nolock:
            self.lockresourceRW()
        wresourcehandle = file(os.path.join(self.workingdir, self.getWriteResourceName()), "w+")
        PrettyPrint(self.getDocument().documentElement, wresourcehandle)
        wresourcehandle.close()
        shutil.copy(os.path.join(self.workingdir, self.getWriteResourceName()), os.path.join(self.workingdir, self.resource))
        os.remove(os.path.join(self.workingdir, self.getWriteResourceName()))
        if not nolock:
            self.unlockresource()

    def _createEmptyDocumentStructure(self, **keys):
        #create xml and include path to dtd
        try:
            implementation = xml.dom.getDOMImplementation("4DOM")
        except:
            implementation = xml.dom.getDOMImplementation()
        self.dtd=keys.get("dtd", None)
        doct=None
        if self.dtd!=None and os.path.exists(self.dtd):
            doct=implementation.createDocumentType(self.cdsls_element,None,os.path.abspath(self.dtd))
        #create xml without specifying dtd
        doc = implementation.createDocument(None,self.cdsls_element,doct)
        topelement=doc.documentElement
        topelement.setAttribute(self.cdsls_version_attribute,self.version)

        topelement.setAttribute(self.cdsls_tree_attribute, stripleadingsep(keys.get("cdsltree", self.getTreePath())))
        topelement.setAttribute(self.cdsls_sharedtree_attribute, stripleadingsep(keys.get("cdsltreeshared", self.getSharedTreepath())))
        topelement.setAttribute(self.cdsls_link_attribute, stripleadingsep(keys.get("cdsllink", self.getLinkPath())))
        topelement.setAttribute(self.cdsls_maxnodeidnum_attribute, keys.get(self.cdsls_maxnodeidnum_attribute, self.getMaxnodeidnum()))
        topelement.setAttribute(self.cdsls_usenodeids_attribute, keys.get("usenodeids", self.getUseNodeids()))
        topelement.setAttribute(self.cdsls_mountpoint_attribute, stripleadingsep(keys.get(self.cdsls_mountpoint_attribute, self.getMountpoint())))
        topelement.setAttribute(self.cdsls_defaultdir_attribute, stripleadingsep(keys.get(self.cdsls_defaultdir_attribute, self.getDefaultDir())))
        topelement.setAttribute(self.cdsls_nodeprefix_attribute, keys.get(self.cdsls_nodeprefix_attribute, self.getNodePrefix()))
        topelement.setAttribute(self.cdsls_expand_string_attribute, keys.get(self.cdsls_expand_string_attribute, self.getExpandString()))
        
        repositorieselement=doc.createElement(self.repositories_element)
        topelement.appendChild(repositorieselement)
        
        return doc
        
    def _readCdslsElement(self, element, ignoreerrors=False):
        import xml.dom
        self.cdsls=dict()
        self.repositories=dict()
        child=element.firstChild
        while child:
            if child.nodeType == xml.dom.Node.ELEMENT_NODE and child.tagName == self.cdsl_element:
                self._readCdslElement(child, ignoreerrors)
            elif child.nodeType == xml.dom.Node.ELEMENT_NODE and child.tagName == self.repositories_element:
                self._readRepositoriesElement(child, ignoreerrors)
                    
            child=child.nextSibling
            
    def _readCdslElement(self, element, ignoreerrors=False):
        from ComCdsl import Cdsl
        _src = dirtrim(element.getAttribute(self.cdsl_src_attribute))
        _type = element.getAttribute(self.cdsl_type_attribute)
        _timestamp = element.getAttribute(self.cdsl_time_attribute)
            
        #get nodes from cdsl-inventoryfile
        nodes = []
        child = element.firstChild
        while child:
            if child.nodeType == xml.dom.Node.ELEMENT_NODE and child.tagName == self.nodes_element:
                nodes=self._readNodesElement(child, ignoreerrors)
            child=child.nextSibling
            
        self.cdsls[_src]=Cdsl(_src, _type, self, nodes=nodes,timestamp=_timestamp, ignoreerrors=ignoreerrors)

    def _readNodesElement(self, element, ignoreerrors=False):
        child = element.firstChild
        nodes = []
        while child:
            if child.nodeType == xml.dom.Node.ELEMENT_NODE and child.tagName == self.noderef_element:
                useNodeids = self.getUseNodeids()
                nodePrefix = self.getNodePrefix()
                if useNodeids == "True" and (not nodePrefix or nodePrefix == "" or nodePrefix == "False"):
                    nodes.append(child.getAttribute(self.noderef_ref_attribute).replace("id_",""))
                else:
                    nodes.append(child.getAttribute(self.noderef_ref_attribute))
            child=child.nextSibling
        return nodes

    def _readRepositoriesElement(self, element, ignoreerrors=False):
        child = element.firstChild
        while child:
            if child.nodeType == xml.dom.Node.ELEMENT_NODE and child.tagName == self.repository_element:
                path=child.getAttribute("path")
                if child.hasAttribute(self.repository_resource_attribute):
                    resource=child.getAttribute(self.repository_resource_attribute)
                else:
                    resource=self.default_resources[0]
                self.repositories[path]=ComoonicsCdslRepository(resource=resource, mountpoint=path, root=os.path.join(self.root, self.getMountpoint()))
                
            child = child.nextSibling

    def stripsrc(self, _src):
#        cdslRepository.workingdir.pushd()
        from comoonics.cdsl import strippath
        if not _src.startswith(os.sep):
            _src=os.path.join(os.getcwd(), _src)
        cwd=Path()
        cwd.pushd(self.workingdir)
        if os.path.exists(_src):
            _src=os.path.realpath(_src)
        src=_src
        src=stripleadingsep(strippath(strippath(src, self.root), self.getMountpoint()))
        src=stripleadingsep(strippath(src, self.getLinkPath()))
        src=stripleadingsep(strippath(src, self.getSharedTreepath()))
        if src.startswith(self.getTreePath()):
            src=stripleadingsep(strippath(src, self.getTreePath()))
            src=os.sep.join(src.split(os.sep)[1:])
        src=self.unexpand(src)
        self.logger.debug("cdsl stripped %s to %s" %(_src, src))
        cwd.popd()
        return src
                
    def guessresource():
        """
        Tries to guess the config file for the given cdsl filesystem.
        First it tries to find /<root>/<mountpoint>/.cdsl_inventory.xml if it does not find it it tries
        /<root>/<mountpoint>/var/lib/cdsl_inventory.xml.
        """
        for _resource in ComoonicsCdslRepository.default_resources:
            guess=_resource
            if os.path.exists(guess):
                return guess
        raise IOError(2, "No default repository resource found.")
    guessresource=staticmethod(guessresource)
    
    def realpath(self, src):
        """
        Returns the realpath of a src. What it does it joins root, mountpath and src and gets the realpath
        from it
        @param src: the path to resolve to a realpath
        @type src: string
        @return: the resolved path of this src 
        @rtype: string
        """
        if self.getMountpoint().startswith(os.sep):
            _path=os.path.join(self.root, self.getMountpoint()[1:], src)
        else:
            _path=os.path.join(self.root, self.getMountpoint(), src)
        return os.path.realpath(_path)
    
    def getRepositories(self):
        """
        Returns a list of sub cdsl repositories usually being implemented by other shared filesystems with cdsls enabled.
        Basically the sub cdsl repositories are represented by repository elements like as follows
        <cdsls>
           ..
           <repositories>
              <repository path=".."/>
              ..
           </repositories>
           ..
        </cdsls>
        """
        return self.repositories
    
    def getRepository(self, path):
        return self.repositories[path]
    
    def addRepository(self, repository, path=None):
        """
        Adds a sub repository for another cdsl environment. Referenced by the given path.
        @param repository: the previously generated repository
        @type  repository: comoonics.cdsl.ComCdslRepository.ComoonicsCdslRepository
        @param path: the path to this repository
        @type  path: string
        """
        self.refresh(False)
        if not path:
            path=repository.getMountpoint()
        self.repositories[path]=repository
        repository.setRoot(os.path.join(self.root, self.getMountpoint()))
        repositorieselement=self.getElement().getElementsByTagName(self.repositories_element)[0]
        repositoryelement = self.getDocument().createElement(self.repository_element)
        repositoryelement.setAttribute(self.repository_path_attribute, path)
        repositoryelement.setAttribute(self.repository_resource_attribute, repository.getResource())
        repository.setParent(self)
        repositorieselement.appendChild(repositoryelement)
        self.lockresourceRW()
        self.writeresource()
        self.unlockresource()

    def removeRepository(self, repositoryorpath):
        """
        Removes a repository already child of this repository.
        @param repositoryorpath: either the repository or the path to the repository to be deleted.
        @type  repositoryorpath: L{String} or L{comooncs.cdsl.ComCdsl.ComoonicsCdslRepository}
        """
        self.refresh(False)
        self._removeRepository(repositoryorpath)
        
    def _removeRepository(self, repositoryorpath):
        if isinstance(repositoryorpath, basestring):
            repository=self.getRepository(repositoryorpath)
        else:
            repository=repositoryorpath
        path=repository.getMountpoint()
        if self.repositories.has_key(path):
            del self.repositories[path]
            child=self.getElement().firstChild
            while child:
                if child.nodeType == xml.dom.Node.ELEMENT_NODE and child.tagName == self.repositories_element:
                    child2 = child.firstChild
                    while child2:
                        if child2.nodeType == xml.dom.Node.ELEMENT_NODE and child2.tagName == self.repository_element and child2.getAttribute(self.repository_path_attribute) == path:
                            child.removeChild(child2)
                        child2=child2.nextSibling 
                child=child.nextSibling
                    
        self.lockresourceRW()
        self.writeresource()
        self.unlockresource()

    def setParent(self, parent):
        self.parent=parent
        
    def getParent(self):
        return self.parent

    def getRepositoryForCdsl(self, src):
        """
        Returns the cdslRepository this cdsl src belongs to.
        @param src: the path to the cdsl
        @type: L{String}
        @return: the parent repository for this cdsl
        @rtype: L{comoonics.cdsl.ComCdslRepository.ComoonicsCdslRepository}
        """
        from comoonics.cdsl import strippath
        src=stripleadingsep(strippath(strippath(stripleadingsep(src), self.root), self.getMountpoint()))
        for mountpoint in self.getRepositories().keys():
            if src.startswith(mountpoint):
                return self.getRepository(mountpoint).getRepositoryForCdsl(src)
        return self

    def getCdsl(self,src, repository=None):
        """
        Uses given source to return matching cdsl
        @param src: Path of searched cdsl
        @type src: string
        @return: cdsl-object belonging to given path
        @rtype: L{ComoonicsCdsl}
        @raise CdslRepositoryNotFound: if the cdsl could not be found in the repository 
        """
        if not repository:
            repository=self.getRepositoryForCdsl(src)
        src=self.stripsrc(src)
        if repository.cdsls.has_key(src):
            return repository.cdsls[src]
        else:
            path=Path()
            path.pushd(repository.workingdir)
            for cdsl in repository.cdsls.values():
                if cdsl.src == src or (os.path.exists(cdsl.src) and os.path.exists(src) and os.path.samefile(cdsl.src, src)):
                    path.popd()
                    return cdsl
            path.popd()
        raise CdslNotFoundException(src,repository)
        
            
    def commit(self,cdsl):
        """
        Adds or modifies cdsl entry in inventoryfile (depending on existing entry with the same src attribute like the given cdsl)
        @param cdsl: cdsl to commit
        @type cdsl: L{ComoonicsCdsl}
        """
        #Open and lock XML-file and return DOM
        path=Path()
        path.pushd(self.workingdir)
        self.refresh(False)
        self.lockresourceRW()
        if self.exists(cdsl):
            log.debug("cdsl exists")
            log.debug("removing cdsl %s.." % cdsl.src)
            #locate existing node entry
            oldnode = self.cdsls[cdsl.src].getElement()
            self.getElement().removeChild(oldnode)

        #modify existing cdsl-entry
        if cdsl.getDocument().isSameNode(self.getDocument()):
            _node = cdsl.getElement()         
        else:
            _node=self.getDocument().importNode(cdsl.getElement(), True)
            cdsl.setElement(_node)
            cdsl.setDocument(self.getDocument())
        self.getElement().appendChild(_node)
        
        #modify cdsls of cdslRepository instance
        self.cdsls[cdsl.src] = cdsl
        
        self.writeresource()
        self.unlockresource()
        path.popd()
        return cdsl
    
    def delete(self,cdsl):
        """
        Deletes cdsl entry in inventoryfile if existing
        @param cdsl: cdsl to delete
        @type cdsl: L{ComoonicsCdsl}
        """
        _deleted=None
        self.refresh(False)
        cwd=Path()
        cwd.pushd()
        if self.exists(cdsl):
            # delete cdsl-entry if existing"""
            #Open and lock XML-file and return DOM
            self.lockresourceRW()
            element=self.cdsls[cdsl.src].getElement()
            self.getElement().removeChild(element)
            self.writeresource(True)
            
            if self.cdsls.has_key(cdsl.src):
                _deleted=cdsl
                del self.cdsls[_deleted.src]        
        else:
            # raise exeption if cdsl to delete is not existing"""
            raise CdslNotFoundException(cdsl, self)
        return _deleted

    def _getNodes(self, clusterinfo=None):
        nodes = []
        if clusterinfo:
            if ((self.getUseNodeids() == "True") and (self.getMaxnodeidnum() == "0")): #maxnodidnum is not set but use_nodeid is set
                nodes = clusterinfo.getNodeIdentifiers("id")
            elif (self.getMaxnodeidnum() == "0"): #maxnodidnum is set but use_nodeid is not set
                nodes = clusterinfo.getNodeIdentifiers("name")           
            else: #use_nodeids and maxnodeidnum are set
                for i in range(1,int(self.getMaxnodeidnum())+1):
                    nodes.append(str(i))
            
            #value of node_prefix matters only if use_nodeids is set
            #if node_prefix in inventoryfile is "", then getAttr gets "True" instead
            if ((self.getNodePrefix() != "True") and (self.getUseNodeids() == "True")):
                for i in range(len(nodes)):
                    nodes[i] = str(self.getNodePrefix()) + str(nodes[i])
            elif ((self.getNodePrefix() != "True") and (self.getNodePrefix() != "")) and not (self.getUseNodeids() == "True"):
                raise TypeError("Prefix could only be used together with use_nodeids.")
        elif self.getMaxnodeidnum() != "" and int(self.getMaxnodeidnum()) > 0:
            for i in range(1,int(self.getMaxnodeidnum())+1):
                nodes.append(str(i))
                
        return nodes

    def buildInfrastructure(self,clusterinfo=None, recursive=True):
        """
        Creates cdsl infrastructure, includes creating of needed directories and symbolic links 
        and keep in mind the exposure with a maybe given default directory (copy to every node, 
        link)
        @param clusterinfo: Clusterinfo with needed attributes
        @type clusterinfo: L{ComoonicsClusterInfo}
        @param recursive:  If true also build dependent repos. (Default: True)
        @type  recursive:  L{Boolean} 
        """
        nodes=self._getNodes(clusterinfo)
        if not nodes or len(nodes) == 0:
            raise TypeError("Either specify a clusterinfo or maxnodeidnums need to be set in order to determine the nodeids need to build the cdsl infrastructure.")
        
        path=Path()
        path.pushd(self.workingdir)
        if not os.path.exists(self.resource):
            self.lockresourceRW()
            self.writeresource()
            self.unlockresource()
            
        cdslDefaultdir = os.path.join(self.getTreePath(),self.getDefaultDir())
        if not os.path.exists(cdslDefaultdir):
            log.debug("Creating default_dir " + cdslDefaultdir)
            #os.makedirs(cdslDefaultdir)
            ComSystem.execMethod(os.makedirs,cdslDefaultdir)
                    
        #Create basedirectory for every node
        for node in nodes:
            nodepath=os.path.join(self.getTreePath(),str(node))
            if not os.path.exists(nodepath):
                log.debug("Creating hostdirectory " + nodepath +"..")
                ComSystem.execMethod(os.makedirs,nodepath)
        
        # Create the shared directory
        if not os.path.exists(self.getSharedTreepath()):
            log.debug("Creating shareddir " + self.getSharedTreepath())
            ComSystem.execMethod(os.makedirs, self.getSharedTreepath())
        
        # Create directories root_variable/relpath_variable if not already existing
        if not os.path.exists(self.getLinkPath()):
            log.debug("Creating link directory " + self.getLinkPath())
            ComSystem.execMethod(os.makedirs,self.getLinkPath())
        
        if recursive:
            for repository in self.getRepositories().values():
                repository.buildInfrastructure(clusterinfo, recursive)
        path.popd()

    def removeInfrastructure(self,clusterinfo=None, recursive=True, force=False, withcdsls=True):
        """
        Removes the CDSL Infrastructure belonging to this repository.
        This removes all cdsls which are existing in the repository.
        @param clusterinfo: If given nodeids are queried from this clusterinformation
        @type  clusterinfo: L{comoonics.cluster.ComClusterInfo.ComoonicsClusterInfo}
        @param recursive  : Also remove the infrastructures found in child repositories (default=True).
        @type  recursive  : L{Boolean}
        @param force      : Force every command ignoring errors. Removes everything inside the cdsl environment. Default: False.
        @type  force      : L{Boolean}
        @param withcdsls  : Also remove the cdsls insite the repository. Default: True
        @type  withcdsls  : L{Boolean}
        """
        import shutil
        self.refresh(False)

        nodes=self._getNodes(clusterinfo)
        if not nodes or len(nodes) == 0:
            raise TypeError("Either specify a clusterinfo or maxnodeidnums need to be set in order to determine the nodeids need to build the cdsl infrastructure.")
                        
        if recursive:
            for repository in self.getRepositories().values():
                repository.removeInfrastructure(clusterinfo, recursive, force, withcdsls)
                self._removeRepository(repository)

        wpath=Path()
        wpath.pushd(self.workingdir)
        if withcdsls:
            for cdsl in self.getCdsls():
                if cdsl.exists():
                    cdsl.delete(recursive, force)

        cdslDefaultdir = os.path.join(self.getTreePath(),self.getDefaultDir())
        if os.path.exists(cdslDefaultdir):
            log.debug("Removing default_dir " + cdslDefaultdir)
            if force:
                ComSystem.execMethod(shutil.rmtree, cdslDefaultdir, force)
            else:
                ComSystem.execMethod(os.removedirs, cdslDefaultdir)
                    
        #Create basedirectory for every node
        for node in nodes:
            nodepath=os.path.join(self.getTreePath(),str(node))
            if os.path.exists(nodepath):
                log.debug("Removing nodedir " + nodepath)
                if force:
                    ComSystem.execMethod(shutil.rmtree, nodepath, force)
                else:
                    ComSystem.execMethod(os.removedirs, nodepath)
        
        # Create the shared directory
        if os.path.exists(self.getSharedTreepath()):
            log.debug("Removing shareddir " + self.getSharedTreepath())
            if force:
                ComSystem.execMethod(shutil.rmtree, self.getSharedTreepath(), force)
            else:
                ComSystem.execMethod(os.removedirs, self.getSharedTreepath())
        
        # Create directories root_variable/relpath_variable if not already existing
        if os.path.exists(self.getLinkPath()):
            log.debug("Removing link directory " + self.getLinkPath())
            ComSystem.execMethod(os.removedirs, self.getLinkPath())

        for path in [ self.getTreePath(), self.getSharedTreepath(), self.getLinkPath() ]:
            path=os.path.dirname(path)
            if os.path.dirname(path)!="" and os.path.exists(path):
                ComSystem.execMethod(os.removedirs, path)
                
        if os.path.exists(self.resource):
            ComSystem.execMethod(os.remove, self.resource)
        wpath.popd()

    def _getnearestcdsls(self, path, down=True, clusterinfo=None, onerror=None):
        from comoonics.cdsl import isSubPath
        foundcdsl=None
        for cdsl in self.walkCdsls(clusterinfo, None, onerror):
            if down and isSubPath(path, cdsl.src):
                if not foundcdsl:
                    foundcdsl=cdsl
                elif foundcdsl and isSubPath(cdsl.src, foundcdsl.src):
                    foundcdsl=cdsl
            elif not down and isSubPath(cdsl.src, path):
                if not foundcdsl:
                    foundcdsl=cdsl
                elif foundcdsl and isSubPath(cdsl.src, foundcdsl.src):
                    foundcdsl=cdsl
        return foundcdsl

    def expandCdsl(self, cdsl):
        """
        expand this cdsl if need be. This is the case when this cdsl is nested. The nested path needs to 
        be expanded with subdirs in order to allow a hostdependent cdsl of a shared path.
        Algorithm is roughly as follows:
          We walk through the path of this cdsl from root to leaf.
          For the given subpath get the "nearest" cdsl then walk down parent to parent. If a parent is a
          hostdependent cdsl and a hostdependent cdsl was already found expand its path and follow 
          recursively.
        Examples:
          h                   => l/h                      depth<h>=1
          h/s                 => st/h/s                   depth<h>=1
          h/s/h               => l/h/c.s/h                depth<h>=2   expandcount=1
          h/s/h/s             => st/h/s/c.h/s             depth<h>=2   expandcount=1
          h/s/h/s/h           => l/h/c.s/h/c.s/h          depth<h>=2   expandcount=2
          t/h                 => l/t/h
          t/h/t/s             => st/t/h/t/s
          t/h/t/s/t/h         => l/t/h/t/c.s/t/h
          t/h/t/s/t/h/t/s     => s/t/h/t/s/t/c.h/t/s
          t/h/t/s/t/h/t/s/t/h => l/t/h/t/c.s/t/h/t/c.s/t/h
          ..
        @param _cdsl: the cdsl.
        @type _cdsl: comoonics.cdsl.ComCdsl.Cdsl|string
        @return: returns the expanded path of the cdsl without either cdsltreeShared, cdsllink, ..
        @rtype: string 
        """ 

        from comoonics.cdsl import strippath, guessType
        from comoonics.cdsl.ComCdsl import Cdsl

        # let's get the cdsl
        if isinstance(cdsl, basestring):
            try:
                cdsl=self.getCdsl(cdsl)
            except CdslNotFoundException:
                cdsl=Cdsl(cdsl, guessType(cdsl, self), self, cdsl.clusterinfo)
                if cdsl and cdsl.exists():
                    log.warning("The cdsl %s seems not to be in the repository. Please rebuild database.")
                    raise
        
        # store path
        tmppath=cdsl.src

        # Let's walk to the root and expand
        parent=cdsl.getParent()
        while parent != None:
            if parent != None and parent.getParent() != None and cdsl.type != parent.type:
                (_phead, _ptail)=os.path.split(parent.src)
                tmppath=os.path.join(_phead, "%s.%s" %(self.getExpandString(), stripleadingsep(_ptail)), stripleadingsep(strippath(tmppath, parent.src)))
            parent=parent.getParent()
        
        return tmppath
    
    def unexpand(self, path):
        """
        unexpands the given path.
        @param path: the path that should be cleared of all cdsl expansions
        @type path: L{String}
        @return: returns the unexpanded path
        @rtype: L{String}
        """
        from comoonics.cdsl import strippath
        subpath=path
        subpath=stripleadingsep(strippath(strippath(subpath, self.root), self.getMountpoint()))
        subpath=stripleadingsep(strippath(subpath, self.getLinkPath()))
        subpath=stripleadingsep(strippath(subpath, self.getSharedTreepath()))
        if path.startswith(self.getTreePath()):
            path=stripleadingsep(strippath(path, self.getTreePath()))
            path=os.sep.join(path.split(os.sep)[1:])
#        if clusterinfo:
#            nodes=clusterinfo.getNodeIdentifiers()
#        else:
#            nodes=range(1, int(self.getMaxnodeidnum())+1)
#        for node in nodes:
#            subpath=stripleadingsep(strippath(subpath, os.path.join(self.getTreePath(), str(node))))
        newsubpath=list()
        prepath=os.sep.join(path.split(os.sep)[:path.count(os.sep)-subpath.count(os.sep)])
        head, tail=os.path.split(subpath)
        while tail and tail != "":
            if tail.startswith(self.getExpandString()+"."):
                tail=tail[len(self.getExpandString())+1:]
            newsubpath.append(tail)
            head, tail=os.path.split(head)
        newsubpath.reverse()
        return dirtrim(os.path.join(prepath, os.sep.join(newsubpath)))
    
    def isExpandedDir(self, _expanded):
        """
        Returns True if this path is and expanded path
        """
        return _expanded.find(self.getExpandString()) >= 0 # and self.hasCdsl(_expanded.replace(self.getExpandString(), ""))

    def setTreePath(self, value):
        self.setAttribute(self.cdsls_tree_attribute, value)
    
    def getTreePath(self, realpath=False):
        """
        @rtype: string
        """
        if not realpath:
            return self.getAttribute(self.cdsls_tree_attribute, self.cdsltree_default)
        else:
            return self.realpath(self.getTreePath(False))

    def setSharedTreepath(self, value):
        self.setAttribute(self.cdsls_sharedtree_attribute, value)
    
    def getSharedTreepath(self):
        """
        @rtype: string
        """
        return self.getAttribute(self.cdsls_sharedtree_attribute, self.cdslsharedtree_default)

    def setLinkPath(self, value):
        self.setAttribute(self.cdsls_link_attribute, value)
    
    def getLinkPath(self):
        """
        @rtype: string
        """
        return self.getAttribute(self.cdsls_link_attribute, self.cdsllink_default)

    def setMountpoint(self, value):
        self.setAttribute(self.cdsls_mountpoint_attribute, value)
    
    def getMountpoint(self):
        """
        @rtype: string
        """
        return self.getAttribute(self.cdsls_mountpoint_attribute, "")

    def setDefaultDir(self, value):
        self.setAttribute(self.cdsls_defaultdir_attribute, value)
    
    def getDefaultDir(self):
        """
        @rtype: string
        """
        return self.getAttribute(self.cdsls_defaultdir_attribute, self.defaultdir_default)
    
    def setMaxnodeidnum(self, value):
        self.setAttribute(self.cdsls_maxnodeidnum_attribute, value)
    
    def getMaxnodeidnum(self):
        """
        @rtype: string
        """
        return self.getAttribute(self.cdsls_maxnodeidnum_attribute, self.maxnodeidnum_default)
 
    def setNodePrefix(self, value):
        self.setAttribute(self.cdsls_nodeprefix_attribute, value)
    
    def getNodePrefix(self):
        """
        @rtype: string
        """
        return self.getAttribute(self.cdsls_nodeprefix_attribute, "")
    
    def setUseNodeids(self, value):
        self.setAttribute(self.cdsls_usenodeids_attribute, value)
    
    def getUseNodeids(self):
        """
        @rtype: string
        """
        return self.getAttribute(self.cdsls_usenodeids_attribute, self.usenodeids_default)
    
    def setExpandString(self, value):
        self.setAttribute(self.cdsls_expand_string_attribute, value)
    
    def getExpandString(self):
        """
        @rtype: string
        """
        return self.getAttribute(self.cdsls_expand_string_attribute, self.default_expand_string)
    
    def setVersion(self, value):
        self.setAttribute(self.cdsls_version_attribute, value)
    
    def getVersion(self):
        """
        @rtype: string
        """
        return self.getAttribute(self.cdsls_version_attribute, "")
    
    def addNode(self,node,addtotree=True, recursive=True):
        """
        Adds node to all defined cdsls in inventoryfile (does not consider directories of cdsl in filesystem) 
        @param node: ID of node which should be added to cdsls, needed type of ID (nodeID, name or prefix & ID) 
        depends on values of used inventoryfile
        @type node: String
        @param addtotree: If true, add new node to filesystem, uses copy of default-directory for cdsl-directorys. (Default: True)
        @type addtotree: Boolean
        @param recursive: Will also change the child repositories.
        @type  recursive: L{Boolean}
        """
        #prepare filesystem for new node
        if addtotree == True:
            root = self.root
            mountpoint = dirtrim(self.getMountpoint())
            cdsltree = dirtrim(self.getTreePath())
        
            _rootMountpoint = os.path.normpath(os.path.join(root,mountpoint))
            if not os.path.exists(_rootMountpoint):
                raise IOError(2, "Mount point " + _rootMountpoint + " does not exist.")
            
            cdslDefaultdir = os.path.join(_rootMountpoint, cdsltree, self.getDefaultDir())
            nodedir = os.path.join(_rootMountpoint, cdsltree, node)
            if not os.path.exists(cdslDefaultdir):
                raise IOError(2, "Required default directory " + cdslDefaultdir + " does not exist")
            
            #create needed directories if they are not existing
            if not os.path.exists(os.path.dirname(nodedir)):
                ComSystem.execMethod(os.makedirs,os.path.dirname(nodedir))
                
            if os.path.exists(nodedir):
                raise IOError(2, "Node destination directory %s already exists." %nodedir)
            #copy content of defaultnode-directory to newnode-directory
            ComSystem.execLocalStatusOutput("cp -a " + cdslDefaultdir + " " + nodedir)
        
        #Open and lock XML-file and return DOM
        self.lockresourceRW()
        self.refresh()
        if recursive:
            for repository in self.getRepositories():
                repository.addNode(node, addtotree, recursive)
        
        #find noderef and remove element
        #_nodes = xpath.Evaluate("/cdsls/cdsl/nodes[noderef/@ref != '%s']" %(node),doc)
        for cdsl in self.cdsls.values():
            cdsl.addNode(node)
        
        self.writeresource()
        self.unlockresource()
    
    def removeNode(self,node,removefromtree=True, recursive=True):
        """
        Remove node to all defined cdsls in inventoryfile (does not consider directories of cdsl in filesystem)
        @param node: ID of node which should be added to cdsls, needed type of ID (nodeID, name or prefix & ID) 
        depends on values of used inventoryfile
        @type node: string
        @param removefromtree: If true, remove node from filesystem. (Default: True)
        @type removefromtree: Boolean
        @param recursive: Will also change the child repositories.
        @type  recursive: L{Boolean}
        """
        import shutil
        #Open and lock XML-file and return DOM
        self.lockresourceRW()
        self.refresh()
        
        for cdsl in self.cdsls.values():
            cdsl.removeNode(node)
            
        self.writeresource()
        self.unlockresource()
        if removefromtree == True:
            root = self.root
            mountpoint = dirtrim(self.getMountpoint())
            cdsltree = dirtrim(self.getTreePath())
            _rootMountpoint = os.path.normpath(os.path.join(root, mountpoint))
            if not os.path.exists(_rootMountpoint):
                raise IOError(2, "Mount point " + _rootMountpoint + " does not exist.")
            
            nodedir = os.path.join(_rootMountpoint, cdsltree, node)
                
            if not os.path.exists(nodedir):
                raise IOError(2, "Node destination directory %s does not  exists." %nodedir)
            #copy content of defaultnode-directory to newnode-directory
            ComSystem.execMethod(shutil.rmtree, nodedir)
        
    def update(self,src,clusterInfo,onlyvalidate=True):
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
        from comoonics.cdsl import strippath
        
        _deleted=None
        _added=None

        _cdsl=None
        if isinstance(src, basestring):
            try:
                _src = strippath(src, self.getLinkPath())
                _cdsl = self.getCdsl(_src)
            except CdslNotFoundException, e:
                _added=self.guessonerror(e.value, clusterInfo)
        else:
            _cdsl=src

        if _cdsl and not self.hasCdsl(_cdsl.src):
            _added=src
        elif _cdsl and not _cdsl.exists():
            _deleted=src 
     
        if not onlyvalidate and _added:
            self.log.debug("update: %s does not exist in repository adding it." %_added)
            ComSystem.execMethod(self.commit, _added)
        if not onlyvalidate and _deleted:
            self.log.debug("update: %s does not exist on filesystem removing it." %_deleted)
            ComSystem.execMethod(self.delete, _deleted)
        return _added, _deleted

    def guessonerror(self, src, clusterInfo):
        from comoonics.cdsl import guessType
        from comoonics.cdsl.ComCdsl import Cdsl
        
        _added=None
        _deleted=None
        _type=guessType(src, self, False)
        if _type != Cdsl.HOSTDEPENDENT_TYPE and _type != Cdsl.SHARED_TYPE:
            self.logger.debug("File %s seems to be no cdsl. Skipping it." %src)
        
            #create hostdependent and shared cdsl-object and test if one of these is existing
#            _cdslHostdependent = Cdsl(src, Cdsl.HOSTDEPENDENT_TYPE, self, clusterInfo)
#            _cdslShared = Cdsl(src, Cdsl.SHARED_TYPE, self, clusterInfo)
#                       
#            if _cdslShared.exists():
#                self.log.debug("update: would add shared CDSl with source " + src + " to inventoryfile.")
#                _added=_cdslShared
#            elif _cdslHostdependent.exists():
#                self.log.debug("update: would add hostdependent CDSL with source " + src + " to inventoryfile.")
#                _added=_cdslHostdependent
#            else:
#                log.debug("update: CDSL with source " + src + " does neither exist in inventoryfile nor in filesystem, no need to update inventoryfile")
#                raise CdslNotFoundException(src, self)
        else:
            _added=Cdsl(src, _type, self, clusterInfo)
        
        return _added

    def setRoot(self,root):
        """
        Set chroot of cdsl, needed e.g. when a cdsl is picked out from inventoryfile
        and you work in an environment which is prepared for chroot
        @param root: chroot-path to set
        @type root: string
        """
        self.root = root

###############
# $Log: ComCdslRepository.py,v $
# Revision 1.23  2010-05-28 09:40:15  marc
# - ComoonicsCdslRepository
#   - refresh
#     - refresh in workingdir as cdsls are relative
#   - stripsrc
#     - moved here from Cdsl
#     - removed dep for clusterinfo
#   - getCdsl
#     - uses stripsrc to strip src instead of incomplete
#   - delete
#     - delete in workingdir as cdsls are relative
#   - unexpand
#     - removed dep to clusterinfo
#
# Revision 1.22  2010/05/27 08:43:25  marc
# - adapted to new upstream Path API
# - CdslRepository:
#   - __init__: detect 0 size inventoryfile
# - ComoonicsCdslRepository
#   - added defaultdir_default
#   - attribute workingdir is a string not a Path
#   - __init__: added parameter nocreate to not create repository if it does not exist but raise Exception
#   - getWriteResourceName: added method that returns the name of the temporary inventory file to be written to
#   - lockresourceRW: not truncate existing inventory files but open in write mode (r+ and w+)
#   - lockresource: some more errors to be detected
#   - _parseresourceFP: if nolock create a temporary handle but not use self.resourcehandle
#   - writeresource: first write to getWriteResourceName then move it to old repository
#   - _createEmptyDocumentStructure: accept given predefined parameters
#   - commit: exchanged replaceChild to removeChild and all appendChild (better readable)
#   - guessonerror: simplified perhaps obsolete
#