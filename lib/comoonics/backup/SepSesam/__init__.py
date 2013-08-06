"""

Init this package

"""

import SepSesamBackupHandler
from comoonics.storage.ComArchive import ArchiveHandlerFactory
ArchiveHandlerFactory.registerArchiveHandler(SepSesamBackupHandler.SepSesamBackupHandler)
