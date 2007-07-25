"""Comoonics scsi module

API for working with scsi and linux

"""


# here is some internal information
# $Id: ComSCSI.py,v 1.3 2007-07-25 11:35:26 marc Exp $
#


__version__ = "$Revision: 1.3 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/scsi/ComSCSI.py,v $

from comoonics import ComLog
from comoonics.ComExceptions import ComException

import os
import os.path
import re
from comoonics import ComSystem

log=ComLog.getLogger("comoonics.scsi.ComSCSI")

class SCSIException(ComException):
    def __str__(self):
        return "SCSI-Error: %s" %(self.value)

FCPATH_2_HOST="/sys/class/fc_host"
FCPATH_TRANSPORT="/sys/class/fc_transport"
FCPATH_TRANSPORT_TARGET=FCPATH_TRANSPORT+"/target:%u:%u:%u"
FCPATH_TRANSPORT_TARGET_NODENAME=FCPATH_TRANSPORT_TARGET+"/node_name"
FCPATH_HOST_DEVICE=FCPATH_2_HOST+"/%s/device"
FCPATH_HOST_TARGET=FCPATH_2_HOST+"/target:%u:%u:%u"
FCPATH_HOST_LUN=FCPATH_HOST_TARGET+"/%u:%u:%u:%u"
SCSIPATH_2_PROC="/proc/scsi"
QLA_SCSIPATH_PROC="%s/qla2xxx" %(SCSIPATH_2_PROC)
SCSIPATH_2_PROC_SCSI="%s/scsi" %(SCSIPATH_2_PROC)
SCSIPATH_2_HOST="/sys/class/scsi_host"
SCSISCAN_PATH=SCSIPATH_2_HOST+"/%s/scan"
SCSIDEVICE_PATH=SCSIPATH_2_HOST+"/%s/device"
SCSIPATH_2_DEVICE="/sys/class/scsi_device"
SCSIPATH_TARGET=SCSIPATH_2_DEVICE+"/%u:%u:%u:%u"
SCSIPATH_TARGET_BLOCK=SCSIPATH_TARGET+"/device/block"
SYSPATH_2_BLOCK="/sys/block"
SCSIID_CMD="/sbin/scsi_id"
SCSIID_CMD_GETUID=SCSIID_CMD+" -g -u -s "
FC_ISSUE_LIP_PATH=FCPATH_2_HOST+"/%s/issue_lip"
SCSISCAN_CMD="---"
SCSIDELETE_CMD="1"
FCLIP_CMD="1"
QLARESCAN_CMD="scsi-qlascan"

SCSIHOST_PATTERN="host(\d+)"
SCSITARGET_PATTERN=".*(\d+:\d+:\d+)"
SCSILUN_PATTERN="(\d+):(\d+):(\d+):(\d+)"
QLALUN_PATTERN="\(\s*(\d+):\s*(\d+)\): Total reqs \d+, Pending reqs \d+, flags 0x.*"
QLATARGET_PATTERN="^scsi-qla0-target-(%u)=(\w+);$"
QLAPORT_PATTERN="^scsi-qla(\d+)-port-(\d+)=(\w+):(\w+):(\d+):(\d+);$"

def rescan(host=None, add=True, remove=True):
    if not host:
        for host in getSCSIHosts():
            rescan(host)
    elif type(host)==list:
        for _host in host:
            rescan(_host)
    else:
        if os.path.isfile(SCSISCAN_PATH %(host)) and os.access(SCSISCAN_PATH %(host), os.W_OK):
            scan_filename=SCSISCAN_PATH %(host)
            log.debug("rescan(%s)" %(scan_filename))
            if isFibreChannel(host):
                fcrescan(host)
            scan=open(scan_filename, "w")
            print >> scan, SCSISCAN_CMD
            try:
                scan.close()
            except:
                pass
            remove_dir=SCSIDEVICE_PATH %(host)
            if not os.path.isdir(remove_dir):
                raise SCSIException("sysfile for host %s does not exist or is not writable (%s)" %(host, remove_dir))
            for device_file in os.listdir(remove_dir):
                if re.match(SCSITARGET_PATTERN, device_file):
                    for lun_file in os.listdir(remove_dir+"/"+device_file):
                        lunmatch=re.match(SCSILUN_PATTERN, lun_file)
                        if lunmatch:
                            if remove:
                                scsi_remove_disk(host, remove_dir+"/"+device_file+"/"+lun_file)
                            if add:
                                try:
                                    scsi_add_disk(host, remove_dir+"/"+device_file, lunmatch.group(2), lunmatch.group(3), lunmatch.group(4))
                                except:
                                    scsi_add_disk_old(int(lunmatch.group(1)), int(lunmatch.group(2)), int(lunmatch.group(3)), int(lunmatch.group(4)))
        else:
            raise SCSIException("sysfile for host %s does not exist or is not writable (%s)" %(host, SCSISCAN_PATH %(host)))

def rescan_qla(host=None, add=True, remove=True, timeout=5):
    if not host:
        for host in getQlaHosts():
            rescan_qla(host)
    elif type(host)==list:
        for _host in host:
            rescan_qla(_host)
    elif os.path.isfile(SCSISCAN_PATH %(host)) and os.access(SCSISCAN_PATH %(host), os.W_OK):
        qlarescan(host)
        import time
        log.debug("rescan_qla: wait(%u)" %(timeout))
        time.sleep(timeout)
        qlarescan_disks(host, add, remove)
    else:
        raise SCSIException("sysfile for host %s does not exist or is not writable (%s)" %(host, SCSISCAN_PATH %(host)))

def getSCSIHosts():
    return getHostsForPath(SCSIPATH_2_HOST)

def getFCHosts():
    return getHostsForPath(FCPATH_2_HOST)
def getQlaHosts():
    hosts=list()
    for host in getHostsForPath(SCSIPATH_2_HOST):
        if isQlaHost(host):
            hosts.append(host)
    return hosts

def getHostsForPath(path, pattern=SCSIHOST_PATTERN):
    hosts=list()
    if os.path.isdir(path):
        for host in os.listdir(path):
            log.debug("getHostsForPath "+ host)
            if re.match(pattern, host):
                hosts.append(host)
        return hosts
    else:
        raise SCSIException("No Hosts detected in %s." %(SCSIPATH_2_HOST))

def fcrescan(host):
    scan_filename=FC_ISSUE_LIP_PATH %(host)
    if os.path.isfile(scan_filename) and os.access(scan_filename, os.W_OK):
        log.debug("fcrescan(%s)" %(scan_filename))
        scan=open(scan_filename, "w")
        print >> scan, FCLIP_CMD
        try:
            scan.close()
        except:
            pass
        if isQlaHost(host):
            qlarescan(host)
    else:
        log.warn("issulipfile does not exist or is not writable (%s)" %(scan_filename))

def getHostId(host):
    regexp=re.match(SCSIHOST_PATTERN, host)
    if regexp:
        return int(regexp.group(1))
    else:
        return None

def qlarescan(host):
    hostid=getHostId(host)
    if hostid!=None:
        path="%s/%u" %(QLA_SCSIPATH_PROC, hostid)
        if os.path.isfile(path) and os.access(path, os.W_OK):
            scan=open(path, "w")
            log.debug("%s>%s" %(QLARESCAN_CMD, path))
            print >>scan, QLARESCAN_CMD
            try:
                scan.close()
            except:
                pass

    else:
        raise SCSIException("Invalid Hostid %s" %(host))

def qlarescan_disks(host, add=True, remove=True):
    hostid=getHostId(host)
    if hostid!=None:
        qlafile="%s/%u" %(QLA_SCSIPATH_PROC, hostid)
        if os.access(qlafile, os.W_OK) and os.access(SCSIPATH_2_PROC_SCSI, os.W_OK):
            qla=open(qlafile, "r")
            regexp=re.compile(QLALUN_PATTERN)
            busid=0
            for line in qla:
#                log.debug(line)
                match=regexp.match(line)
                if match:
                    targetid=int(match.group(1))
                    lunid=int(match.group(2))
                    if remove:
                        scsi_remove_disk_old(hostid, busid, targetid, lunid)
                    if add:
                        scsi_add_disk_old(hostid, busid, targetid, lunid)


def isQlaHost(host):
    hostid=getHostId(host)
    return os.path.isfile("%s/%u" %(QLA_SCSIPATH_PROC, hostid))

def isFibreChannel(host):
    scan_filename=FC_ISSUE_LIP_PATH %(host)
    return os.path.isfile(scan_filename)

def scsi_remove_disk_old(hostid, busid, targetid, targetlun):
    # only supported for qlogic hbas
    scsi_old_cmd("scsi remove-single-device %u %u %u %u" %(hostid, busid, targetid, targetlun))

def scsi_add_disk_old(hostid, busid, targetid, targetlun):
    # only supported for qlogic hbas
    scsi_old_cmd("scsi add-single-device %u %u %u %u" %(hostid, busid, targetid, targetlun))

def scsi_old_cmd(cmd):
    log.debug(cmd)
    filename=SCSIPATH_2_PROC_SCSI
    scsi=open(filename, "w")
    print >>scsi, cmd
    try:
        scsi.close()
    except:
        pass


def scsi_remove_disk(host, disk_path):
    target=False
    if os.path.isdir(disk_path) and os.access(disk_path, os.W_OK):
        log.debug("scsi_remove_disk(%s/delete)" %(disk_path))
        remove=open(disk_path+"/delete", "w")
        print >> remove, SCSIDELETE_CMD
        target=True
        try:
            remove.close()
        except:
            pass
    else:
        raise SCSIException("sysfile for host %s does not exist or is not writable (%s)" %(host, disk_path))
    return target

def scsi_add_disk(host, target_path, busid, targetid, lunid):
    target=False
    log.debug("Adding target: %s/%s" %(host, target_path))
    if os.path.isdir(target_path) and os.access(target_path, os.W_OK):
        log.debug("scsi_add_disk(%s/delete)" %(target_path))
        add=open(target_path, "w")
        print >> add, "%s %s %s" %(busid, targetid, lunid)
        try:
            add.close()
        except:
            pass
    else:
        raise SCSIException("sysfile for host %s does not exist or is not writable (%s)" %(host, target_path))
    return target

def getWWWN(scsi_hostid, scsi_busid, scsi_id):
    filename=FCPATH_TRANSPORT_TARGET_NODENAME %(int(scsi_hostid), int(scsi_busid), int(scsi_id))
    qlafile=QLA_SCSIPATH_PROC+"/%u" %(int(scsi_hostid))
    if os.path.exists(filename):
        nodenamef=open(filename, "r")
        nodename=nodenamef.readlines()[0]
        nodename=nodename[2:-1]
        nodenamef.close()
    elif os.path.exists(qlafile):
        qla=open(qlafile, "r")
        regexp_target=re.compile(QLATARGET_PATTERN %(int(scsi_id)))
        regexp_port=re.compile(QLAPORT_PATTERN)
        wwpn=None
        nodename=None
        for line in qla:
            match=regexp_target.match(line)
            if match:
                wwpn=match.group(2)
                log.debug("wwpn: %s" %(wwpn))
            if not match:
                match=regexp_port.match(line)
                if match:
                    log.debug("match: %s, %s" %(match.group(3), match.group(4)))
                if wwpn and match and match.group(4)==wwpn:
                    nodename=match.group(3)
        qla.close()
    else:
        raise SCSIException("Could not find or read/write either old or new scsipath. Is driver loaded?")
    if nodename and nodename != "":
        return nodename
    else:
        raise SCSIException("Could not find wwwn for scsitarget %u:%u:%u" %(int(scsi_hostid), int(scsi_busid), int(scsi_id)))

def getBlockDeviceForUID(uid):
    """ Returns the block devicefile for the given uid """
    if os.path.exists(SCSIPATH_2_DEVICE):
        for target in os.listdir(SCSIPATH_2_DEVICE):
            try:
                blockdev_path=SCSIPATH_2_DEVICE+"/"+target+"/device/block"
                if os.path.exists(blockdev_path):
                    blockdev=os.path.basename(os.readlink(blockdev_path))
                    _uid=ComSystem.execLocalOutput(SCSIID_CMD_GETUID+"/block/"+blockdev)[0].splitlines()[0]
                    log.debug("getBlockDeviceForUID(): %s == %s" %(uid, _uid))
                    if _uid==uid:
                        return "/dev/"+blockdev
            except:
                ComLog.debugTraceLog(log)
                pass

    else:
        raise SCSIException("Syspath %s does not exist. Old Linux or no Linux or no sys mounted??" %(SYSPATH_2_BLOCK))

def getBlockDeviceForWWWNLun(wwwn, lun, hosts=None):
    """ returns the scsidevicename of wwwn, lun combination searching on all hosts or the given ones. """
    blockdev_file=None
    if not hosts:
        try:
            hosts=getFCHosts()
        except SCSIException:
            ComLog.debugTraceLog(log)
            hosts=getQlaHosts()

    for host in hosts:
        device_dir=FCPATH_HOST_DEVICE %(host)
        if os.path.isdir(device_dir):
            for device_file in os.listdir(device_dir):
                match=re.match(SCSITARGET_PATTERN, device_file)
                if match:
                    (scsi_hostid, scsi_busid, scsi_id)=match.groups()
                    _wwwn=getWWWN(scsi_hostid, scsi_busid, scsi_id)
                    log.debug("Found WWWN: %s==%s" %(_wwwn, wwwn))
                    if _wwwn==wwwn:
                        blockdev_file=FCPATH_HOST_LUN %(host, int(scsi_hostid), int(scsi_busid), int(scsi_id), int(scsi_hostid), int(scsi_busid), int(scsi_id), int(lun))
                        blockdev_file+="/block"

        hostid=getHostId(host)
        busid=0
        qlafile=QLA_SCSIPATH_PROC+"/%u" %(int(hostid))
        if os.path.exists(qlafile):
            qla=open(qlafile, "r")
            regexp_lun=re.compile(QLALUN_PATTERN)
            regexp_port=re.compile(QLAPORT_PATTERN)
            nodename=None
            scsi_ids=list()
            for line in qla:
                match=regexp_port.match(line)
                if match:
                    (scsi_hostid, scsi_id, wwpn, wwnn, _x, _y)=match.groups()
                    log.debug("match: %s, %s, %s" %(wwpn, wwnn, scsi_id))
                    if wwnn==wwwn or wwpn==wwwn:
                        scsi_ids.append(int(scsi_id))
                if not match:
                    match=regexp_lun.match(line)
                    if match:
                        (scsi_id, scsi_lun)=match.groups()
                        if int(scsi_id) in scsi_ids and int(scsi_lun) == int(lun):
                            blockdev_file=SCSIPATH_TARGET_BLOCK %(int(hostid), int(busid), int(scsi_id), int(scsi_lun))
            qla.close()

    if blockdev_file and os.path.exists(blockdev_file):
        log.debug("blockdevfile: %s" %(blockdev_file))
        if os.path.exists(blockdev_file):
            return "/dev/"+os.path.basename(os.readlink(blockdev_file))
    else:
        raise SCSIException("Could not find blockdevice for wwwn: %s, lun: %u" %(wwwn, int(lun)))

def test():
    __line("Testing scsihosts")
    print getSCSIHosts()
    __line("Testing fchosts")
    print getFCHosts()

    __line("scsirescaning fchosts")
    for host in getFCHosts():
        rescan(host)

def __line(str):
    print "--------------------------- %s ---------------------------------------" %(str)

if __name__=="__main__":
    test()

###########################
# $Log: ComSCSI.py,v $
# Revision 1.3  2007-07-25 11:35:26  marc
# -loglevel
#
# Revision 1.2  2007/04/04 12:32:44  marc
# MMG Backup Legato Integration :
# - added timeout after rescan
#
# Revision 1.1  2007/03/26 08:04:58  marc
# initial revision
#
