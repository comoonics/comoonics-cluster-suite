"""Comoonics cdsl validate module


Checks directories inside CDSL Link, which must be defined in a given cdslRepository, 
for existing cdsls. Append cdsls which are found to cdslRepository. Includes a special 
version of os.walk() (see L{os} for details), which skips submounts but follows symbolic links.
"""


__version__ = "$Revision: 1.6 $"

import comoonics.pythonosfix as os
    
def ismount(path):
    """
    Uses os.path.ismount (see L{os.path} for details) and wrap it to detect 
    bind mounts.
    """
    from comoonics import ComSystem
    if os.path.ismount(path):
        return True
    _tmp1 = ComSystem.execLocalStatusOutput("mount")[1]
    _tmp2 = _tmp1.split("\n")
    for line in _tmp2:
        if line.split()[2] == os.path.normpath(path):
            return True
    return False

def walk(top, topdown=True, onerror=None):
    """Directory tree generator.

    Modified version of os.walk(). See L{os} for details of usage.
    In contrast to os.path.walk it does not stop when hitting a symbolic 
    link, but does stop when hitting a underlying mountpoint (replaced 
    i{if not islink(path):} with i{if not ismount(path):}). Needs import 
    from error, listdir of Module L{os} to get needed globals (added i{from 
    os import error, listdir}). Removed import from method islink(). Uses method 
    ismount which is defined in this module.
    """

    from os.path import join, isdir
    from os import error, listdir

    # We may not have read permission for top, in which case we can't
    # get a list of the files the directory contains.  os.path.walk
    # always suppressed the exception then, rather than blow up for a
    # minor reason when (say) a thousand readable directories are still
    # left to visit.  That logic is copied here.
    try:
        # Note that listdir and error are globals in this module due
        # to earlier import-*.
        names = listdir(top)
    except error, err:
        if onerror is not None:
            onerror(err)
        return

    dirs, nondirs = [], []
    for name in names:
        if isdir(join(top, name)):
            dirs.append(name)
        else:
            nondirs.append(name)

    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        path = join(top, name)
        if not ismount(path):
            for x in walk(path, topdown, onerror):
                yield x
    if not topdown:
        yield top, dirs, nondirs
                          
def cdslValidate(cdslRepository,clusterInfo,_onlyvalidate=True,chroot=""):
    """
    Method to search filesystem at cdsl link, which is defined in given cdslRepository, for cdsls.
    Adds found cdsls to cdslRepository.
    @param cdslRepository: Includes needed informations about cdsls like cdsl_link
    @type cdslRepository: L{CdslRepository}
    @param clusterInfo: Includes needed information about cluster like nodenames and -ids
    @type clusterInfo: L{ClusterInfo}
    @param _onlyvalidate: only validate but not change if True else also change the database. Default False
    @type _onlyvalidate: Boolean
    @return: Returns two lists. The first list are all files added to the repository and second all that 
            have to be|have been removed.
    @rtype: list<L{Cdsl}>, list<L{Cdsl}>  
    """
    from comoonics.cdsl import dirtrim
    from comoonics.ComPath import Path
    
    _added=list()
    _removed=list()
    
    _cdslLink = dirtrim(cdslRepository.getDefaultCdslLink())
    if chroot and chroot == "":
        chroot=cdslRepository.root
    if chroot and chroot == "":
        chroot="/"
    _rootMountpoint = os.path.join(chroot, dirtrim(cdslRepository.getDefaultMountpoint()))

    _cwd=Path(_rootMountpoint)
    _cwd.pushd()
    for root,dirs,files in walk(_cdslLink):
        for name in files:
            _tmp2 = dirtrim(os.path.join(root,name).replace(_rootMountpoint,"",1).replace(_cdslLink,"",1))
            __added, __removed=cdslRepository.update(_tmp2,clusterInfo,_onlyvalidate,chroot)
            if __added:
                _added.append(__added)
            if __removed:
                _removed.append(__removed)
        for name in dirs:
            _tmp2 = dirtrim(os.path.join(root,name).replace(_rootMountpoint,"",1).replace(_cdslLink,"",1))
            __added, __removed=cdslRepository.update(_tmp2,clusterInfo,_onlyvalidate,chroot)
            if __added:
                _added.append(__added)
            if __removed:
                _removed.append(__removed)
    _cwd.popd()
    return _added, _removed
