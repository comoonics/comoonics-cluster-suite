"""

Init this package

"""

import SepSesam
from exceptions import ImportError
from comoonics.storage.ComArchive import ArchiveHandlerFactory
ArchiveHandlerFactory.registerArchiveHandler(EMCLegatoBackupHandler)
