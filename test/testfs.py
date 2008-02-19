import sys
import traceback
import copy

sys.path.append("../lib")

from comoonics import ComDevice
from comoonics import ComUtils
from comoonics import ComFileSystem
from comoonics import ComDataObject
from comoonics.enterprisecopy import ComCopyset
from comoonics.ComFileSystem import *

#sourcedisk=ComDisk.Disk("/dev/sdd")

#from Ft.Xml import *
#from Ft.Xml.Domlette import implementation, PrettyPrint

import xml.dom
from xml.dom import EMPTY_NAMESPACE
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml import xpath


# create Reader object
reader = Sax2.Reader()

xml_fs2fs="""
<root>
    <copyset type="filesystem">
          <source type="filesystem">
              <device name="/dev/VG_TEST/LV_SOURCE">
                <filesystem type="gfs"/>
                <mountpoint name="/mnt/source"/>
            </device>
          </source>
          <destination type="filesystem">
            <device name="/dev/VG_TEST/LV_DEST" id="testfs">
                  <filesystem type="gfs" clustername="vmwareclusternew"/>
                  <mountpoint name="/mnt/dest">
                      <option name="lockproto" value="lock_nolock"/>
                  </mountpoint>
               </device>
           </destination>
    </copyset>
</root>
"""

xml_fs2arc="""
<root>
    <copyset type="filesystem">
          <source type="filesystem">
              <device name="/dev/VG_TEST/LV_SOURCE">
                <filesystem type="gfs"/>
                <mountpoint name="/mnt/source">
                    <option name="ro"/>
                </mountpoint>
            </device>
          </source>
          <destination type="backup">
              <metadata>
                <archive type="file" format="tar" compression="none" name="/tmp/metadata.tar">
                    <file name="./testfs.xml"/>
                </archive>
              </metadata>
              <data>
                <archive type="file" format="tar" compression="gzip" name="/tmp/testdata.tar.gz"/>
              </data>
          </destination>
    </copyset>
</root>
"""

xml_arc2fs="""
<root>
    <copyset type="filesystem">
          <source type="backup">
              <metadata>
                <archive type="file" format="tar" compression="none" name="/tmp/metadata.tar">
                    <file name="./testfs.xml"/>
                </archive>
              </metadata>
              <data>
                <archive type="file" format="tar" compression="gzip" name="/tmp/testdata.tar.gz"/>
              </data>
          </source>
          <destination type="filesystem">
            <device name="/dev/VG_TEST/LV_DEST" id="testfs">
                  <filesystem type="gfs" clustername="vmwareclusternew"/>
                  <mountpoint name="/mnt/dest">
                      <option name="lockproto" value="lock_nolock"/>
                  </mountpoint>
               </device>
           </destination>
    </copyset>
</root>
"""

def usage():
    print ("%s fs2fs | fs2arc | arc2fs" % sys.argv[0])
    sys.exit(127)

print len(sys.argv)
if len(sys.argv) < 2:
    usage()

if sys.argv[1] == "fs2fs":
    xml=xml_fs2fs
elif sys.argv[1] == "fs2arc":
    xml=xml_fs2arc
elif sys.argv[1] == "arc2fs":
    xml=xml_arc2fs
else:
    usage()



#file=os.fdopen(os.open("./example_config.xml",os.O_RDONLY))
#doc = reader.fromStream(file)

doc = reader.fromString(xml)

PrettyPrint(doc)

sets = xpath.Evaluate('root/copyset[@type="filesystem"]', doc)
print sets
for i in range(len(sets)):
    print sets[i]
    cs=ComCopyset.getCopyset(sets[i], doc)
    cs.doCopy()
    print("NOW DO THE UNDO")
    cs.undoCopy()