import sys
import traceback

sys.path.append("../lib")

import ComBootDisk

boot=ComBootDisk.BootDisk("/dev/hda1")
boot.installBootloader()
