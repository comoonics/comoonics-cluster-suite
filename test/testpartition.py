import sys
import traceback

sys.path.append("../lib")

import ComDisk
import ComUtils

#sourcedisk=ComDisk.Disk("/dev/sdd")
destdisk=ComDisk.Disk("/dev/sda")
#ComUtils.copyPartitionTable(sourcedisk, destdisk)

disk=ComDisk.Disk("/dev/hda")
disk.savePartitionTable("/tmp/hda.table")

disk=ComDisk.Disk("/dev/sdd")
disk.savePartitionTable("/tmp/sdd.table")

destdisk.restorePartitionTable("/tmp/sdd.table")
