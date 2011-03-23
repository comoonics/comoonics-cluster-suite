""" Comoonics filecopy copyset module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFilesystemCopyset.py,v 1.19 2011-02-21 16:23:53 marc Exp $
#


__version__ = "$Revision: 1.19 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComFilesystemCopyset.py,v $

import xml.dom
import warnings

from ComCopyObject import CopyObject
from ComCopyset import Copyset
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
    DEFAULT_OPTIONS=["--archive", "--update", "--one-file-system", "--delete"]
    def __init__(self, *params, **kwds):
        """
        Valid constructors are
        __init__(element, doc)
        __init__(source, dest)
        __init__(source=source, dest=dest)
        """
        if (len(params)==2 and isinstance(params[0], CopyObject) and isinstance(params[1], CopyObject)) or \
           (kwds and kwds.has_key("source") and kwds.has_key("dest")):
            source=None
            dest=None
            if len(params)==2:
                source=params[0]
                dest=params[1]
            else:
                source=kwds["source"]
                dest=kwds["dest"]
            doc=xml.dom.getDOMImplementation().createDocument(None, self.TAGNAME, None)
            element=doc.documentElement
            element.setAttribute("type", "filesystem")
            element.appendChild(source.getElement())
            element.appendChild(dest.getElement())
            Copyset.__init__(self, element, doc)
            self.source=source
            self.dest=dest
        elif len(params)==2:
            element=params[0]
            doc=params[1]
            Copyset.__init__(self, element, doc)
            try:
                __source=element.getElementsByTagName('source')[0]
                self.source=CopyObject(__source, doc)
            except Exception, e:
                ComLog.getLogger(__logStrLevel__).warning(e)
                ComLog.debugTraceLog(ComLog.getLogger(__logStrLevel__))
                raise ComException("Source for filesystem copyset with name \"%s\" is not defined" %(self.getAttribute("name", "unknown")))
            try:
                __dest=element.getElementsByTagName('destination')[0]
                self.dest=CopyObject(__dest, doc)
            except Exception, e:
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
        if isinstance(self.source, FilesystemCopyObject) and self.source.filesystem.getLabel(self.source.device) != "" and self.dest.filesystem.getLabel(self.dest.device) == "":
            self.dest.filesystem.labelDevice(self.dest.device, self.source.filesystem.getLabel(self.source.device))

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
        _opts=FilesystemCopyset.DEFAULT_OPTIONS

        if self.getProperties():
            for _property in self.getProperties().keys():
                _value=self.getProperties()[_property].getValue()
                if _value=="":
                    if len(_property)==1:
                        _opts.append("-%s" %_property)
                    else:
                        _opts.append("--%s" %_property)
                else:
                    if len(_property)==1:
                        _opts.append("-%s %s" %(_property, _value))
                    else:
                        _opts.append("--%s %s" %(_property, _value))
        return _opts

    def _getFSCopyCommand(self):
        __cmd=CMD_RSYNC
        __cmd+=" "+" ".join(self.getCopyCommandOptions(__cmd))+" "
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
            if isinstance(self.source, FilesystemCopyObject):
                if not self.source.filesystem.isCopyable():
                    return True
            mountpoint=self.source.getMountpoint().getAttribute("name")
            ComLog.getLogger(__logStrLevel__).debug("doCopy: isinstance(%s, PathCopyObject): %s" %(self.dest.__class__, isinstance(self.dest, PathCopyObject)))
            if isinstance(self.dest, FilesystemCopyObject) or isinstance(self.dest, PathCopyObject):
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
                if self.dest.filesystem.copyable:
                    return True
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
# Revision 1.19  2011-02-21 16:23:53  marc
# - implemented functionality that a filesystem would be queried if it allows copying or not (e.g. swap does not)
#
# Revision 1.18  2011/02/17 13:14:04  marc
# added support for labeled filesystems
#
# Revision 1.17  2010/03/08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.16  2010/02/09 21:48:24  mark
# added .storage path in includes
#
# Revision 1.15  2008/03/12 12:27:41  marc
# - added a constructor that also would take copyobjects as is
# - introduced static variable for DEFAULT_OPTIONS to be overwritten if needed
# - added tests.
#
# Revision 1.14  2008/02/20 10:52:40  mark
# add support for copy of FilesystemCopyObject to PathCopyObject
#
# Revision 1.13  2008/01/25 14:08:46  marc
# - Fix BUG#191 so that options might be given via properties (2nd)
#
# Revision 1.12  2008/01/25 13:07:12  marc
# - Fix BUG#191 so that options might be given via properties
#
# Revision 1.11  2008/01/25 10:31:24  marc
# - BUG#191 removed ACL support as it does not work so easily
#
# Revision 1.10  2008/01/24 16:16:55  marc
# - fixed bug that rsync has space missing
#
# Revision 1.9  2008/01/24 13:38:37  marc
# - fixed bug that rsync has space missing
#
# Revision 1.8  2008/01/24 10:07:42  marc
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