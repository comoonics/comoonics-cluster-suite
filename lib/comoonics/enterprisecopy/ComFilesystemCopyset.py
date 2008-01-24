""" Comoonics filecopy copyset module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFilesystemCopyset.py,v 1.8 2008-01-24 10:07:42 marc Exp $
#


__version__ = "$Revision: 1.8 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComFilesystemCopyset.py,v $

import xml.dom
import exceptions
import warnings
from xml import xpath

from ComCopyObject import CopyObject
from ComCopyset import *
from comoonics.ComDisk import Disk
from comoonics.ComExceptions import *
from comoonics import ComSystem
from comoonics import ComLog
from comoonics.ComExceptions import ComException

from ComFilesystemCopyObject import FilesystemCopyObject
from ComPathCopyObject import PathCopyObject
from ComArchiveCopyObject import ArchiveCopyObject

CMD_RSYNC="/usr/bin/rsync"

class RSyncError(ComException):

    """
    EXIT_VALUES copied from manpage
    """
    EXIT_VALUES={
       1:  "Syntax or usage error",
       2:  "Protocol incompatibility",
       3:  "Errors selecting input/output files, dirs",
       4:  """Requested action not supported: an attempt was made to manipulate
64-bit files on a platform that  cannot  support
them; or an option was specified that is supported by the client
and not by the server.
""",
       5:  "Error starting client-server protocol",
       6:  "Daemon unable to append to log-file",
       10: "Error in socket I/O",
       11: "Error in file I/O",
       12: "Error in rsync protocol data stream",
       13: "Errors with program diagnostics",
       14: "Error in IPC code",
       20: "Received SIGUSR1 or SIGINT",
       21: "Some error returned by waitpid()",
       22: "Error allocating core memory buffers",
       23: "Partial transfer due to error",
       24: "Partial transfer due to vanished source files",
       25: "The --max-delete limit stopped deletions",
       30: "Timeout in data send/receive"
    }

    IGNORE_CODES= [ 6, 10, 11, 24 ]

    def __init__(self, execlocalexc):
        self._errorcode=execlocalexc.rc >> 8
        self._error=execlocalexc.err
        self._out=execlocalexc.out
    def __str__(self):
        _type=self.getErrorType()
        return """<%s> %s<%u>: %s
erroroutput: %s""" %(_type, "RSyncError", self._errorcode, self.getErrorMessage(), self._error)
    def getErrorType(self):
        if self.isIgnored():
            return "WARNING"
        else:
            return "ERROR"
    def isIgnored(self):
        return self._errorcode in self.IGNORE_CODES

    def getErrorMessage(self):
        return self.EXIT_VALUES.get(self._errorcode, "Unknown Error")

__logStrLevel__ = "comoonics.enterprisecopy.ComFilesystemCopyset.FilesystemCopyset"
class FilesystemCopyset(Copyset):
    def __init__(self, element, doc):
        Copyset.__init__(self, element, doc)
        try:
            __source=xpath.Evaluate('source', element)[0]
            self.source=CopyObject(__source, doc)
        except Exception, e:
            ComLog.getLogger(__logStrLevel__).warning(e)
            raise ComException("Source for filesystem copyset with name \"%s\" is not defined" %(self.getAttribute("name", "unknown")))
        try:
            __dest=xpath.Evaluate('destination', element)[0]
            self.dest=CopyObject(__dest, doc)
        except Exception, e:
        #except None:
            #print ("EXCEPTION: %s\n" %e)
            ComLog.getLogger(__logStrLevel__).warning(e)
            raise ComException("Destination for filesystem copyset with name \"%s\" is not defined" %(self.getAttribute("name", "unknown")))

    def doCopy(self):
        # do everything
        #stype=self.source.getAttribute("type")
        #dtype=self.dest.getAttribute("type")

        self.prepareSource()

        # Update MetaData
        self.dest.updateMetaData(self.source.getMetaData())

        self.prepareDest()

        # decide how to copy data
        try:
            self._copyData()
        except RSyncError, _re:
            if _re.isIgnored():
                warnings.warn(_re.__str__())
            else:
                raise _re

        self.postSource()
        self.postDest()

    def undoCopy(self):
        # simple undo we need to think about that again
        try:
            self.postSource()
        except Exception, e:
            ComLog.getLogger(__logStrLevel__).warning(e)
        try:
            self.postDest()
        except Exception, e:
            ComLog.getLogger(__logStrLevel__).warning(e)

    def prepareSource(self):
        #do things like fsck, mount
        # scan for fsconfig
        self.source.prepareAsSource()

    def postSource(self):
        self.source.cleanupSource()

    def postDest(self):
        self.dest.cleanupDest()

    def prepareDest(self):
        # do things like mkfs, mount
        self.dest.prepareAsDest()

#    def copyFsAttributes(self):
#        """ copy all Attributes from source to dest that are not defined
#        in dest
#        """
#        # save dest attributes
#        __attr = self.destination.getFileSystem().getElement().attributes
#        # copy all source fs info to dest
#        self.destination.setFileSystem(self.source.getFileSystem())
#        # restore saved attibutes from dest
#        self.destination.getFileSystem().setAttributes(__attr)

    def getCopyCommandOptions(self, _cmd=CMD_RSYNC):
        """
        Returns the options for the sync command and also the supported options. Xattrs, selinux, acls
        """
        _opts=["--archive", "--update", "--one-file-system", "--delete"]
        try:
            __out = ComSystem.execLocalOutput("%s --version | tr '\n' ' ' | grep -i capabilities | grep -i xattr" %_cmd)
            _opts.append("--xattrs")
        except ComSystem.ExecLocalException:
            pass
        try:
            __out = ComSystem.execLocalOutput("%s --version | tr '\n\' ' ' | grep -i capabilities | grep -i acls" %_cmd)
            _opts.append("--acls")
        except ComSystem.ExecLocalException:
            pass
        return _opts

    def _getFSCopyCommand(self):
        __cmd=CMD_RSYNC
        __cmd+=" ".join(self.getCopyCommandOptions(__cmd))
        __cmd+=self.source.getMountpoint().getAttribute("name")
        __cmd+="/ "
        __cmd+=self.dest.getMountpoint().getAttribute("name")
        __cmd+="/"
        return __cmd

    def _copyData(self):
        # FIXME: this implementation is VERY POOR!! This should be fixed without any instance casting of classes on
        #        the end of the child tree. There should be a abstract class FilesystemCopyObject and PathCopyObject
        #        derive from!!!!
        # 1. copy fs/path to fs/path
        ComLog.getLogger(__logStrLevel__).debug("doCopy: instance(self.source: %s), instance(self.dest: %s)" %(self.source.__class__, self.dest.__class__))
        ComLog.getLogger(__logStrLevel__).debug("doCopy: isinstance(%s, PathCopyObject): %s" %(self.source.__class__, isinstance(self.source, PathCopyObject)))
        if isinstance(self.source, FilesystemCopyObject) or isinstance(self.source, PathCopyObject):
            mountpoint=self.source.getMountpoint().getAttribute("name")
            if isinstance(self.dest, FilesystemCopyObject):
                __cmd = self._getFSCopyCommand()
                try:
                    __out = ComSystem.execLocalOutput(__cmd, True)
                except ComSystem.ExecLocalException, ele:
                    raise RSyncError(ele)
                #ComLog.getLogger(__logStrLevel__).debug("doCopy: "  + __cmd +" "+ __ret)
                return True

            # 2. copy fs to archive
            elif isinstance(self.dest, ArchiveCopyObject):
#                try:
                archive=self.dest.getDataArchive()
                archive.createArchive("./", mountpoint)
                return True
                #except Exception, e:
#                except None, e:
#                    ComLog.getLogger(__logStrLevel__).error(e)
#                return False
        # 3. copy archive to fs
        elif isinstance(self.source, ArchiveCopyObject):
            if isinstance(self.dest, FilesystemCopyObject) or isinstance(self.dest, PathCopyObject):
#                try:
                archive=self.source.getDataArchive()
                mountpoint=self.dest.getMountpoint().getAttribute("name")
                archive.extractArchive(mountpoint)
                return True
#                except Exception, e:
#                    ComLog.getLogger(__logStrLevel__).error(e)
#                return False
        raise ComException("data copy %s to %s is not supported" \
                           %( self.source.__class__.__name__, self.dest.__class__.__name__))

# $Log: ComFilesystemCopyset.py,v $
# Revision 1.8  2008-01-24 10:07:42  marc
# bugfix for 189
# - added options for rsync so that acls and xattrs will also be synced.
#
# Revision 1.7  2007/10/16 15:26:24  marc
# - fixed BUG 27, break or warn when rsync error
#
# Revision 1.6  2007/09/07 14:37:37  marc
# - added support for PathCopyObject
#
# Revision 1.5  2007/08/07 11:18:01  marc
# - Fix Bug BZ #77 that exceptions from commands being executed are ignored. They should not!
#
# Revision 1.4  2007/07/25 11:10:09  marc
# - better errormessages
# - loglevel
#
# Revision 1.3  2007/03/26 07:57:30  marc
# kicked out a nasty print (Mr. Hlawatschek!)
#
# Revision 1.2  2006/12/08 09:39:51  mark
# added support for generic CopyObject Framework
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.4  2006/07/06 08:59:07  mark
# Changed bahavior on rsync error codes see Bug #6
#
# Revision 1.3  2006/07/03 14:30:24  mark
# added undo
#
# Revision 1.2  2006/07/03 10:41:01  mark
# bug fix for rsync command
#
# Revision 1.1  2006/06/28 17:25:16  mark
# initial checkin (stable)
#