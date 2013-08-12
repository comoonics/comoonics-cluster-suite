""" Comoonics filecopy copyset module

The ComFilesystemCopyset presents a way to copy one filesystem/path to one another. It is represented by an XML configuration of the following
format:
   <copyset type="filesystem" name="save-tmp">
      <properties>
         <!-- properties are optional and will be added as commandline attributes to the copy command -->
         <property name="..">..</property>
         ..
      <properties>
      <source type="path">
         <path name="%s"/>
      </source>
      <destination type="path">
         <path name="%s"/>
      </destination>
   </copyset>

"""


# here is some internal information
# $Id: ComFilesystemCopyset.py,v 1.19 2011-02-21 16:23:53 marc Exp $
#


__version__ = "$Revision: 1.19 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComFilesystemCopyset.py,v $

import xml.dom
import warnings

from ComCopyObject import getCopyObject, CopyObject
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
   EXCLUDES_DELIMITOR=","
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
            self.source=getCopyObject(__source, doc)
         except Exception, e:
            ComLog.getLogger(__logStrLevel__).warning(e)
            ComLog.debugTraceLog(ComLog.getLogger(__logStrLevel__))
            raise ComException("Source for filesystem copyset with name \"%s\" is not defined" %(self.getAttribute("name", "unknown")))
         try:
            __dest=element.getElementsByTagName('destination')[0]
            self.dest=getCopyObject(__dest, doc)
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
      if isinstance(self.source, FilesystemCopyObject) and self.source.filesystem.getLabel(self.source.device) != "" and isinstance(self.dest, FilesystemCopyObject) and self.dest.filesystem.getLabel(self.dest.device) == "":
         self.dest.filesystem.labelDevice(self.dest.device, self.source.filesystem.getLabel(self.source.device))

#   def copyFsAttributes(self):
#      """ copy all Attributes from source to dest that are not defined
#      in dest
#      """
#      # save dest attributes
#      __attr = self.destination.getFileSystem().getElement().attributes
#      # copy all source fs info to dest
#      self.destination.setFileSystem(self.source.getFileSystem())
#      # restore saved attibutes from dest
#      self.destination.getFileSystem().setAttributes(__attr)

   def getCopyCommandOptions(self, _cmd=CMD_RSYNC):
      """
      Returns the options for the sync command and also the supported options. Xattrs, selinux, acls
      """
      import re
      opts=FilesystemCopyset.DEFAULT_OPTIONS

      if self.getProperties():
         for property in self.getProperties().keys():
            value=self.getProperties()[property].getValue().strip()
            if not value:
               if len(property)==1:
                  opts.append("-%s" %property)
               else:
                  opts.append("--%s" %property)
            else:
               values=re.split("\s*%s\s*" %self.EXCLUDES_DELIMITOR, value)
               if len(property)==1:
                  format='-%s %s'
               else:
                  format='--%s=%s'
               for value in values:
                  opts.append(format %(property, value))
      return opts

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
      #      the end of the child tree. There should be a abstract class FilesystemCopyObject and PathCopyObject
      #      derive from!!!!
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
#            try:
            archive=self.dest.getDataArchive()
            archive.createArchive("./", mountpoint)
            return True
            #except Exception, e:
#            except None, e:
#               ComLog.getLogger(__logStrLevel__).error(e)
#            return False
      # 3. copy archive to fs
      elif isinstance(self.source, ArchiveCopyObject):
         if isinstance(self.dest, FilesystemCopyObject) or isinstance(self.dest, PathCopyObject):
            if isinstance(self.dest, FilesystemCopyObject) and not self.dest.filesystem.copyable:
               return True
#            try:
            archive=self.source.getDataArchive()
            mountpoint=self.dest.getMountpoint().getAttribute("name")
            archive.extractArchive(mountpoint)
            return True
#            except Exception, e:
#               ComLog.getLogger(__logStrLevel__).error(e)
#            return False
      raise ComException("data copy %s to %s is not supported" \
                     %( self.source.__class__.__name__, self.dest.__class__.__name__))

