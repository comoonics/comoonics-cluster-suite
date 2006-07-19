import sys
import os

sys.path.append("../lib")

from comoonics import ComScsi
from comoonics import ComSystem


ComSystem.setExecMode("ask")
#print os.listdir("/sys/class")

scsi=ComScsi.SCSI()
scsi.rescan("-", "-", "-", "-")
scsi.rescan("-", "0", "1", "2")
scsi.rescan("-", "x", "-", "-")
