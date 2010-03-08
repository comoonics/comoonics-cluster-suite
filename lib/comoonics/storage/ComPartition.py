"""Comoonics partition module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComPartition.py,v 1.3 2010-03-08 12:30:48 marc Exp $
#

#import parted
import re

from xml.dom import Node
from xml import xpath

from ComParted import PartedHelper

from comoonics.ComDataObject import DataObject
from comoonics import ComLog
from comoonics.ComExceptions import ComException

__version__ = "$Revision: 1.3 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/ComPartition.py,v $

class Partition(DataObject):
    TAGNAME="partition"

    __logStrLevel__ = "Partition"


    PARTITION_TYPES={"primary":   0,  # parted.PARTITION_PRIMARY, \
                     "logical":   1,  # parted.PARTITION_LOGICAL, \
                     "extended":  2,  #parted.PARTITION_EXTENDED, \
                     "freespace": 4,  #parted.PARTITION_FREESPACE, \
                     "metadata":  8,  #parted.PARTITION_METADATA, \
                     "protected":16 } #parted.PARTITION_PROTECTED}


    def __init__(self, *args):
        if len(args) !=2:
            raise RuntimeError("2 Arguments required")
        if not isinstance(args[1], Node):
            raise RuntimeError("1. Argument must be a xml.dom.Document")
        doc=args[1]
        if isinstance(args[0], Node):
            element=args[0]
        else:
            element=self.__create_element_from_parted(args[0], doc)

        DataObject.__init__(self, element, doc)

    def __create_element_from_parted(self, part, doc):
        element=doc.createElement(self.TAGNAME)
        phelper=PartedHelper()
        # name
        element.setAttribute("name", str(part.num))
        #type
        element.setAttribute("type", self.__name_of_part_type(part.type))
        #size
        element.setAttribute("size", str(phelper.getPartSize(part)))
        #start
        #element.setAttribute("start", str(part.geom.start))
        #end
        #element.setAttribute("end", str(part.geom.end))
        #all flags
        for flag in phelper.get_flags_as_string(part):
            felem=PartitionFlag(doc.createElement("flag"), doc)
            felem.setAttribute("name", flag)
            element.appendChild(felem.getElement())
        return element


    def __name_of_part_type(self, _type):
        for t in self.PARTITION_TYPES.iteritems():
            if t[1]==_type:
                return t[0]
        return None

    def __type_of_part_name(self, name):
        return Partition.PARTITION_TYPES.get(name)

    def getType(self):
        return self.getAttribute("type")

    def getPartedType(self):
        return self.PARTITION_TYPES.get(self.getType())

    def getPartedSizeOptimum(self, dev):
        sectors=self.getPartedSize(dev)
        if sectors == 0: return 0
        # now round up
        phelper=PartedHelper()
        cyls=phelper.end_sector_to_cyl(dev, sectors)
        sectors=phelper.end_cyl_to_sector(dev, cyls)
        return sectors

    def getPartedSize(self, dev):
        """ returns always size in sectors """
        size=self.getAttribute("size")
        # calculate new size
        # FIXME Round up to next cylinder
        # Test Megabyte e.g. size="200M"
        res=re.search("([0-9]+)M", size)
        if res:
            sectors=int(res.group(1)) * 1024 * 1024 / dev.sector_size
            ComLog.getLogger(self.__logStrLevel__). \
                debug("found size in Megabytes : %s -> %s sectors" % (res.group(1), sectors))
            return sectors

        # Test Gigabyte e.g. size="200G"
        res=re.search("([0-9]+)G", size)
        if res:
            sectors = int(res.group(1)) * 1024 * 1024 * 1024 / dev.sector_size
            ComLog.getLogger(self.__logStrLevel__). \
                debug("found size in Gigabytes : %s -> %s sectors" %(res.group(1), sectors))
            return sectors

        # Test Percentage
        res=re.search("([0-9]+)%", size)
        if res:
            sectors=int(float(float(res.group(1)) / 100 * dev.heads * dev.cylinders * dev.sectors))
            ComLog.getLogger(self.__logStrLevel__). \
                debug("found size in %% : %s -> %s sectors" %( res.group(1), sectors))
            return sectors

        # Test REMAIN
        res=re.search("REMAIN", size)
        if res:
            ComLog.getLogger(self.__logStrLevel__).debug("found size in Tag :REMAIN")
            return 0

        # Test sectors
        res=re.search("[0-9]+", size)
        if res:
            ComLog.getLogger(self.__logStrLevel__).debug("found size in Tag :%s " % size)
            return int(size)

        raise ComException("size %s not supported" % size)

    def getPartedFlags(self):
        flags = []
        for flag in self.getFlags():
            flags.append(flag.getFlagPartedNum())
        return flags

    def getFlags(self):
        flags=[]
        elems = self.element.getElementsByTagName(PartitionFlag.TAGNAME)
        for elem in elems:
            flags.append(PartitionFlag(elem, self.document))
        return flags

    def hasFlag(self, name):
        try:
            return len(xpath.Evaluate('flag/@name='+name, self.element))
        except Exception:
            return False

    def setFlag(self, name):
        if self.hasFlag(name):
            return True
        flag=PartitionFlag(self.getDocument().createElement("flag"), self.getDocument())
        flag.setAttribute("name", name)
        self.appendChild(flag)

    def removeFlag(self, name):
        try:
            node=xpath.Evaluate('flag/@name='+name, self.element)[0]
            self.element.removeChild(node)
        except Exception:
            raise ComException("no flag with name %s found" %name)


class PartitionFlag(DataObject):
    TAGNAME="flag"
    ALLFLAGS={"boot":   1, # parted.PARTITION_BOOT, \
              "root":   2, #parted.PARTITION_ROOT, \
              "swap":   3, #parted.PARTITION_SWAP, \
              "hidden": 4, #parted.PARTITION_HIDDEN, \
              "raid":   5, #parted.PARTITION_RAID, \
              "lvm":    6, #parted.PARTITION_LVM, \
              "lba":    7 } # parted.PARTITION_LBA}

    def __init__(self, element, doc):
        DataObject.__init__(self, element, doc)

    def getAllFlags(self):
        return PartitionFlag.ALLFLAGS.keys()

    def getFlagName(self):
        return self.getAttribute("name")

    def getFlagPartedNum(self):
        return self.ALLFLAGS.get(self.getFlagName())