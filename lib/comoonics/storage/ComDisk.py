"""Comoonics disk module


Module for disk abstraction layer.

"""

import os
import exceptions
import time
import xml.dom

from comoonics import ComSystem
from comoonics.ComDataObject import DataObject
from comoonics.ComExceptions import ComException
from comoonics import ComLog
from ComPartition import Partition
from ComLVM import LogicalVolume, VolumeGroup, PhysicalVolume, LinuxVolumeManager

CMD_SFDISK = "/sbin/sfdisk"
CMD_DD="/bin/dd"
CMD_DMSETUP = "/sbin/dmsetup"
CMD_KPARTX = "/sbin/kpartx"
DEVICEMAPPER_PART_DELIM="p"
OPTS_KPARTX = "-p %s" %DEVICEMAPPER_PART_DELIM


class Disk(DataObject):
   def __init__(self, element, doc=None):
      """ default Constructur """
      super(Disk, self).__init__(element, doc)

class StorageDisk(Disk):
   MAPPING_TAG_NAME="mapping"
   HOST_TAG_NAME="host"
   """ Disk represents a disk on a storage system """
   def __init__(self, element, doc=None):
      """ default constructur called by __new__ """
      super(StorageDisk, self).__init__(element, doc)
   def getHostNames(self, lun):
      """ returns all hostnames as list for the given lun """
      mappings=self.getElement().getElementsByTagName(self.MAPPING_TAG_NAME)
      if type(lun)==int:
         lun="%u" %(lun)
      hosts=list()
      for mapping in mappings:
         if mapping.getAttribute("lun")==lun:
            ehosts=mapping.getElementsByTagName(self.HOST_TAG_NAME)
            for ehost in ehosts:
               hosts.append(ehost.getAttribute("name"))
      return hosts

   def getLuns(self):
      """ returns all defined luns in this disk """
      luns=list()
      mappings=self.getElement().getElementsByTagName(self.MAPPING_TAG_NAME)
      for mapping in mappings:
         luns.append(mapping.getAttribute("lun"))
      return luns

class HostDisk(Disk):
   log=ComLog.getLogger("comoonics.ComDisk.HostDisk")
   LABEL_PREFIX="LABEL="
   TAGNAME="disk"
   class DeviceNameResolver(object):
      key=None
      def getKey(self):
         return self.key
      def resolve(self, value):
         pass

   class DeviceNameResolverError(ComException):
      pass
   resolver=dict()

   # static methods
   def map2realDMName(device, prefixpath="/dev/mapper"):
      """
      Maps the given devicemapper name to the real one (first created).
      Should be executed on every proper device mapper device.
      """
      if os.path.islink(device):
         # more recent versions of multipath will not use device files but symbolic links to the 
         # dm-* devices. Those links are relative and need therefore be converted to absolute 
         # paths.
         return os.path.realpath(os.path.join(os.path.dirname(device), os.readlink(device)))
      else:
         cmd="%s info -c --noheadings -o name %s" %(CMD_DMSETUP, device)
         try:
            return os.path.join(prefixpath, ComSystem.execLocalOutput(cmd, True, "")[:-1])
         except ComSystem.ExecLocalException:
            ComLog.debugTraceLog()
            return device
   map2realDMName=staticmethod(map2realDMName)

   def __init__(self, *params):
      """ Disk represents a raw disk
         Possible constructors:
         __init__(self, element, doc=None)  type(element)=Node
         __init__(self, name, doc=None) type(name)==str
      """
      if len(params)==1:
         doc=xml.dom.getDOMImplementation().createDocument(None, self.TAGNAME, None)
      elif len(params)==2:
         doc=params[1]
      else:
         raise exceptions.TypeError("""Wrong number of arguments to constructor of HostDisk.
   Either __init__(self, element, doc=None) or
        __init__(self, name, doc=None) are supported.""")

      if isinstance(params[0], basestring):
         element=doc.createElement(self.TAGNAME)
         element.setAttribute("name", params[0])
      else:
         element=params[0]
      super(HostDisk, self).__init__(element, doc)
      self.log.debug("__init__")
      self.devicename=None
      self.stabilizedfile="/proc/partitions"
      self.stabilizedtype="hash"
      self.stabilizedgood=2
      self.partitions=dict()

   def is_lvm(self):
      return hasattr(self, "volumegroup") and hasattr(self, "logicalvolume")

   def is_lvm_activated(self):
      return self.is_lvm() and self.logicalvolume.isActivated()

   def lvm_vg_activate(self):
      self.volumegroup.activate()

   def lvm_vg_deactivate(self):
      self.volumegroup.deactivate()

   def pv_deactivate(self, devicename=None):
      """
      Deactivates all vgs held by this disk (including partitions)
      @param devicename: if given only this device will be taken into account 
      """
      if not devicename:
         for devicename in self.getDeviceNames():
            self.pv_deactivate(devicename)

      if not PhysicalVolume.isPV(devicename):
         return
      pvs=LinuxVolumeManager.pvlist(pvname=devicename)
      for pv in pvs:
         if pv.parentvg:
            for lv in LinuxVolumeManager.lvlist(pv.parentvg):
               if lv.isActivated():
                  pv.parentvg.deactivate()
                  break

   def pv_activate(self, devicename=None):
      """
      Activates all vgs hold by this disk/or given device
      """
      if not devicename:
         for devicename in self.getDeviceNames():
            self.pv_activate(devicename)
      pvs=LinuxVolumeManager.pvlist(pvname=devicename)
      for pv in pvs:
         if pv.parentvg:
            for lv in LinuxVolumeManager.lvlist(pv.parentvg):
               if lv.isActivated():
                  pv.parentvg.deactivate()
                  break

   def getLog(self):
      return self.log

   def exists(self):
      return ComSystem.execMethod(os.path.exists, self.getDeviceName())

   def sameSize(self):
      """ 
      """
      return self.getAttributeBoolean("samesize", False)

   def getDeviceName(self):
      """ returns the Disks device name (e.g. /dev/sda) """
      if hasattr(self, "devicename") and self.devicename != None:
         return self.devicename
      else:
         return self.getAttribute("name")

   def getDevicePath(self):
      return self.getDeviceName()

   def getDeviceNames(self, notme=False):
      """ Returns a list of devicenames for this devices and all partitions.
      @param notme: do not include the disk devicename but only the paritions.
      """
      devicenames=list()
      basedevice=HostDisk.map2realDMName(self.getDeviceName())
      if not notme:
         devicenames.append(basedevice)
      self.initFromDisk()
      for part in self.partitions.keys():
         devicenames.append(basedevice+self.getPartitionDelim()+part)
      return devicenames
   
   def getPartitionDelim(self):
      if self.isDMMultipath():
         return DEVICEMAPPER_PART_DELIM
      else:
         return ""
      

   def getSize(self):
      """ returns the size of the disk in sectors"""
      pass

   def refByLabel(self):
      """
      is disk referenced by Label? returns True or False
      Format <disk name="LABEL=..."/>
      """
      return self.getDeviceName()[:len(self.LABEL_PREFIX)]==self.LABEL_PREFIX

   def resolveDeviceNameByKeyValue(self, key, value):
      """
      resolves a device name by searching for a method to resolve it by key and the resolve via value as
      Parameter
      """
      if self.resolver.has_key(key):
         name=self.resolver[key].resolve(value)
         if name and name != "":
            self.devicename=name
         else:
            raise HostDisk.DeviceNameResolverError("Could not resolve device \"%s\" for type \"%s\"" %(value, key))
      else:
         raise HostDisk.DeviceNameResolverError("Could not find resolver for device referrenced by %s=%s" %(key, value))

   def resolveDeviceName(self):
      """
      resolves the given devicenames and returns a list of commands to execute to get device operational.
      """
      journal_cmds=list()
      if len(self.getDeviceName().split("="))==2:
         (key, value)=self.getDeviceName().split("=")[:2]
         self.resolveDeviceNameByKeyValue(key, value)
      if LogicalVolume.isValidLVPath(self.getDeviceName()):
         lv=LogicalVolume(self.getDeviceName())
         lv.init_from_disk()
         self.initLVM()
         self.lvm_activated=False
         if self.getAttribute("options", "") != "skipactivate" and not self.is_lvm_activated():
            self.lvm_vg_activate()
            self.lvm_activated=True
            journal_cmds.append("lvm_vg_activate")
      elif self.getAttribute("options", "") != "skipdeactivate":
         devicenames=list()
         devicename=HostDisk.map2realDMName(self.getDeviceName())
         devicenames.append(devicename)
         self.initFromDisk()
         if self.isDMMultipath():
            partdelim=DEVICEMAPPER_PART_DELIM
         else:
            partdelim=""
         for partition in self.getAllPartitions():
            devicenames.append("%s%s%s" %(devicename, partdelim, partition.getAttribute("name")))
            for devicename in devicenames:
               if PhysicalVolume.isPV(devicename):
                  journal_cmds.append("pv_deactivate")
      return journal_cmds

   def initLVM(self):
      (vgname, lvname)=LogicalVolume.splitLVPath(self.getDeviceName())
      self.volumegroup=VolumeGroup(vgname, self.getDocument())
      self.logicalvolume=LogicalVolume(lvname, self.volumegroup, self.getDocument())
      self.volumegroup.init_from_disk()
      self.logicalvolume.init_from_disk()

   def initFromDisk(self):
      """ reads partition information from the disk and fills up DOM
      with new information
      """
      HostDisk.log.debug("initFromDisk()")

      #FIXME: create LabelResolver
      if self.refByLabel():
         pass
      if not self.exists():
         raise ComException("Device %s not found or no valid device!" % self.getDeviceName())
      import ComParted

      phelper=ComParted.getInstance()
      for partition in phelper.initFromDisk(self.getDeviceName()):
         self.addPartition(Partition(partition, self.getDocument()))
         
   def restore(self):
      if hasattr(self, "lvm_activated") and self.lvm_activated:
         self.lvm_vg_deactivate()

   def addPartition(self, part):
      """ adds a partition to the existing ones. Already existing ones will be overwritten """
      added=False
      self.partitions[part.getAttribute("name")]=part
      for epartition in self.getElement().getElementsByTagName(Partition.TAGNAME):
         if epartition.getAttribute("name") == part.getAttribute("name"):
            self.getElement().replaceChild(part.getElement(), epartition)
            added=True
      if not added:
         self.appendChild(part)
   
   def hasPartition(self, part):
      """ Returns true if partition (Partition object) exists as partion in this disk """
      return self.partitions[part.getAttribute("name")]
   
   def removePartition(self, part):
      """ Removes the given partition from the partitions """
      if self.hasPartition(part):
         del self.partitions[part.getAttribute("name")]
         for epartition in self.getElement().getElementsByTagName(Partition.TAGNAME):
            if epartition.getAttribute("name") == part.getAttribute("name"):
               self.getElement().removeChild(epartition)    

   def createPartitions(self):
      """ creates new partition table """
      if not self.exists():
         raise ComException("Device %s not found" % self.getDeviceName())
      import ComParted

      phelper=ComParted.getInstance()
      phelper.createPartitions(self.getDeviceName(), self.getAllPartitions(), self.sameSize())
      self.stabilize()

   def stabilize(self):
      self.commit()

      #dev.sync()
      #dev.close()

      # run partx if the device is a multipath device
      self.log.debug("ComHostDisk: checking for multipath devices")
      if self.isDMMultipath():
         devicename=HostDisk.map2realDMName(self.getDeviceName())
         self.log.debug("Device %s is a dm_multipath device, adding partitions" %devicename)
         __cmd=CMD_KPARTX + " " + OPTS_KPARTX +" -d " + devicename
         try:
            __ret = ComSystem.execLocalOutput(__cmd, True, "")
            self.log.debug(__ret)
            __cmd=CMD_KPARTX + " " + OPTS_KPARTX + " -a " + devicename
            __ret = ComSystem.execLocalOutput(__cmd, True, "")
            self.log.debug(__ret)
            #FIXME: crappy fix to give os some time to create devicefiles.
            time.sleep(10)
         except ComSystem.ExecLocalException, ele:
            ComLog.debugTraceLog(self.log)
            self.log.debug("Could not execute %s. Error %s" %(ele.cmd, ele))

   def isDMMultipath(self):
      if not os.path.exists(CMD_DMSETUP):
         return False
      __cmd="%s table %s --target=multipath 2>/dev/null | grep multipath &>/dev/null"  % (CMD_DMSETUP, self.getDeviceName())
      try:
         ComSystem.execLocalOutput(__cmd, True, "")
         return True
      except ComSystem.ExecLocalException: 
         return False

   def getAllPartitions(self):
      parts=[]
      for elem in self.element.getElementsByTagName(Partition.TAGNAME):
         parts.append(Partition(elem, self.document))
      return parts


   def savePartitionTable(self, filename):
      """ saves the Disks partition table in sfdisk format to <filename>
      Throws ComException on error
      """
      __cmd = self.getDumpStdout() + " > " + filename
      __ret = ComSystem.execLocalOutput(__cmd, True, "saved partition table")
      self.log.debug("savePartitionTable( " + filename + "):\n " + __ret)

   def getPartitionTable(self):
      try:
         rv = ComSystem.execLocalOutput(self.getDumpStdout(), True, "getPartitionTable")
         return rv
      except ComSystem.ExecLocalException:
         return list()

   def getDumpStdout(self):
      """ returns the command string for dumping partition information
      see sfdisk -d
      """
      return CMD_SFDISK + " -d " + self.getDeviceName()

   def hasPartitionTable(self):
      """ checks wether the disk has a partition table or not """
      #__cmd = CMD_SFDISK + " -Vq " + self.getDeviceName() + " >/dev/null 2>&1"
      #if ComSystem.execLocal(__cmd):
      #   return False
      #return True
      __cmd = CMD_SFDISK + " -l " + self.getDeviceName()
      rc, std, err = ComSystem.execLocalGetResult(__cmd, True)
      if rc!=0:
         return False
      if (" ".join(err).upper().find("ERROR")) > 0:
         return False
      return True



   def deletePartitionTable(self):
      """ deletes the partition table """
      __cmd = CMD_DD + " if=/dev/zero of=" + self.getDeviceName() + " bs=512 count=2 >/dev/null 2>&1"
      if ComSystem.execLocal(__cmd):
         return False
      return self.rereadPartitionTable()

   def rereadPartitionTable(self):
      """ rereads the partition table of a disk """
      __cmd = CMD_SFDISK + " -R " + self.getDeviceName() + " >/dev/null 2>&1"
      if ComSystem.execLocal(__cmd):
         self.commit()
         return False
      else:
         self.commit()
         return True

   def restorePartitionTable(self, filename):
      """ writes partition table stored in <filename> to Disk.
      Note, that the format has to be sfdisk stdin compatible
      see sfdisk -d
      Throws ComException on error
      """
      __cmd = self.getRestoreStdin(True) + " < " + filename
      __out = ComSystem.execLocalOutput(__cmd, True, "")
      self.log.debug("restorePartitionTable( " + filename + "):\n " + __out)
      self.commit()

   def getRestoreStdin(self, force=False):
      """ returns command string to restore a partition table
      config from sfdisk stdin
      see sfdisk < config
      """
      __cmd = [CMD_SFDISK]
      if force:
         __cmd.append("--force")
      __cmd.append(self.getDeviceName())
      return " ".join(__cmd)

   def commit(self):
      """ Method that waits for synchronized commits on underlying devices
      """
      try:
         from comoonics.tools import stabilized
         stabilized.stabilized(file=self.stabilizedfile, type=self.stabilizedtype, good=self.stabilizedgood)
      except ImportError:
         warnings.warn("Could not import a stabilization functionality to synchronized changed disk devices with depending kernel. You might think of installing comoonics-storage-py.")

# Initing the resolvers
try:
   from comoonics.scsi.ComSCSIResolver import SCSIWWIDResolver, FCTransportResolver
   res=SCSIWWIDResolver()
   HostDisk.resolver[res.getKey()]=res
   res=FCTransportResolver()
   HostDisk.resolver[res.getKey()]=res
except ImportError:
   import warnings
   warnings.warn("Could not import SCSIWWIDResolver and FCTransportResolver. Limited functionality for HostDisks might be available.")
