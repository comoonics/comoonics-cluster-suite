"""

Init this package

"""

from ComEMCLegatoBackupHandler import EMCLegatoBackupHandler
from comoonics.storage.ComArchive import ArchiveHandlerFactory
ArchiveHandlerFactory.registerArchiveHandler(EMCLegatoBackupHandler)
