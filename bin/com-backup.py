#!/usr/bin/python
"""
This program is only a test program to evaluate functionality of the comoonics.backup api
"""

__version__ = "0.1"
__description__="""
This program is only a test program to evaluate functionality of the comoonics.backup API
"""

import logging
import sys
import os.path
sys.path.append(os.path.join(os.path.normpath(sys.prefix), "lib", "python" + sys.version[:3], "site-packages"))

try:
   from comoonics.tools.poptparse import PersistentOptionParser as OptionParser
except ImportError:
   from optparse import OptionParser 
from optparse import OptionGroup

import comoonics.storage
from comoonics import ComLog

__logStrLevel__="com-backup"

logger=logging.getLogger(__logStrLevel__)
logger.propagate=0
logger.setLevel(logging.INFO)

def parse_cmdline(args=sys.argv):
   parser = OptionParser(description=__doc__, usage="usage: %prog [options] action [arguments]", version=__version__)
   # Flags
   parser.add_option("-v", "--verbose",     default=False, action="store_true", help="toggle debugmode and be more helpful")
#   parser.add_option("-a", "--ask",      dest="ask",      default=False, action="store_true", help="ask before any being command executed")
#   parser.add_option("-S", "--simulate",   dest="simulate",   default=False, action="store_true", help="don't execute anything just simulate. Only valid for developer. It might not do what you expect!")

   # Options
   backup_options=OptionGroup(parser, "Backup Options")
   backup_options.add_option("-i", "--implementation", choices=comoonics.storage.ComArchive.ArchiveHandlerFactory.listArchiveHandlerNames(),
                             help="Select backup implementation. Valid options are: %s." %comoonics.storage.ComArchive.ArchiveHandlerFactory.listArchiveHandlerNames())
   backup_options.add_option("-t", "--type", default=comoonics.storage.ComArchive.ArchiveHandler.NONE,
                             help="Set the backup format type. Default: %default")
   backup_options.add_option("-c", "--compression", default=comoonics.storage.ComArchive.ArchiveHandler.NONE,
                             help="Set the compression of this backup handler (if any). Default %default.")
   backup_options.add_option("-f", "--format", default=comoonics.storage.ComArchive.ArchiveHandler.NONE,
                             help="Set the backup format of this backup handler (if any). Default %default.")
   parser.add_option_group(backup_options)
   try:
      parser.setGlobalDefaultsFilename(get_defaultsfiles()[0])
      parser.setLocalDefaultsFilename(get_defaultsfiles()[1], get_defaultsenvkey())
   except (TypeError, NameError):
      pass

   (options, args) = parser.parse_args(args)

   if options.verbose:
      ComLog.getLogger().propagate=1
      ComLog.setLevel(logging.DEBUG)
   else:
      ComLog.setLevel(logging.INFO)
   if not args or len(args) < 2:
      parser.error("To few arguments given to command.")
   return (options, args[0], args[1:])

(options, action, arguments)=parse_cmdline(sys.argv)
implementation=comoonics.storage.ComArchive.ArchiveHandlerFactory.getArchiveHandler(name=options.implementation, hndlrformat=options.format, hndlrtype=options.type, compression=options.compression)
logger.debug("Implementation %s: Executing action %s with arguments %s." %(implementation, action, arguments))