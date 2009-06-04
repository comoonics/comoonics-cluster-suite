"""

Comoonics cdsl package

Provides modules to manage cdsls on filesystem and in inventoryfile. Offers 
functionality to create, manipulate and check cdsls on filesystem/in inventoryfile. 
Discovers needed cdsl type by looking after type of used cluster configuration.
"""


#Files
DEFAULT_INVENTORY="/var/lib/cdsl/cdsl_inventory.xml"

#xpathes for elements

"""
#define defaultvalues
cdsltree_default = "cluster/cdsl"
cdsltreeShared_default = "cluster/shared"
cdslLink_default = "/cdsl.local"
maxnodeidnum_default = "0"
useNodeids_default = "False"

noderef_path_part = "nodes/noderef/@ref"
"""

def stripleadingsep(_path):
    """
    Normalizes a given path as described in os.path.normpath and strips all leading os.sep if existant.
    @param _path: the path to be stripped 
    @type _path: string
    @return: the normalized and stripped path as described
    @rtype : string 
    """
    import os.path
    _tmp=os.path.normpath(_path)
    if _tmp[0]==os.sep:
        _tmp=_tmp[1:]
    return _tmp

def guessType(_cdslpath, _cdslrepository, _exists=True):
    """
    Returns the guessed type of this cdsl.
    First it searches the repository of the last cdsl in path and takes the negative. If it does not
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
    _path=dirtrim(_cdslpath)
    if _path.find(os.sep) > 0:
#        _path=os.path.dirname(_path)
        while _path:
            _path, _tail=os.path.split(_path)
            _cdsl=_cdslrepository.getCdsl(_path)
            if _cdsl and _cdsl.isHostdependent():
                return Cdsl.SHARED_TYPE
            elif _cdsl and _cdsl.isShared():
                return Cdsl.HOSTDEPENDENT_TYPE

    if isHostdependentPath(os.path.realpath(_cdslpath), _cdslrepository, _exists):
        return Cdsl.SHARED_TYPE
    elif isSharedPath(os.path.realpath(_cdslpath), _cdslrepository, _exists):
        return Cdsl.HOSTDEPENDENT_TYPE
    else:
        return Cdsl.UNKNOWN_TYPE

def strippath(_path, _headpath):
    """
    Strips the headpath from the head of given path and returns the "relative" resultpath. If it does not
    match the _path is returned without changes.
    @param _path: the path to be stripped from
    @type _path: string
    @param _headpath: the path used as strip path.
    @type _headpath: string
    @return: the stripped path or the whole path if it does not match
    @rtype: string   
    """
    import os.path
    if os.path.normpath(_path[0:len(_headpath)])==os.path.normpath(_headpath):
        return _path[len(_headpath):]
    else:
        return _path

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
    _tmp2=os.path.join(root, cdslRepository.getDefaultMountpoint(), cdslRepository.getDefaultCdsltree())
    _tmp3=os.path.join(root, cdslRepository.getDefaultMountpoint(), cdslRepository.getDefaultCdsltreeShared())
    _tmp4=os.path.join(root, cdslRepository.getDefaultMountpoint(), cdslRepository.getDefaultCdslLink())
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
        __exists1=os.path.exists(os.path.join(_cdslRepository.getDefaultCdsltreeShared(), _tpath))
        __exists2=os.path.exists(_tpath)
    return __exists1 or ( __exists2 and isSubPath(_path, _cdslRepository.getDefaultCdsltreeShared()))

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
        __exists1=os.path.exists(os.path.join(_cdslRepository.getDefaultCdslLink(), _tpath))
        __exists2=os.path.exists(_tpath)
    return __exists1 or (__exists2 and (isSubPath(_path, _cdslRepository.getDefaultCdslLink()) or isSubPath(_path, _cdslRepository.getDefaultCdsltree())))

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

def isSubPath(_path, _subdir):
    import os
    import os.path
    _p=dirtrim(_path)
    _s=dirtrim(_subdir)
    return _p.startswith(_s+os.sep) or _p.endswith(os.path.join(os.sep, _s)) or _p.find(os.path.join(os.sep, _s)+os.sep)>=0

def dirtrim(_dir):
    import os
    _tmp=_dir
    if _dir.startswith(os.sep):
        _tmp=_tmp[1:]
    if _dir.endswith(os.sep):
        _tmp=_tmp[:-1]
    return _tmp    

#################
# $Log: __init__.py,v $
# Revision 1.4  2009-06-04 13:49:49  marc
# code review and rewrite.
# added unittests.
#