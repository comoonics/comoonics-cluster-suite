"""Comoonics lvm module
Module to reflect LVM functions in python.
"""

import os
import math
import xml.dom
from xml.dom import Node

from comoonics import ComSystem
from comoonics.ComDataObject import DataObject
from comoonics import ComLog
from comoonics.ComExceptions import ComException

CMD_LVM="/usr/sbin/lvm"

class LinuxVolumeManager(DataObject):
   """Internal Exception classes
   """
   class LVMException(ComException): pass
   class LVMCommandException(ComSystem.ExecLocalException): pass
   class LVMAlreadyExistsException(LVMException):pass
   class LVMNotExistsException(LVMException):pass

   '''
   Baseclass for all LVM Objects. Shares attributes and methods for all subclasses
   '''

   __logStrLevel__ = "comoonics.LVM"
   log=ComLog.getLogger(__logStrLevel__)
   TAGNAME="linuxvolumemanager"
   LVM_ROOT = "/etc/lvm"
   CMD_LVM="lvm"

   ''' Static methods '''

   def lvm(command, *params):
      """
      Executes the lvm command @command with given parameters as list.
      @returns: returns the output of the command as string if successful.
      """
      try:
         _command="%s %s %s" %(LinuxVolumeManager.CMD_LVM, command, " ".join(params))
         return ComSystem.execLocalOutput(_command, True, "%s")
      except ComSystem.ExecLocalException, el:
         raise LinuxVolumeManager.LVMCommandException(el.cmd, el.rc, el.out, el.err)

   lvm=staticmethod(lvm)

   def lvmarray(command, *params):
      """
      Executes the lvm command @command with given parameters as list.
      @returns: returns the output of the command as list if successful.
      """
      try:
         _command="%s %s %s" %(LinuxVolumeManager.CMD_LVM, command, " ".join(params))
         return ComSystem.execLocalOutput(_command, False, "%s")
      except ComSystem.ExecLocalException, el:
         raise LinuxVolumeManager.LVMCommandException(el.cmd, el.rc, el.out, el.err)

   lvmarray=staticmethod(lvmarray)

   def has_lvm():
      '''
      Just checks if lvm functionality is available.
      Returns true or raises an exception (RuntimeException)
      '''
      if ComSystem.isSimulate():
         return 1
      CMD_LVM="/usr/sbin/lvm"
      if not (os.access(CMD_LVM, os.X_OK) or
         os.access("/sbin/lvm", os.X_OK)):
         raise RuntimeError("LVM binaries do not seam to be available")

      if not (os.access(CMD_LVM, os.X_OK)) and (os.access("/sbin/lvm", os.X_OK)):
         CMD_LVM="/sbin/lvm"

      try:
         _cachedir=LinuxVolumeManager.lvm("dumpconfig", "devices/cache_dir")
         _cachedir.strip()
      except LinuxVolumeManager.LVMCommandException:
         if not ComSystem.isSimulate() and not os.access("/etc/lvm/.cache", os.R_OK) and not os.access("/etc/lvm/cache/.cache", os.R_OK):
            raise RuntimeError("LVM could not read lvm cache file")

      f = open("/proc/devices", "r")
      lines = f.readlines()
      f.close()

      for line in lines:
         try:
            (dev, name) = line[:-1].split(' ', 2)
         except:
            continue
         if name == "device-mapper":
            __lvmDevicePresent__ = 1
            break

      if __lvmDevicePresent__ == 0:
         raise RuntimeError("LVM Functionality does not seam to be available")
      return 1

   has_lvm=staticmethod(has_lvm)

   def vglist(doc=None):
      '''
      Returns a list of Volumegroup classes found on this system
      '''
      LinuxVolumeManager.has_lvm()

      if not doc:
         doc=xml.dom.getDOMImplementation().createDocument(None, None, None)

      vgs = {}
      out=LinuxVolumeManager.lvmarray('vgdisplay', "-C" "--noheadings", "--units b", "--nosuffix", "--separator :", " --options vg_name,pv_name")

      for line in out:
         try:
            (vgname, pvname) = line.strip().split(':')
         except:
            continue
         if not vgname or vgname=="":
            continue
         LinuxVolumeManager.log.debug("vg %s, pv %s" %(vgname, pvname))
         if vgs.has_key(vgname):
            vg=vgs[vgname]
         else:
            vg=VolumeGroup(vgname, doc)
            vgs[vgname]=vg
         vg.init_from_disk()
         pv= PhysicalVolume(pvname, vg, doc)
         pv.init_from_disk()
         vg.addPhysicalVolume(pv)
         for lv in LinuxVolumeManager.lvlist(vg):
            vg.addLogicalVolume(lv)
      return vgs.values()

   vglist=staticmethod(vglist)

   def lvlist(vg, doc=None):
      LinuxVolumeManager.has_lvm()

      if not doc:
         doc=xml.dom.getDOMImplementation().createDocument(None, None, None)

      lvs = []
      # field names for "options" are in LVM2.2.01.01/lib/report/columns.h
      rv = LinuxVolumeManager.lvmarray('lvdisplay', '-C', '--noheadings', '--units b', '--nosuffix', '--separator :', '--options vg_name,lv_name', str(vg.getAttribute("name")))
      for line in rv:
         try:
            (vgname, lv) = line.strip().split(':')
         except:
            continue

         if not vg:
            vg=VolumeGroup(vgname, doc)

         LinuxVolumeManager.log.debug(u"%s, %s" %(vg.getAttribute("name"), lv))
         logmsg = u'lv is %s/%s' % (vg.getAttribute("name"), lv)
         LinuxVolumeManager.log.debug(logmsg)
         lv=LogicalVolume(lv, vg, doc)
         lv.init_from_disk()
         lvs.append( lv )

      return lvs

   lvlist=staticmethod(lvlist)

   def pvlist(vg=None, doc=None, pvname=None):
      '''
      Returns a list of phyicalvolumes found on this system
      '''
      LinuxVolumeManager.has_lvm()

      if not doc:
         doc=xml.dom.getDOMImplementation().createDocument(None, None, None)

      pipe=""
      if vg:
         pipe=" | grep %s" % str(vg.getAttribute("name"))
      if pvname:
         pipe=" "+pvname
      pvs= []
      rv = LinuxVolumeManager.lvmarray('pvdisplay', '-C', '--noheadings', '--units b', '--nosuffix', '--separator :', '--options pv_name,vg_name', pipe)
      for line in rv:
         try:
            (dev, vgname) = line.strip().split(':')
         except:
            continue
         LinuxVolumeManager.log.debug("pv is %s in vg %s" %(dev, vgname))
         vg=VolumeGroup(vgname, doc)
         pv=PhysicalVolume(dev, vg, doc)
         vg.addPhysicalVolume(pv)
         pv.init_from_disk()
         pvs.append( pv )

      return pvs

   pvlist=staticmethod(pvlist)

   def getPossiblePhysicalExtents(floor=0):
      """Returns a list of integers representing the possible values for
         the physical extent of a volume group.  Value is in KB.

         floor - size (in KB) of smallest PE we care about.
      """

      possiblePE = []
      curpe = 8
      while curpe <= 16384*1024:
         if curpe >= floor:
            possiblePE.append(curpe)
         curpe = curpe * 2

      return possiblePE

   getPossiblePhysicalExtents=staticmethod(getPossiblePhysicalExtents)

   def clampLVSizeRequest(size, pe, roundup=0):
      """Given a size and a PE, returns the actual size of logical volumne.

      size - size (in MB) of logical volume request
      pe   - PE size (in KB)
      roundup - round sizes up or not
      """

      if roundup:
         func = math.ceil
      else:
         func = math.floor
      return (long(func((size*1024L)/pe))*pe)/1024

   clampLVSizeRequest=staticmethod(clampLVSizeRequest)

   def clampPVSize(pvsize, pesize):
      """Given a PV size and a PE, returns the usable space of the PV.
      Takes into account both overhead of the physical volume and 'clamping'
      to the PE size.

      pvsize - size (in MB) of PV request
      pesize - PE size (in KB)
      """

      # we want Kbytes as a float for our math
      pvsize *= 1024.0
      return long((math.floor(pvsize / pesize) * pesize) / 1024)

   clampPVSize=staticmethod(clampPVSize)

   def getMaxLVSize(pe):
      """Given a PE size in KB, returns maximum size (in MB) of a logical volume.

      pe - PE size in KB
      """
      return pe*64

   getMaxLVSize=staticmethod(getMaxLVSize)

   # Public methods
   def __init__(self, *params):
      if len(params) == 2:
         DataObject.__init__(self, params[0], params[1])
      else:
         raise IndexError('Index out of range for LinuxVolumeManager constructor (%u)' % len(params))
      self.ondisk=False

   # Methods shared by all subclasses (mostly abstract)
   def checkAttribute(self, attribute, position):
      attr=self.getAttribute("attrs", "")
      self.log.debug("checkAttribute(%s, %u)==%s"%(attribute, position, str(self.getAttribute("attrs", ""))))
      if len(attr)>position and attr[position]==attribute:
         return True
      else:
         return False

   def create(self): pass

   def remove(self): pass

   def rename(self, newname): pass

   def resize(self, newsize): pass

class LogicalVolume(LinuxVolumeManager):
   '''
   Representation of the Linux Volume Manager Logical Volume
   '''

   class LVMInvalidLVPathException(LinuxVolumeManager.LVMException): pass

   ATTRIB_ACTIVATED="a"
   ATTRIB_ACTIVATED_POS=4
   TAGNAME="logicalvolume"
   parentvg=None
   DEV_PATH="/dev"
   MAPPER_PATH=DEV_PATH+"/mapper"

   LVPATH_SPLIT_PATTERNS=["^%s/([^-]+)-([^/-]+)$" %(MAPPER_PATH), "^%s/([^/]+)/([^/]+)$" %(DEV_PATH)]

   # static methods
   def isValidLVPath(path, doc=None):
      """
      returns True if this path is a valid path to a logical volume and if that volume either activated or not exists.
      Supported paths are /dev/mapper/<vg_name>-<lv_name> or /dev/<vg_name>/<lv_name>.
      """
      try:
         (vgname, lvname)=LogicalVolume.splitLVPath(path)
         if not doc:
            doc=xml.dom.getDOMImplementation().createDocument(None, None, None)
         vg=VolumeGroup(vgname, doc)
         vg.init_from_disk()
         lv=LogicalVolume(lvname, vg, doc)
         lv.init_from_disk()
         return True
      except LinuxVolumeManager.LVMCommandException:
         return False
      except LinuxVolumeManager.LVMException:
#         ComLog.debugTraceLog(LogicalVolume.log)
         return False
      except RuntimeError:
         # If any command fails BZ #72
         ComLog.debugTraceLog(LogicalVolume.log)
         return False
   isValidLVPath=staticmethod(isValidLVPath)

   def splitLVPath(path):
      """
      just splits the given path in vgname and lvname. Returns (vgname, lvname) or raises an LVMException.
      """
      import re
      match=None
      for pattern in LogicalVolume.LVPATH_SPLIT_PATTERNS:
         match=re.match(pattern, path)
         if match and match.group(1) != "mapper":
            return match.groups()
      raise LogicalVolume.LVMInvalidLVPathException("Path %s is not a valid LVM Path" %(path))

   splitLVPath=staticmethod(splitLVPath)

   def __init__(self, *params):
      '''
      Constructor

      __init__(devicename, doc=None)
      __init__(element, parent_vg, doc=None)
      __init__(name, parent_vg, doc=None)
      '''
      name=None
      if len(params)==2 or (isinstance(params[0], basestring) and LogicalVolume.isValidLVPath(params[0]) and len(params)==1):
         doc = doc=xml.dom.getDOMImplementation().createDocument(None, None, None)
      elif len(params) == 3:
         doc = params[2]

      if isinstance(params[0], basestring) and LogicalVolume.isValidLVPath(params[0]):
         (vgname, name)=LogicalVolume.splitLVPath(params[0])
         parent_vg=VolumeGroup(vgname)
      elif len(params)==2:
         parent_vg=params[1]
      if len(params) >= 2 and isinstance(params[0], Node):
         element=params[0]
         LinuxVolumeManager.__init__(self, element, doc)
      elif len(params) >=2 or name:
         if not name:
            name=params[0]
         LinuxVolumeManager.__init__(self, doc.createElement(LogicalVolume.TAGNAME), doc)
         self.setAttribute("name", name)
      else:
         raise IndexError('Index out of range for Logical Volume constructor (%u)' % len(params))
      self.parentvg=parent_vg
      try:
         LinuxVolumeManager.lvm('lvdisplay', '-C', '--noheadings', '--units b', '--nosuffix', '--separator :', str(self.parentvg.getAttribute("name"))+"/"+str(self.getAttribute("name")))
         self.ondisk=True
      except LinuxVolumeManager.LVMCommandException:
         pass

   # The LVM methods
   def isActivated(self):
      return self.checkAttribute(self.ATTRIB_ACTIVATED, self.ATTRIB_ACTIVATED_POS)

   def init_from_disk(self):
      """
      Initializes this logical volume from disk and reads all attributes and sets them
      """
      LinuxVolumeManager.has_lvm()

      try:
         rv=LinuxVolumeManager.lvmarray('lvdisplay', '-C', '--noheadings', '--units b', '--nosuffix', '--separator : ', str(self.parentvg.getAttribute("name"))+"/"+str(self.getAttribute("name")))
         self.ondisk=False
         #FIXME
         # an exception should be thrown, if lvdisplay output has changed the syntax.
         # do we really need the for loop ?
         for line in rv:
            try:
               (attrs, size, origin) = line.strip().split(':')[2:5]
               self.setAttribute("attrs", attrs)
               self.setAttribute("size", long(math.floor(long(size) / (1024 * 1024))))
               self.setAttribute("origin", origin)
            except:
               #FIXME
               # this should be fixed to get an exception if the values cannot be parsed.
               continue

         if not ComSystem.isSimulate():
            self.ondisk=True
      except LinuxVolumeManager.LVMCommandException:
         pass

   def create(self):
      """
      Newly creates the logical volume
      """
      LinuxVolumeManager.has_lvm()
      size=""

      if self.ondisk and self.getAttribute("overwrite", "false") == "true":
         self.remove()

      try:
         self.init_from_disk()
      except:
         pass

      if self.ondisk:
         raise LinuxVolumeManager.LVMAlreadyExistsException(self.__class__.__name__+"("+str(self.getAttribute("name"))+")")
      try:
         size=self.getAttribute("size")
         if int(self.getAttribute("size")) > int(self.parentvg.getAttribute("free")):
            ComLog.getLogger(self.__logStrLevel__).warn("Requested LV size %s is too big taking free %s" % (self.getAttribute("size"), self.parentvg.getAttribute("free")))
            self.setAttribute("size", self.parentvg.getAttribute("free"))
            size=self.getAttribute("size")
      except NameError:
         if ComSystem.isSimulate():
            size="1000"
         else:
            size=self.parentvg.getAttribute("free")
      LinuxVolumeManager.lvm('lvcreate', '-L %sM' %size, '-n %s' %str(self.getAttribute("name")), '%s' %str(self.parentvg.getAttribute("name")))
      self.init_from_disk()
      if ComSystem.isSimulate():
         self.ondisk=True

   def remove(self):
      """
      Removes an existing physical volume
      """
      LinuxVolumeManager.has_lvm()
      if not self.ondisk:
         raise LinuxVolumeManager.LVMNotExistsException(self.__class__.__name__+"("+str(self.getAttribute("name"))+")"+"("+str(self.getAttribute("name"))+")")
      LinuxVolumeManager.lvm('lvremove', '-f', '%s/%s' % (str(self.parentvg.getAttribute("name")), str(self.getAttribute("name"))))
      self.ondisk=False

   def rename(self, newname):
      """
      Renames this logical volume
      """
      LinuxVolumeManager.has_lvm()
      if not self.ondisk:
         raise LinuxVolumeManager.LVMNotExistsException(self.__class__.__name__+"("+str(self.getAttribute("name"))+")")
      LinuxVolumeManager.lvm('lvrename', '%s %s %s' % (str(self.parentvg.getAttribute("name")), str(self.getAttribute("name")), newname))
      self.init_from_disk()

   def resize(self, newsize=None):
      """
      Resizes this Logical volume

      newsize - is the newsize of the logical volume. If not defined the rest of the volumegroup will be used
      """
      LinuxVolumeManager.has_lvm()
      if not self.ondisk:
         raise LinuxVolumeManager.LVMNotExistsException(self.__class__.__name__+"("+str(self.getAttribute("name"))+")")
      if not newsize:
         newsize="+"+self.parentvg.getAttribute("free")
      LinuxVolumeManager.lvm('lvresize', '-L %sM', '%s/%s' % (newsize, str(self.parentvg.getAttribute("name")), str(self.getAttribute("name"))))
      self.init_from_disk()

class PhysicalVolume(LinuxVolumeManager):
   '''
   Representation of the Linux Volume Manager Physical Volume
   '''

   TAGNAME="physicalvolume"
   parentvg=""

   # static methods
   def isPV(path, with_vg=True):
      """
      returns True if this path is a physial volume (if with_vg: and has a VG on it).
      """
      try:
         out=LinuxVolumeManager.lvmarray("pvs", '--noheadings --options pv_name,vg_name --separator=: ', path, ' 2>/dev/null')
         for line in out:
            line=line.split(":")
            if len(line)==2:
               if with_vg and line[1] != "":
                  return True
               elif not with_vg:
                  return True 
      except:
         pass
      return False

   isPV=staticmethod(isPV)

   def __init__(self, *params):
      '''
      Constructor

      __init__(element, parent_vg, doc=None)
      __init__(name, parent_vg, doc=None)
      __init__(name, doc=None)
      '''
      _parent_vg=None
      if (len(params) == 2 or len(params) == 3) and isinstance(params[0], Node) and isinstance(params[1], VolumeGroup):
         if len(params) == 2:
            _doc=xml.dom.getDOMImplementation().createDocument(None, None, None)
         else:
            _doc=params[2]
         _element=params[0]
         _parent_vg=params[1]
         LinuxVolumeManager.__init__(self, _element, _doc)
      elif len(params) <= 3 and isinstance(params[0], basestring):
         if (len(params) == 2 and isinstance(params[1], VolumeGroup)) or len(params) == 1:
            _doc=xml.dom.getDOMImplementation().createDocument(None, None, None)
         elif len(params) == 2:
            _doc=params[1]
         elif len(params) == 3:
            _doc=params[2]
         if len(params) >1 and isinstance(params[1], VolumeGroup):
            _parent_vg=params[1]
         _name=params[0]
         
         LinuxVolumeManager.__init__(self, _doc.createElement(self.TAGNAME), _doc)
         self.setAttribute("name", _name)
      elif len(params)<1 or len(params)>3:
         raise IndexError('Index out of range for Logical Volume constructor (%u)' % len(params))
      else:
         raise TypeError("Unsupported type for constructor %s" % type(params[0]))
      if not _parent_vg:
         self.parentvg=_parent_vg 
      try:
         LinuxVolumeManager.lvm('pvdisplay', '-C', '--noheadings', '--units b', '--nosuffix', '--separator : ', str(self.getAttribute("name")))
         self.ondisk=True
      except LinuxVolumeManager.LVMCommandException:
         pass

   '''
   The LVM methods
   '''

   def resolveName(self):
      """
      Will automatically try to detect the specified device. Implicitly the same functionality as in
      HostDisk.resolve() is used.
      """
      from comoonics.storage.ComDevice import Device
      device=Device(self.getAttribute("name"), self.getDocument())
      cmds=device.resolveDeviceName()
      self.log.debug("resolveName: setting name from %s => %s." %(str(self.getAttribute("name")), str(device.getDeviceName())))
      self.setAttribute("name", device.getDeviceName())
      return cmds

   def init_from_disk(self):
      """
      Initializes this physical volume from disk and reads all attributes and sets them
      """
      LinuxVolumeManager.has_lvm()

      self.ondisk=False
      rv=LinuxVolumeManager.lvmarray('pvdisplay', '-C', '--noheadings', '--units b', '--nosuffix', '--separator :', str(self.getAttribute("name")))

      for line in rv:
         try:
            (pvname, vgname, format, attr, size, free) = line.strip().split(':')
            self.setAttribute("format", format)
            self.setAttribute("attr", attr)
            self.setAttribute("size", long(math.floor(long(size) / (1024 * 1024))))
            self.setAttribute("free", long(math.floor(long(free) / (1024 * 1024))))
         except:
            continue
         if not self.parentvg and vgname:
            self.parentvg=VolumeGroup(vgname, self)
            self.parentvg.init_from_disk()
      if not ComSystem.isSimulate():
         self.ondisk=True

   def create(self):
      """
      Newly creates the physical volume
      """
      LinuxVolumeManager.has_lvm()
      if self.ondisk and self.getAttribute("overwrite", "false") == "true":
         for lv in self.parentvg.lvs:
            lv.delete()
         self.parentvg.remove()
         self.remove()

      try:
         self.init_from_disk()
      except:
         pass

      if self.ondisk:
         raise LinuxVolumeManager.LVMAlreadyExistsException(self.__class__.__name__+"("+str(self.getAttribute("name"))+")")
      LinuxVolumeManager.lvm('pvcreate', '-f', '-v', '-y', str(self.getAttribute("name")))
      self.init_from_disk()
      if ComSystem.isSimulate():
         self.ondisk=True

   def remove(self):
      """
      Removes an existing physical volume
      """
      LinuxVolumeManager.has_lvm()
      if not self.ondisk:
         raise LinuxVolumeManager.LVMNotExistsException(self.__class__.__name__+"("+str(self.getAttribute("name"))+")")
      LinuxVolumeManager.lvm('pvremove', '-ff ', str(self.getAttribute("name")))
      self.ondisk=False

   def rename(self, newname):
      """
      Renames this physical volume
      """
      pass

   def resize(self, ignore=None):
      """
      Resizes this Physical volume
      HANDLE WITH CARE: I don't now if pvresize is actually implemented

      newname is ignored because of pvresize gets its size automatically from the underlying device
      """
      LinuxVolumeManager.has_lvm()
      if not self.ondisk:
         raise LinuxVolumeManager.LVMNotExistsException(self.__class__.__name__+"("+str(self.getAttribute("name"))+")")
      LinuxVolumeManager.lvm('pvresize ', str(self.getAttribute("name")))

class VolumeGroup(LinuxVolumeManager):
   '''
   Representation of the Linux Volumen Manager Volume Group
   '''

   ATTRIB_CLUSTERED="c"
   ATTRIB_CLUSTERED_POS=5
   TAGNAME="volumegroup"
   pvs=dict()
   lvs=dict()

   '''
   Static methods
   '''

   def scan():
      """
      Runs vgscan.
      """

      LinuxVolumeManager.has_lvm()
      LinuxVolumeManager.lvm('vgscan', '-v')

   scan=staticmethod(scan)

   '''
   Public methods
   '''

   def __init__(self, *params):
      '''
      Constructor

      Valid Constructors are:
      __init__(element, doc=None)
      __init__(name, _pv=None, doc=None)
      '''
  
      self.pvs=dict()
      self.lvs=dict()
      
      if (len(params) == 1) or (len(params)==2 and isinstance(params[1], PhysicalVolume)):
         doc = doc=xml.dom.getDOMImplementation().createDocument(None, None, None)
      elif (len(params) == 2) and not isinstance(params[1], PhysicalVolume):
         doc = params[1]
      else:
         raise IndexError("Index out of range for Volume Group constructor (%u)" % len(params))
         
      if isinstance(params[0], Node):
         self.log.debug("createing volumegroup %s/%s from element" % (params[0].tagName, str(params[0].getAttribute("name"))))
         LinuxVolumeManager.__init__(self, params[0], params[1])
         # init all lvs
         __lvs=self.getElement().getElementsByTagName(LogicalVolume.TAGNAME)
         for i in range(len(__lvs)):
            self.addLogicalVolume(LogicalVolume(__lvs[i], self, doc))
         # init all pvs
         __pvs=self.getElement().getElementsByTagName(PhysicalVolume.TAGNAME)
         for i in range(len(__pvs)):
            self.addPhysicalVolume(PhysicalVolume(__pvs[i], self, doc))
      elif isinstance(params[0], basestring):
         self.log.debug("createing volumegroup %s from new element" % params[0])
         LinuxVolumeManager.__init__(self, doc.createElement(self.TAGNAME), doc)
         self.setAttribute("name", params[0])
         if len(params) > 1 and isinstance(params[1], PhysicalVolume):
            self.addPhysicalVolume(params[1])
      else:
         raise TypeError("Unsupported type for constructor %s" % type(params[0]))
      try:
         LinuxVolumeManager.lvm('pvscan', ' | grep "[[:blank:]]%s[[:blank:]]"' % str(self.getAttribute("name")))
         if not ComSystem.isSimulate():
            self.ondisk=True
      except LinuxVolumeManager.LVMCommandException:
         pass

   def __str__(self):
      '''
      Return all attributes of element to string
      '''
      str=LinuxVolumeManager.__str__(self)
#      for i in range(len(self.getElement().attributes)):
#         str+="%s = %s, " % (self.getElement().attributes.item(i).name, self.getElement().attributes.item(i).value)
      #str+="\n"
#      str+="pvs:\n"
#      for pv in self.getPhysicalVolumes():
#         str+="%s" % pv
#      #str+="\n"
#      str+="lvs:\n"
#      for lv in self.getLogicalVolumes():
#         str+="%s" % lv
      return str

   def isClustered(self):
      return self.checkAttribute(self.ATTRIB_CLUSTERED, self.ATTRIB_CLUSTERED_POS)

   def getLogicalVolumes(self):
      return self.lvs.values()

   def getLogicalVolumeMap(self):
      return self.lvs

   def getLogicalVolume(self, name):
      return self.lvs[name]

   def hasLogicalVolume(self, name):
      return self.lvs.has_key(name)

   def addLogicalVolume(self, lv):
      """
      Adds a logical volume to this volume group
      """
      self.lvs[lv.getAttribute("name")] = lv
      self.getElement().appendChild(lv.getElement())
      lv.parentvg=self

   def delLogicalVolume(self, lv):
      """
      Removes a logical volume from this group
      """
      self.getElement().removeChild(lv.getElement())
      del self.lvs[lv.getAttribute("name")]

   def getPhysicalVolumes(self):
      return self.pvs.values()

   def getPhysicalVolumeMap(self):
      return self.pvs

   def getPhysicalVolume(self, name):
      return self.pvs[name]

   def hasPhysicalVolume(self, name):
      return self.pvs.has_key(name)


   def addPhysicalVolume(self, pv):
      """
      Adds a physical volume to this volume group
      """
      self.pvs[pv.getAttribute("name")] = pv
      self.getElement().appendChild(pv.getElement())
      pv.parentvg=self

   def delPhysicalVolume(self, pv):
      """
      Removes a physical volume from this group
      """
      self.getElement().removeChild(pv.getElement())
      del self.pvs[pv.getAttribute("name")]

   def init_from_disk(self):
      """
      Initializes this volume group from disk and reads all attributes and sets them
      """
      LinuxVolumeManager.has_lvm()
      self.ondisk=False

      rv=LinuxVolumeManager.lvmarray('vgdisplay', '-C', '--noheadings', '--units b', '--nosuffix', '--separator : ', str(self.getAttribute("name")))

      for line in rv:
         try:
            (vgname, numpvs, numlvs, serial, attrs, size, free) = line.strip().split(':')
            if vgname == self.getAttribute("name"):
               self.setAttribute("numpvs", numpvs)
               self.setAttribute("numlvs", numlvs)
               self.setAttribute("serial", serial)
               self.setAttribute("attrs", attrs)
               self.setAttribute("size", str(long(math.floor(long(size) / (1024 * 1024)))))
               self.setAttribute("free", long(math.floor(long(free) / (1024 * 1024))))
         except:
            continue
      if not ComSystem.isSimulate():
         self.ondisk=True

   def activate(self):
      """
      Activate volume groups by running vgchange -ay.
      """

      LinuxVolumeManager.has_lvm()
      LinuxVolumeManager.lvm('vgchange', '-ay', str(self.getAttribute("name")))
      LinuxVolumeManager.lvm(' vgmknodes '+str(self.getAttribute("name")))

   def deactivate(self):
      """
      Deactivate volume groups by running vgchange -an.
      """

      LinuxVolumeManager.has_lvm()
      LinuxVolumeManager.lvm('vgchange', '-an ', str(self.getAttribute("name")))

   def clustered(self):
      """
      Set clusteredflag to yes by vgchange -cy.
      """

      LinuxVolumeManager.has_lvm()
      LinuxVolumeManager.lvm('vgchange', '-cy ', str(self.getAttribute("name")))

   def notclustered(self):
      """
      Unset clusteredflag to yes by vgchange -cn.
      """

      LinuxVolumeManager.has_lvm()
      LinuxVolumeManager.lvm('vgchange', '-cn', str(self.getAttribute("name")))

   def create(self):
      """
      Creates this volumegroup
      """

      LinuxVolumeManager.has_lvm()

      if self.ondisk and self.getAttribute("overwrite", "false") == "true":
         for lv in self.lvs:
            lv.remove()
         self.remove()

      try:
         self.init_from_disk()
      except:
         pass

      if self.ondisk:
         raise LinuxVolumeManager.LVMAlreadyExistsException(self.__class__.__name__+"("+str(self.getAttribute("name"))+")")
      _cmdoptions=list()
      try:
         _cmdoptions.append("--physicalextentsize %sk" % self.getAttribute("pe_size"))
      except:
         pass

      if self.isClustered():
         _cmdoptions.append("--clustered y")
      else:
         _cmdoptions.append("--clustered n")
      LinuxVolumeManager.lvm('vgcreate', '%s %s %s' % (" ".join(_cmdoptions), str(self.getAttribute("name")), ' '.join(self.getPhysicalVolumeMap().keys())))
      self.init_from_disk()
      if ComSystem.isSimulate():
         self.ondisk=True

   def remove(self):
      """Removes a volume group.  Deactivates the volume group first
      """

      LinuxVolumeManager.has_lvm()
      # we'll try to deactivate... if it fails, we'll probably fail on
      # the removal too... but it's worth a shot
      if not self.ondisk:
         raise LinuxVolumeManager.LVMNotExistsException(self.__class__.__name__+"("+str(self.getAttribute("name"))+")")
      self.deactivate()

      LinuxVolumeManager.lvm('vgremove ', str(self.getAttribute("name")))
      self.ondisk=False

   def rename(self, newname):
      """
      Renames this volumegroup
      """

      LinuxVolumeManager.has_lvm()
      if not self.ondisk:
         raise LinuxVolumeManager.LVMNotExistsException(self.__class__.__name__+"("+str(self.getAttribute("name"))+")")
      LinuxVolumeManager.lvm('vgrename '+str(self.getAttribute("name"))+" "+newname)

   def resize(self, newpvs):
      """
      Resizes this volumegroup

      newpvs: must be an array of type PhysicalVolume
      """
      LinuxVolumeManager.has_lvm()
      if not self.ondisk:
         raise LinuxVolumeManager.LVMNotExistsException(self.__class__.__name__+"("+str(self.getAttribute("name"))+")")
      LinuxVolumeManager.lvm('vgextend '+str(self.getAttribute("name"))+" "+newpvs)
