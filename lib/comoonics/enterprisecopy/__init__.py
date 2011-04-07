"""

Init this package

"""

from ComModification import registerModification
from ComRequirement import registerRequirement
from ComCopyset import registerCopyset
from ComCopyObject import registerCopyObject
from ComModificationset import registerModificationset
from ComMessage import MessageRequirement, MessageModification
from ComPathModificationset import PathModificationset
from ComPathCopyObject import PathCopyObject
from ComISOFSModificationset import ISOFSModificationset

def get_defaultsfiles():
    import os.path
    default_dir = "/etc/comoonics"
    home_dir = os.path.join(os.environ['HOME'], ".comoonics")
    globalcfgdefault_file= os.path.join(default_dir, "enterprisecopy.cfg") 
    localcfgdefault_file= os.path.join(home_dir, "enterprisecopy.cfg")
    return globalcfgdefault_file, localcfgdefault_file

def get_defaultsenvkey():
    return "COMOONICS_ENTERPRISECOPY_CFG" 

registerModification("message", MessageModification)

registerRequirement("message", MessageRequirement)

registerModificationset("path", PathModificationset)
registerModificationset("isofs", ISOFSModificationset)

registerCopyObject("path", PathCopyObject)

try:
    from ComSysrqModification import SysrqModification
    registerModification("sysrq", SysrqModification)
except ImportError:
    pass

########
# $Log: __init__.py,v $
# Revision 1.5  2010-03-08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.4  2010/02/07 20:02:29  marc
# SysRq will only be loaded if available
#
# Revision 1.3  2008/02/19 17:32:41  mark
# added ComISOFSModificationset
#
# Revision 1.2  2007/09/07 14:34:45  marc
# added registry implementation for all sets.
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#