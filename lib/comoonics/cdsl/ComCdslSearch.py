"""Comoonics cdsl search module


Checks directories inside CDSL Link, which must be defined in a given cdslRepository, 
for existing cdsls. Append cdsls which are found to cdslRepository. Includes a special 
version of os.walk() (see L{os} for details), which skips submounts but follows symbolic links.
"""


__version__ = "$Revision: 1.4 $"

from xml import xpath
from xml.dom.ext.reader import Sax2

from ComCdslRepository import CdslRepository

import comoonics.pythonosfix as os
    
def ismount(path):
    """
    Uses os.path.ismount (see L{os.path} for details) and wrap it to detect 
    bind mounts.
    """
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
    from comoonics import ComSystem

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
                          
def cdslSearch(cdslRepository,clusterInfo,chroot="/"):
    """
    Method to search filesystem at cdsl link, which is defined in given cdslRepository, for cdsls.
    Adds found cdsls to cdslRepository.
    @param cdslRepository: Includes needed informations about cdsls like cdsl_link
    @type cdslRepository: L{CdslRepository}
    @param clusterInfo: Includes needed information about cluster like nodenames and -ids
    @type clusterInfo: L{ClusterInfo}
    """
    _cdslLink = re.sub('/$','', cdslRepository.getDefaultCdslLink())
    _rootMountpoint = re.sub('/$','', os.path.join(chroot,re.sub('^/','', cdslRepository.getDefaultMountpoint())))
    _path = os.path.join(chroot,re.sub('^/','', cdslRepository.getDefaultMountpoint()),re.sub('^/','', _cdslLink))
    
    for root,dirs,files in walk(_path):
            for name in files:
                _tmp = os.path.join(root,name).replace(_cdslLink,"",1)
                _tmp2 = (os.path.join(root,name).replace(_rootMountpoint,"",1)).replace(_cdslLink,"",1)
                cdslRepository.update(_tmp2,clusterInfo,chroot)
            for name in dirs:
                _tmp = os.path.join(root,name).replace(_cdslLink,"",1)
                _tmp2 = (os.path.join(root,name).replace(_rootMountpoint,"",1)).replace(_cdslLink,"",1)
                cdslRepository.update(_tmp2,clusterInfo,chroot)

def main():
    """
    Creates clusterRepository, clusterInfo and cdslRepository and search for cdsls which 
    are not already included in inventoryfile.
    """
    # create Reader object
    reader = Sax2.Reader(validate=True)

    #parse the document and create clusterrepository object
    file = os.fdopen(os.open("../lib/comoonics/cdsl/test/cluster.conf",os.O_RDONLY))
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
    clusterInfo = ClusterInfo(clusterRepository)
        
    cdslRepository = CdslRepository("/var/lib/cdsl/cdsl_inventory.xml",None,False)
    cdslSearch(cdslRepository,clusterInfo)
         
if __name__ == '__main__':
    main()