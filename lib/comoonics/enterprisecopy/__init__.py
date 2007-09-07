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
from ComSysrqModification import SysrqModification

registerModification("message", MessageModification)
registerModification("sysrq", SysrqModification)

registerRequirement("message", MessageRequirement)

registerModificationset("path", PathModificationset)

registerCopyObject("path", PathCopyObject)

########
# $Log: __init__.py,v $
# Revision 1.2  2007-09-07 14:34:45  marc
# added registry implementation for all sets.
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#