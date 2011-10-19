"""

Comoonics cdsl package

Provides modules to manage cdsls on filesystem and in inventoryfile. Offers 
functionality to create, manipulate and check cdsls on filesystem/in inventoryfile. 
Discovers needed cdsl type by looking after type of used cluster configuration.
"""
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

#Files
def cmpbysubdirs(path1, path2):
    import os
    return str(path1).count(os.sep) - str(path2).count(os.sep)

def stripleadingsep(_path):
    """
    Normalizes a given path as described in os.path.normpath and strips all leading os.sep if existant.
    @param _path: the path to be stripped 
    @type _path: string
    @return: the normalized and stripped path as described
    @rtype : string 
    """
    import os.path
    if not _path or _path=="":
        return _path
    _tmp=os.path.normpath(_path)
    if _tmp[0]==os.sep:
        _tmp=_tmp[1:]
    return _tmp

def ismount(path):
    """
    Uses os.path.ismount (see L{os.path} for details) and wrap it to detect 
    bind mounts.
    """
    from comoonics import ComSystem
    import os.path
    if os.path.ismount(path):
        return True
    _tmp1 = ComSystem.execLocalStatusOutput("mount")[1]
    if not _tmp1:
        return False
    _tmp2 = _tmp1.split("\n")
    for line in _tmp2:
        if os.path.realpath(line.split()[2]) == os.path.realpath(path):
            return True
    return False


def guessType(_cdslpath, _cdslrepository, _exists=True):
    """
    Returns the guessed type of this cdsl.
    First it searches the repository of the last cdsl in path and takes the opposite. If it does not
    find the cdsl in the repo it tries to guess from the realpath of the cdslpath if it is 
    either a hostdependent or shared cdsl path and then takes the opposite. 
    Those paths are got from the cdslrepository.
    @param _cdslpath: the path to the cdsl
    @type _cdslpath: string
    @param _cdslrepository: the repository to question for the cdsl environment
    @type _cdslrepository: _cdslrepository: comoonics.cdsl.ComCdslRepository.ComoonicsCdslRepository   
    @return: "hostdependent"|"shared"|"unknown"
    @rtype: string
    """
    import os.path
    from ComCdsl import Cdsl
    from ComCdslRepository import CdslNotFoundException
    _path=os.path.join(_cdslrepository.workingdir, dirtrim(_cdslpath))
#    if _path.find(os.sep) > 0:
#        _path=os.path.dirname(_path)
#        while _path:
#            _path, _tail=os.path.split(_path)
#            try:
#                _cdsl=_cdslrepository.getCdsl(_path)
#                if _cdsl.isHostdependent() and isSharedPath(os.path.realpath(_cdslpath), _cdslrepository, _exists):
#                    return Cdsl.SHARED_TYPE
#                elif _cdsl.isShared() and isHostdependentPath(os.path.realpath(_path), _cdslrepository, _exists):
#                    return Cdsl.HOSTDEPENDENT_TYPE
#            except CdslNotFoundException:
#                continue

    if os.path.islink(_path) and isHostdependentPath(os.readlink(_path), _cdslrepository, _exists):
        return Cdsl.HOSTDEPENDENT_TYPE
    elif os.path.islink(_path) and isSharedPath(os.readlink(_path), _cdslrepository, _exists):
        return Cdsl.SHARED_TYPE
    else:
        return Cdsl.UNKNOWN_TYPE

def subpathsto(to, fromwhere):
    """
    This method will return all subpaths from the frompath fromwhere to the path to. 
    """
    import os.path
    _from=fromwhere
    common=commonpath(_from, to)
    paths=[]
    if common != "" or to=="":
        _from, _head=os.path.split(strippath(_from, common))
        if not _from or _from == "":
            paths.append(os.path.join(common, _head))
        else:
            paths.append(os.path.join(common, _from, _head))
            paths.extend(subpathsto(to, os.path.join(common, _from)))
    return paths
            

def strippath(_path, _headpath, _fullpath=True):
    """
    Strips the headpath from the head of given path and returns the "relative" resultpath. If it does not
    match the _path is returned without changes.
    @param _path: the path to be stripped from
    @type _path: string
    @param _headpath: the path used as strip path.
    @type _headpath: string
    @param _fullpath: only check if the fullpath is given. This is default.
    @type _fullpath: L{Boolean}
    @return: the stripped path or the whole path if it does not match
    @rtype: string   
    """
    import os.path
    if _fullpath and not _headpath.endswith(os.sep):
        _headpath=_headpath+os.sep
    if os.path.normpath(_path[0:len(_headpath)])==os.path.normpath(_headpath):
        return dirtrim(_path[len(_headpath):])
    else:
        return dirtrim(_path)

def isCDSLPath(path, cdslRepository, root="/"):
    """
    This method checks if the given path is already a cdsl path.
    @param path: the path (also relative) to the file to be checked
    @type path: string
    @param cdslRepository: the repository to query for settings
    @type cdslRepository: comoonics.cdsl.ComCdslRepository.CdslRepository
    @param root: if this cdsl is relative to a root other then "/" specify it hereby
    @type root: string       
    @return: True if the is already a cdslpath, False otherwise
    @rtype: Boolean
    """
    import os.path
    _tmp=os.path.realpath(path)
    _tmp2=os.path.join(root, cdslRepository.getMountpoint(), cdslRepository.getTreePath())
    _tmp3=os.path.join(root, cdslRepository.getMountpoint(), cdslRepository.getSharedtreePath())
    _tmp4=os.path.join(root, cdslRepository.getMountpoint(), cdslRepository.getLinkPath())
    return os.path.commonprefix([ _tmp, _tmp2 ]) == _tmp2 or \
           os.path.commonprefix([ _tmp, _tmp3 ]) == _tmp3 or \
           os.path.commonprefix([ _tmp, _tmp4 ]) == _tmp4

def isSharedPath(_path, _cdslRepository, _exists=True):
    """
    This method returns True is the given path includes the CdsltreeSharedpath as subdir.
    @param _path: a relative or full path that is not resolved. Just taken as is.
    @type _path: String
    @param _cdslRepository: the repository to query for the CdsltreeSharedpath
    @type _cdslRepository: comoonics.cdsl.ComCDSLRepository.CdslRepository  
    @param _exists: also tests if the path exists. defaults True
    @type _exists: Boolean   
    @return: True is the path has a subdir of the CdsltreeShared
    @rtype: Boolean 
    """
    import os.path
    __exists1=_exists
    __exists2=True
    if _exists:
        _tpath=ltrimDir(_path)
        __exists1=os.path.exists(os.path.join(_cdslRepository.getSharedTreepath(), _tpath))
        __exists2=os.path.exists(_tpath)
    return __exists1 or ( __exists2 and isSubPath(_path, _cdslRepository.getSharedTreepath()))

def isHostdependentPath(_path, _cdslRepository, _exists=True):
    """
    This method returns True is the given path includes the CdsltreeHostdeppath as subdir.
    @param _path: a relative or full path that is not resolved. Just taken as is.
    @type _path: String
    @param _cdslRepository: the repository to query for the CdsltreeHostdependentPath
    @type _cdslRepository: comoonics.cdsl.ComCDSLRepository.CdslRepository    
    @param _exists: also tests if the path exists. defaults True
    @type _exists: Boolean   
    @return: True is the path has a subdir of the CdsltreeShared
    @rtype: Boolean 
    """
    import os.path
    __exists1=_exists
    __exists2=True
    if _exists:
        _tpath=ltrimDir(_path)
        __exists1=os.path.exists(os.path.join(_cdslRepository.getLinkPath(), _tpath))
        __exists2=os.path.exists(_tpath)
    return __exists1 or (__exists2 and (isSubPath(_path, _cdslRepository.getLinkPath()) or isSubPath(_path, _cdslRepository.getTreePath())))

def ltrimDir(_path, _trimdir=".."):
    """
    This method removes all _trimdir subdirs from the beginning of path. 
    Default is all leading ".." are being removed.
    @param _path: the path to be trimmed. Should be a relative path to work
    @type _path: string
    @param _trimdir: the subdir to be removed. Defaults to ".."
    @type _trimdir: string
    @return: the trimmed path
    @rtype: string   
    """
    import os
    import os.path
    if _path.startswith(os.sep):
        return _path
    _retpath=""
    for _subdir in _path.split(os.sep):
        if _subdir != _trimdir:
            _retpath=os.path.join(_retpath, _subdir)
    return _retpath

def getNodeFromPath(path, cdslRepository, exists=True):
    """
    Returns the node from the given path. If a node is found incl. default it is returned. If not
    a ValueError is raised.
    @return: the nodename/id
    @rtype: String
    @raise ValueError: if no nodepart is found
    @param path: full path to the file
    @type path: String  
    @param cdslRepository: the cdsl repository
    @type cdslRepository: CdslRepository
    """
    import os
    if isHostdependentPath(path, cdslRepository, exists):
        try:
            return strippath(path, cdslRepository.getTreePath()).split(os.sep)[0]
        except:
            pass
    raise ValueError("Could not find nodepart in path %s" %path)

def isSubPath(_path, _subdir):
    import os
    import os.path
    _p=dirtrim(_path)
    _s=dirtrim(_subdir)
    return _p.startswith(_s+os.sep) or _p.endswith(os.path.join(os.sep, _s)) or _p.find(os.path.join(os.sep, _s)+os.sep)>=0 or _s==""

def commonpath(path1, path2):
    """
    Returns the longest path that is common to path1 and path2.
    """
    import os
    _p1=dirtrim(path1)
    _p2=dirtrim(path2)
    if not _p1 or _p1=="":
        return ""
    elif not _p2 or _p2=="":
        return ""
    elif _p1 == _p2:
        return _p1
    elif isSubPath(_p1, _p2):
        return _p2
    elif _p1.find(os.sep) > _p1.find(os.sep):
        _p1h, _p1t=os.path.split(_p1)
        return commonpath(_p1h, _p2)
    else:
        _p2h, _p2t=os.path.split(_p2)
        return commonpath(_p1, _p2h)

def dirtrim(_dir):
    import os
    _tmp=_dir
    if _tmp.startswith("."+os.sep):
        _tmp=_tmp[2:]
    if _dir.startswith(os.sep):
        _tmp=_tmp[1:]
    if _dir.endswith(os.sep):
        _tmp=_tmp[:-1]
    return _tmp    

def setDebug(option, opt, value, parser):
    from comoonics import ComLog
    import logging
    ComLog.setLevel(logging.DEBUG, "comoonics.cdsl")
#    ComLog.getLogger().propagate=1
    
def setQuiet(option, opt, value, parser):
    from comoonics import ComLog
    import logging
    ComLog.setLevel(logging.CRITICAL)
    
def setNoExecute(option, opt, value, parser):
    from comoonics import ComSystem
    ComSystem.__EXEC_REALLY_DO="simulate"

def commonoptparseroptions(parser):
    """
    Sets the give optparser to the common options needed by all cdsl commands.
    """
    import logging
    from ComCdslRepository import ComoonicsCdslRepository
    
    logging.basicConfig()
    
    parser.add_option("-n", "--noexecute", action="callback", callback=setNoExecute, help="display what would be done, but not really change filesystem")
    parser.add_option("-q", "--quiet", action="callback", callback=setQuiet, help="Quiet, does not show any output")
    parser.add_option("-d", "--verbose", action="callback", callback=setDebug, help="Quiet, does not show any output")

    parser.add_option("-i", "--inventoryfile", dest="inventoryfile", default=ComoonicsCdslRepository.default_resources[0], help="path to the cdsl inventory")
    parser.add_option("-c", "--clusterconf", dest="clusterconf", default=None)
    parser.add_option("-r", "--root", dest="root", default="/", help="set the chroot path")
    parser.add_option("-m", "--mountpoint", dest="mountpoint", default="", help="set the mountpoint for this fs if any.")
    return parser

def get_defaultsfiles():
    import os.path
    default_dir = "/etc/comoonics"
    home_dir = os.path.join(os.environ.get('HOME', ''), ".comoonics")
    globalcfgdefault_file= os.path.join(default_dir, "cdsl.cfg") 
    localcfgdefault_file= os.path.join(home_dir, "cdsl.cfg")
    return globalcfgdefault_file, localcfgdefault_file

def get_defaultsenvkey():
    return "COMOONICS_CDSL_CFG" 

from comoonics.ComExceptions import ComException

class CdslInitException(ComException):pass
class CdslUnsupportedTypeException(ComException):pass
class CdslPrefixWithoutNodeidsException(ComException):pass
class CdslDoesNotExistException(ComException):pass
class CdslSourcePathIsAlreadyCdsl(ComException): pass
class CdslAlreadyExists(ComException): pass
class CdslIsNoCdsl(ComException): pass
class CdslOfSameType(ComException): pass
class CdslHasChildren(ComException): pass
class CdslNodeidsRequired(ComException): pass
class CdslNodeIDInUse(ComException): pass

def getCdsl(src, type, cdslrepository, clusterinfo=None, nodes=None, timestamp=None, ignoreerrors=False, realpath=True, stripsource=True):
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
    @param realpath: Should this src path be resolved to its realpath. Default: True.
    @type  realpath: L{Boolean}
    @param stripsource: Should this src path be stripped and checked or taken as is. 
                        This can be switched of if read from repo (speed up). Default: True.
    @type  stripsource: L{Boolean}
    """
    from comoonics.cdsl.ComCdsl import ComoonicsCdsl
    return ComoonicsCdsl(src, type, cdslrepository, clusterinfo=clusterinfo, nodes=nodes, timestamp=timestamp, ignoreerrors=ignoreerrors, realpath=realpath, stripsource=stripsource)

class CdslNotFoundException(ComException):
    def __init__(self, src, repository=None):
        ComException.__init__(self, src)
        self.repository=repository
    def __str__(self):
        return "Could not find Cdsl \"%s\" in repository %s" %(self.value, self.repository)
class CdslRepositoryNotConfigfileException(ComException):pass
class CdslVersionException(ComException): pass
    
def getCdslRepository(**keys):
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
    return getCdslRepositoryClass()(**keys)

def getCdslRepositoryClass():
    from comoonics.cdsl.ComCdslRepository import ComoonicsCdslRepository
    return ComoonicsCdslRepository

CDSL_HOSTDEPENDENT_TYPE="hostdependent"
CDSL_SHARED_TYPE="shared"
CDSL_UNKNOWN_TYPE="unknown"
