""" Comoonics regexp modification module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComRegexpModification.py,v 1.7 2010-11-16 11:30:25 marc Exp $
#


__version__ = "$Revision: 1.7 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComRegexpModification.py,v $

import re

from ComFileModification import FileModification
from comoonics import ComSystem
from comoonics import ComLog

CMD_CP="/bin/cp"

class RegexpModification(FileModification):
    SAVESTRING=".regexp"
    DEFAULT_OPTIONS=0
    __logStrName__="comoonics.enterprisecopy.ComRegexpModification.RegexpModification"
    logger=ComLog.getLogger(__logStrName__)
    # Regular Expression Modification
    def __init__(self, element, doc):
        FileModification.__init__(self, element, doc)

    def doModifications(self, file):
        save=True
        if self.hasAttribute("nobackup"):
            if self.getAttribute("nobackup") == "1":
                save=False
        ComSystem.execMethod(self.doRegexpModifications, file, save)

    def doRegexpModifications(self, file, save=True, dest=None):
        search = self.getAttribute("search")
        replace = self.getAttribute("replace")
        if self.hasAttribute("options"):
            options = self.getREOptions(self.getAttribute("options"))
        else:
            options = self.DEFAULT_OPTIONS
        if save:
            cmd = list()
            cmd.append(CMD_CP)
            cmd.append(file.getAttribute("name"))
            cmd.append(file.getAttribute("name")+self.SAVESTRING)
            rc, ret = ComSystem.execLocalStatusOutput(" ".join(cmd))
            if rc:
                RegexpModification.logger.error(" ".join(cmd) + " " + ret)
            else:
                RegexpModification.logger.debug(" ".join(cmd) + " " + ret)
        try:
            if file.hasAttribute("sourcefile"):
                source=open(file.getAttribute("sourcefile"))
            else:
                source=open(file.getAttribute("name"))
            lines=source.readlines()
            source.close()
            if not dest:
                dest2=open(file.getAttribute("name"), 'w')
            else:
                dest2=dest
            if options | re.MULTILINE:
                dest2.write(re.compile(search, options).sub(replace, "".join(lines)))
            else:
                for line in lines:
                    dest2.write(re.compile(search, options).sub(replace, line))

            if not dest:
                dest2.close()
        except IOError, ioe:
            RegexpModification.logger.error(ioe)


    def getREOptions(self, options):
        __options=self.DEFAULT_OPTIONS
        if options:
            if options.find("i") >= 0:
                __options=__options|re.IGNORECASE
            if options.find("m") >= 0:
                __options=__options|re.MULTILINE
            if options.find("l") >= 0:
                __options=__options|re.LOCALE
            if options.find("x") >= 0:
                __options=__options|re.VERBOSE
            if options.find("s") >= 0:
                __options=__options|re.DOTALL
            if options.find("u") >= 0:
                __options=__options|re.UNICODE

        return __options

# $Log: ComRegexpModification.py,v $
# Revision 1.7  2010-11-16 11:30:25  marc
# - made the regexp dep of execLocal
#
# Revision 1.6  2010/03/08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.5  2010/02/10 12:48:46  mark
# added .storage path in includes
#
# Revision 1.4  2007/09/07 14:41:24  marc
# - added catching of IOExceptino
# - logging
#
# Revision 1.3  2006/09/18 13:58:10  marc
# added options for Regularexpressions
#
# Revision 1.2  2006/07/21 08:59:09  mark
# added nobackup option
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.2  2006/07/07 11:35:00  mark
# changed to inherit FileModification
#
# Revision 1.1  2006/06/30 12:42:45  mark
# initial checkin
#
