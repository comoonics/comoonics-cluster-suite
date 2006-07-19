import sys
import os

sys.path.append("../lib")

from comoonics import ComDevice

sys.path.append("../lib")

dev=ComDevice.Device("/dev/hda3")
print dev.getMountPoint()
if dev.isMounted():
    print "dev is mounted"
else:
    print "dev is not mounted"
