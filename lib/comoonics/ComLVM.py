"""Comoonics lvm module
here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id $
#


__version__ = "$Revision: 1.11 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/Attic/ComLVM.py,v $

import os
import string
from exceptions import RuntimeError, IndexError, TypeError
import math
import xml.dom
from xml.dom import Element, Node

import ComSystem
from ComDataObject import DataObject
import ComLog
from ComExceptions import ComException

CMD_LVM="/usr/sbin/lvm"

class LinuxVolumeManager(DataObject):
    """Internal Exception classes
    """
    class LVMException(ComException): pass
    class LVMAlreadyExistsException(LVMException):pass
    class LVMNotExistsException(LVMException):pass

    '''
    Baseclass for all LVM Objects. Shares attributes and methods for all subclasses
    '''

    __logStrLevel__ = "comoonics.LVM"
    log=ComLog.getLogger(__logStrLevel__)
    TAGNAME="linuxvolumemanager"
    LVM_ROOT = "/etc/lvm"

    ''' Static methods '''

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

        if not os.access("/etc/lvm/.cache", os.R_OK) and not os.access("/etc/lvm/cache/.cache", os.R_OK):
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
        (rc, rv, stderr) = ComSystem.execLocalGetResult(CMD_LVM+' vgdisplay -C --noheadings --units b --nosuffix --separator : --options vg_name,pv_name', True)
        if rc >> 8 != 0:
            raise RuntimeError("running vgdisplay failed: %u, %s, %s" % (rc,rv, stderr))

        for line in rv:
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
        (rc, rv, stderr) = ComSystem.execLocalGetResult(CMD_LVM+' lvdisplay -C --noheadings --units b --nosuffix --separator : --options vg_name,lv_name '+str(vg.getAttribute("name")), True)
        if rc >> 8 != 0:
            raise RuntimeError("running lvdisplay failed: %u, %s, %s" % (rc,rv, stderr))

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

    def pvlist(vg=None, doc=None):
        '''
        Returns a list of phyicalvolumes found on this system
        '''
        LinuxVolumeManager.has_lvm()

        if not doc:
            doc=xml.dom.getDOMImplementation().createDocument(None, None, None)

        pipe=""
        if vg:
            pipe=" | grep %s" % str(vg.getAttribute("name"))
        pvs= []
        (rc, rv, stderr) = ComSystem.execLocalGetResult(CMD_LVM+' pvdisplay -C --noheadings --units b --nosuffix --separator : --options pv_name,vg_name'+pipe, True)
        if rc >> 8 != 0:
            raise RuntimeError("running vgdisplay failed: %u, %s, %s" % (rc,rv, stderr))

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

    # FIXME: this is a hack.  we really need to have a --force option.
    def unlinkConf():
        if os.path.exists("%s/lvm.conf" %(LinuxVolumeManager.LVM_ROOT,)):
            os.unlink("%s/lvm.conf" %(LinuxVolumeManager.LVM_ROOT,))

    unlinkConf=staticmethod(unlinkConf)

    def writeForceConf():
        """Write out an /etc/lvm/lvm.conf that doesn't do much (any?) filtering"""

        try:
            os.unlink("%s/.cache" % LinuxVolumeManager.LVM_ROOT)
        except:
            pass
        if not os.path.isdir(LinuxVolumeManager.LVM_ROOT):
            os.mkdir(LinuxVolumeManager.LVM_ROOT)

        LinuxVolumeManager.unlinkConf()

        f = open("%s/lvm.conf" %(LinuxVolumeManager.LVM_ROOT,), "w+")
        f.write("""
# anaconda hacked lvm.conf to avoid filtering breaking things
devices {
  sysfs_scan = 0
  md_component_detection = 1
}
""")
        return

    writeForceConf=staticmethod(writeForceConf)

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

    '''
    Public methods
    '''
    def __init__(self, *params):
        if len(params) == 2:
            DataObject.__init__(self, params[0], params[1])
        else:
            raise IndexError('Index out of range for LinuxVolumeManager constructor (%u)' % len(params))
        self.ondisk=False

    '''
    Methods shared by all subclasses (mostly abstract)
    '''
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

    """
    static methods
    """
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
        except LinuxVolumeManager.LVMException:
            ComLog.debugTraceLog(LogicalVolume.log)
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
        for pattern in LogicalVolume.LVPATH_SPLIT_PATTERNS:
            match=re.match(pattern, path)
            if match:
                return match.groups()
        raise LogicalVolume.LVMInvalidLVPathException("Path %s is not a valid LVM Path" %(path))

    splitLVPath=staticmethod(splitLVPath)

    def __init__(self, *params):
        '''
        Constructor

        __init__(element, parent_vg, doc=None)
        __init__(name, parent_vg, doc=None)
        '''
        if len(params)==2:
            doc = doc=xml.dom.getDOMImplementation().createDocument(None, None, None)
        elif len(params) == 3:
            doc = params[2]

        parent_vg=params[1]
        if len(params) >= 2 and isinstance(params[0], Node):
            element=params[0]
            LinuxVolumeManager.__init__(self, element, doc)
        elif len(params) >=2:
            name=params[0]
            LinuxVolumeManager.__init__(self, doc.createElement(LogicalVolume.TAGNAME), doc)
            self.setAttribute("name", name)
        else:
            raise IndexError('Index out of range for Logical Volume constructor (%u)' % len(params))
        self.parentvg=parent_vg
        (rc, rv, stderr) = ComSystem.execLocalGetResult(CMD_LVM+' lvdisplay -C --noheadings --units b --nosuffix --separator : '+str(self.parentvg.getAttribute("name"))+"/"+str(self.getAttribute("name")), True)
        if rc >> 8 == 0 and not ComSystem.isSimulate():
            self.ondisk=True

    '''
    The LVM methods
    '''
    def isActivated(self):
        return self.checkAttribute(self.ATTRIB_ACTIVATED, self.ATTRIB_ACTIVATED_POS)

    def init_from_disk(self):
        """
        Initializes this logical volume from disk and reads all attributes and sets them
        """
        LinuxVolumeManager.has_lvm()

        (rc, rv, stderr) = ComSystem.execLocalGetResult(CMD_LVM+' lvdisplay -C --noheadings --units b --nosuffix --separator : '+str(self.parentvg.getAttribute("name"))+"/"+str(self.getAttribute("name")), True)
        if rc >> 8 != 0 or not ComSystem.isSimulate():
            self.ondisk=False
            raise RuntimeError("running lvdisplay of %s failed: %u, %s, %s" % (str(self.parentvg.getAttribute("name"))+"/"+str(self.getAttribute("name")), rc,rv, stderr))

        for line in rv:
            try:
                (lvname, vgname, attrs, size, origin, snap, move, log, copy) = line.strip().split(':')
                self.setAttribute("attrs", attrs)
                self.setAttribute("size", long(math.floor(long(size) / (1024 * 1024))))
                self.setAttribute("origin", origin)
            except:
                continue

        if not ComSystem.isSimulate():
            self.ondisk=True

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
        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' lvcreate -L %sM -n %s %s' %(size, str(self.getAttribute("name")), str(self.parentvg.getAttribute("name"))))
        if rc >> 8 != 0:
            raise RuntimeError("running lvcreate on %s/%s failed: %u,%s" % (str(self.parentvg.getAttribute("name")), str(self.getAttribute("name")),rc >> 8, rv))
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
        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' lvremove -f %s/%s' % (str(self.parentvg.getAttribute("name")), str(self.getAttribute("name"))))
        if rc >> 8 != 0:
            raise RuntimeError("running lvremove on %s/%s failed: %u,%s" % (str(self.parentvg.getAttribute("name")), str(self.getAttribute("name")),rc >> 8, rv))
        self.ondisk=False

    def rename(self, newname):
        """
        Renames this logical volume
        """
        LinuxVolumeManager.has_lvm()
        if not self.ondisk:
            raise LinuxVolumeManager.LVMNotExistsException(self.__class__.__name__+"("+str(self.getAttribute("name"))+")")
        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' lvrename %s %s %s' % (str(self.parentvg.getAttribute("name")), str(self.getAttribute("name")), newname))
        if rc >> 8 != 0:
            raise RuntimeError("running lvrename on %s/%s failed: %u,%s" % (self.parentvg.getAttribute("name"), self.getAttribute("name"),rc >> 8, rv))
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
        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' lvresize -L %sM %s/%s' % (newsize, str(self.parentvg.getAttribute("name")), str(self.getAttribute("name"))))
        if rc >> 8 != 0:
            raise RuntimeError("running lvresize on %s/%s newsize %sM failed: %u,%s" % (str(self.parentvg.getAttribute("name")), newsize, str(self.getAttribute("name")),rc >> 8, rv))
        self.init_from_disk()

class PhysicalVolume(LinuxVolumeManager):
    '''
    Representation of the Linux Volume Manager Physical Volume
    '''

    TAGNAME="physicalvolume"
    parentvg=""

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
            _element=params[0]
            _parent_vg=params[1]
            LinuxVolumeManager.__init__(self, _element, _doc)
        elif len(params) <= 3 and isinstance(params[0], basestring):
            if (len(params) == 2 and isinstance(params[1], VolumeGroup)) or len(params) == 1:
                _doc=xml.dom.getDOMImplementation().createDocument(None, None, None)
            elif len(params) == 2:
                _doc=params[1]
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
        (rc, rv, stderr) = ComSystem.execLocalGetResult(CMD_LVM+' pvdisplay -C --noheadings --units b --nosuffix --separator : '+str(self.getAttribute("name")), True)
        if rc >> 8 == 0 and not ComSystem.isSimulate():
            self.ondisk=True

    '''
    The LVM methods
    '''

    def resolveName(self):
        """
        Will automatically try to detect the specified device. Implicitly the same functionality as in
        HostDisk.resolve() is used.
        """
        from comoonics.ComDevice import Device
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

        (rc, rv, stderr) = ComSystem.execLocalGetResult(CMD_LVM+' pvdisplay -C --noheadings --units b --nosuffix --separator : '+str(self.getAttribute("name")), True)
        if rc >> 8 != 0:
            self.ondisk=False
            raise RuntimeError("running pvdisplay failed: %u, %s, %s" % (rc,rv,stderr))

        for line in rv:
            try:
                (pvname, vgname, format, attr, size, free) = line.strip().split(':')
                self.setAttribute("format", format)
                self.setAttribute("attr", attr)
                self.setAttribute("size", long(math.floor(long(size) / (1024 * 1024))))
                self.setAttribute("free", long(math.floor(long(free) / (1024 * 1024))))
            except:
                continue
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
        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' pvcreate -f -v -y '+str(self.getAttribute("name")))
        if rc >> 8 != 0:
            raise RuntimeError("running pvcreate on %s failed: %u,%s" % (str(self.getAttribute("name")),rc >> 8, rv))
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
        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' pvremove -ff '+str(self.getAttribute("name")))
        if rc >> 8 != 0:
            raise RuntimeError("running pvremove on %s failed: %u,%s" % (str(self.getAttribute("name")),rc >> 8, rv))
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
        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' pvresize '+str(self.getAttribute("name")))
        if rc >> 8 != 0:
            raise RuntimeError("running pvresize on %s failed: %u, $s" % (str(self.getAttribute("name")),rc >> 8, rv))

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

        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' vgscan -v')
        if rc >> 8 != 0:
            raise RuntimeError("running vgscan failed: "+ str(rc)+", ",rv)

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
        elif (len(params) == 2) and not isinstance(params[2], PhysicalVolume):
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
            self.addPhysicalVolume(params[1])
        else:
            raise TypeError("Unsupported type for constructor %s" % type(params[0]))
        (rc, rv, stderr) = ComSystem.execLocalGetResult(CMD_LVM+' pvscan | grep "[[:blank:]]%s[[:blank:]]"' % str(self.getAttribute("name")), True)
        if rc >> 8 == 0 and not ComSystem.isSimulate():
            self.ondisk=True

    def __str__(self):
        '''
        Return all attributes of element to string
        '''
        str=LinuxVolumeManager.__str__(self)
#        for i in range(len(self.getElement().attributes)):
#            str+="%s = %s, " % (self.getElement().attributes.item(i).name, self.getElement().attributes.item(i).value)
        #str+="\n"
#        str+="pvs:\n"
#        for pv in self.getPhysicalVolumes():
#            str+="%s" % pv
#        #str+="\n"
#        str+="lvs:\n"
#        for lv in self.getLogicalVolumes():
#            str+="%s" % lv
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

        (rc, rv, stderr) = ComSystem.execLocalGetResult(CMD_LVM+' vgdisplay -C --noheadings --units b --nosuffix --separator : '+str(self.getAttribute("name")), True)
        if rc >> 8 != 0:
            self.ondisk=False
            raise RuntimeError("running vgdisplay failed: %u, %s, %s" % (rc,rv, stderr))

        for line in rv:
            try:
                (vgname, numpvs, numlvs, serial, attrs, size, free) = line.strip().split(':')
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
        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' vgchange -ay '+str(self.getAttribute("name")))

        if rc >> 8 != 0:
            raise RuntimeError("running vgchange of %s failed: %u, %s" % (str(self.getAttribute("name")), rc >> 8, rv))

        # now make the device nodes
        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' vgmknodes '+str(self.getAttribute("name")))
        if rc >> 8 != 0:
            raise RuntimeError("running vgmknodes failed: %u, %s" % (rc, rv))

    def deactivate(self):
        """
        Deactivate volume groups by running vgchange -an.
        """

        LinuxVolumeManager.has_lvm()
        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' vgchange -an '+str(self.getAttribute("name")))

        if rc >> 8 != 0:
            raise RuntimeError("running vgchange of %s failed: %u, %s" % (str(self.getAttribute("name")), rc >> 8, rv))

    def clustered(self):
        """
        Set clusteredflag to yes by vgchange -cy.
        """

        LinuxVolumeManager.has_lvm()
        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' vgchange -cy '+str(self.getAttribute("name")))

        if rc >> 8 != 0:
            raise RuntimeError("running vgchange of %s failed: %u, %s" % (str(self.getAttribute("name")), rc >> 8, rv))

    def notclustered(self):
        """
        Unset clusteredflag to yes by vgchange -cn.
        """

        LinuxVolumeManager.has_lvm()
        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' vgchange -cn '+str(self.getAttribute("name")))

        if rc >> 8 != 0:
            raise RuntimeError("running vgchange of %s failed: %u, %s" % (str(self.getAttribute("name")), rc >> 8, rv))

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
        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' vgcreate %s %s %s' % (" ".join(_cmdoptions), str(self.getAttribute("name")), ' '.join(self.getPhysicalVolumeMap().keys())))
        if rc >> 8 != 0:
            raise RuntimeError("running vgcreate on %s failed: %u,%s" % (str(self.getAttribute("name")),rc >> 8, rv))
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

        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' vgremove '+str(self.getAttribute("name")))
        if rc >> 8 != 0:
            raise RuntimeError("running vgremove on %s failed: %u, %s" % (str(self.getAttribute("name")),rc >> 8, rv))
        self.ondisk=False

    def rename(self, newname):
        """
        Renames this volumegroup
        """

        LinuxVolumeManager.has_lvm()
        if not self.ondisk:
            raise LinuxVolumeManager.LVMNotExistsException(self.__class__.__name__+"("+str(self.getAttribute("name"))+")")
        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' vgrename '+str(self.getAttribute("name"))+" "+newname)
        if rc >> 8 != 0:
            raise RuntimeError("running vgrename on %s failed: %s, %s" % (str(self.getAttribute("name")), rc >> 8, rv))

    def resize(self, newpvs):
        """
        Resizes this volumegroup

        newpvs: must be an array of type PhysicalVolume
        """
        LinuxVolumeManager.has_lvm()
        if not self.ondisk:
            raise LinuxVolumeManager.LVMNotExistsException(self.__class__.__name__+"("+str(self.getAttribute("name"))+")")
        (rc, rv) = ComSystem.execLocalStatusOutput(CMD_LVM+' vgextend '+str(self.getAttribute("name"))+" "+newpvs)
        if rc >> 8 != 0:
            raise RuntimeError("running vgresize on %s failed: %s, %s" % (str(self.getAttribute("name")), rc >> 8, rv))

def __line__(str):
    print "---------------------------------------%s-----------------------------" %(str)

def test():
    from logging import INFO
    ComLog.setLevel(INFO)
    ComSystem.setExecMode(ComSystem.SIMULATE)
    devicenames=["/dev/sda", "/dev/cciss/c0d0p1", "zipfl", "/dev/mapper/abc-def", "/dev/abc/def", "/dev/mapper/abc/def", "/dev/abc/def/geh" ]
    for device in devicenames:
        __line__("device="+device)
        try:
            (vgname, lvname)=LogicalVolume.splitLVPath(device)
            print "Found: vgname: %s, lvname: %s" %(vgname, lvname)
        except LogicalVolume.LVMInvalidLVPathException, e:
            print e.value

    __line__("Testing core functionality in simulation mode")
    try:
        vgs=LinuxVolumeManager.vglist()
        for _vg in vgs:
            print "Volume group: "
            print _vg
            for lv in _vg.getLogicalVolumes():
                print "Logical volume: ", lv

            for pv in _vg.getPhysicalVolumes():
                print "Physical volume: ", pv
    except RuntimeError, re:
        print re

    try:
        vgname="test_vg"
        lvname="test_lv"
        pvname="/dev/sda"
        __line__("Creating pv: %s" %pvname)
        _pv=PhysicalVolume(pvname)
        _pv.create()
        __line__("Creating vg: %s" %vgname)
        _vg=VolumeGroup(vgname, _pv)
        _vg.create()
        _vg.addPhysicalVolume(_pv)
        __line__("Creating lv: %s" %lvname)
        _lv=LogicalVolume(lvname, _vg)
        _lv.create()
        _vg.addLogicalVolume(_lv)
        
        print "Volumegroup %s: %s" %(vgname, _vg)
        
        __line__("Changing clustered")
        _vg.clustered()
        _vg.notclustered()
        
        __line__("Removing lv")
        _lv.remove()
        __line__("Removing vg")
        _vg.remove()
        __line__("Removing pv")
        _pv.remove()
    except Exception:
        ComLog.errorTraceLog()

if __name__=="__main__":
    test()

##################
# $Log: ComLVM.py,v $
# Revision 1.11  2008-02-27 10:41:47  marc
# - Fixed BZ#199 where creation of clustered volumegroups would yield problems with nodes not running the cluster
# - Support for simulation mode
#
# Revision 1.10  2008/02/27 09:14:14  mark
# enhanced support for doc=None like initialization
#
# Revision 1.9  2008/01/24 09:54:51  mark
# added lvm cache check for RHEL5. Solves BZ 188
#
# Revision 1.8  2007/08/22 14:13:40  marc
# Fixed Bug BZ#88 (clustered flad is created when there is none)
#
# Revision 1.7  2007/08/06 07:39:12  marc
# - fixed BZ#72; also catching RunTimeExceptions when isValidLVPath.
#
# Revision 1.6  2007/06/19 13:10:08  marc
# - fixed loglevel
# - fixed minor bugs with string formating
#
# Revision 1.5  2007/04/04 12:49:23  marc
# MMG Backup Legato Integration :
# - added resolveName for resolving PVs of devices
#
# Revision 1.4  2007/04/02 11:48:16  marc
# MMG Backup Legato Integration:
# - only logging
#
# Revision 1.3  2007/03/26 08:33:04  marc
# - added simple internal testing
# - added LVM attributes
# - changed logging
#
# Revision 1.2  2006/11/23 14:18:22  marc
# added feature that lvs can be selected when cloning
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.8  2006/07/04 11:01:22  marc
# changed handling errror output
#
# Revision 1.7  2006/07/03 16:10:20  marc
# self on disk and checks for creating of already existings pvs, vgs and lvs
#
# Revision 1.6  2006/07/03 12:48:13  marc
# added error detection
#
# Revision 1.5  2006/06/30 13:57:47  marc
# changed lvcreate to take free size if size is too big
#
# Revision 1.4  2006/06/30 08:27:41  marc
# removed autoactivation in create
#
# Revision 1.3  2006/06/29 13:47:28  marc
# stable version
#
# Revision 1.2  2006/06/28 17:26:12  marc
# first version
#
# Revision 1.1  2006/06/26 19:12:48  marc
# initial revision
#