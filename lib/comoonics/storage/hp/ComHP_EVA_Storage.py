#!/usr/bin/python
"""
Python implementation of the Base Storage Interface to connect a modification or copyset to a storage implementation
"""

# here is some internal information
# $Id: ComHP_EVA_Storage.py,v 1.1 2007-02-09 11:36:16 marc Exp $
#

__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/hp/ComHP_EVA_Storage.py,v $

from comoonics.ComExceptions import ComException
from comoonics import ComLog
from comoonics.storage.hp.ComHP_EVA_SSSU import HP_EVA_SSSU, CommandError
from comoonics.storage.ComStorage import Storage, NotImplementedYet, ErrorDuringExecution
from comoonics.storage.hp.ComHP_EVA import HP_EVA_Object

class HP_EVA_Storage(Storage):
    __logStrLevel__ = "HP_EVA_Storage"
    """
    Baseclass for storagesystem implementations. All supported methods should be implemented. If not an exception is
    raised.
    """
    def __init__(self, **kwds):
        """ Default constructor does nothing here """
        super(HP_EVA_Storage, self).__init__(**kwds)
        (self.manager,self.system)=self.system.split("/")

        if not hasattr(self, "cmd"):
            self.cmd=HP_EVA_SSSU.SSSU_CMD
        if kwds.has_key("cmd"):
            self.cmd=kwds["cmd"]
        self.log=None
        if kwds.has_key("log"):
            self.log=kwds["log"]
        else:
            self.log='/tmp/ComHP_EVA_SSSU.log'
        self.cmdlog=None
        if kwds.has_key("cmdlog"):
            self.cmdlog=kwds["cmdlog"]
        else:
            self.cmdlog='/tmp/ComHP_EVA_SSSU_cmd.log'
        self.autoconnect=False
        if kwds.has_key("autoconnect"):
            self.autoconnect=kwds["autoconnect"]
            self.connect()
        self.sssu=None

    def getConnectionName(self):
        """ for singleton implementation if you want to have only one connection per storage system you can use
        this string as unique reference.
        Returns the self.system
        """
        return "%s-%s" %(self.system, self.manager)

    def isConnected(self):
        """ Returns True if this instance is already connected to the storagesystem or otherwise False.
        Default is False."""
        return self.sssu and self.sssu.connected()

    def connect(self):
        """ Connects to the storage system """
        if not self.isConnected():
            mylogger.debug("system: %s, manager: %s" %(self.system,self.manager))
            logfile=cmdlogfile=None
            if self.log:
                logfile = file(self.log, "w")
            if self.cmdlog:
                cmdlogfile = file(self.cmdlog, "w")
            self.sssu=HP_EVA_SSSU(self.manager, self.username, self.password, self.system, self.autoconnect, self.cmd, logfile, cmdlogfile)
            self.sssu.connect()

    def map_luns(self, disk, source=None):
        """ Lunmaps the given disk. Hosts and luns are integrated insite the disk and returns the luns if need be. """
        luns=list()
        for lun in disk.getLuns():
            for host in disk.getHostNames(lun):
                try:
                    self.sssu.cmd("add lun %s vdisk=\"%s\" host=\"%s\"" %(lun, disk.getAttribute("name"), host))
                    if host.count("/")>0:
                        self.sssu.cmd("ls lun \"%s/%s\" xml" %(host[:host.rindex("/")], lun))
                    else:
                        self.sssu.cmd("ls lun \"%s\" xml" %(lun))
                    lun=None
                    if self.sssu.xml_output:
                        lun=HP_EVA_Object.fromXML(self.sssu.xml_output)
                        luns.append(lun)
                except CommandError, ce:
                    raise ErrorDuringExecution("Could not add lun to storage\nExecution errorcode %u: \ncmd: %s" %(self.sssu.last_error_code, self.sssu.last_cmd), ce)
        return luns

    def unmap_luns(self, disk, source=None):
        """ Lunmaps the given disk. Hosts and luns are integrated insite the disk. """
        luns=list()
        for lun in disk.getLuns():
            for host in disk.getHostNames(lun):
                try:
                    if host.count("/")>0:
                        path="%/"%(host[:host.rindex("/")])
                    else:
                        path=""
                    if self.sssu.cmd("ls lun \"%s%s\" xml" %(path,lun))==0 and self.sssu.xml_output:
                        luns.append(HP_EVA_Object.fromXML(self.sssu.xml_output))
                    self.sssu.cmd("delete lun \"%s%s\"" %(path,lun))
                except CommandError, ce:
                    raise ErrorDuringExecution("Could not add lun to storage\nExecution errorcode %u: \ncmd: %s" %(self.sssu.last_error_code, self.sssu.last_cmd), ce)
        return luns

    def _delete(self, type, name, properties, checkfunc=None):
        try:
            vdisk=None
            if self.sssu.cmd("ls %s \"%s\" xml" %(type, name))==0 and self.sssu.xml_output:
                vdisk=HP_EVA_Object.fromXML(self.sssu.xml_output)
                mylogger.debug("deleting vdisk %s" %(vdisk.objectname))
                if isinstance(vdisk, HP_EVA_Object):
                    if not checkfunc or (checkfunc and checkfunc(vdisk)):
                        self.sssu.cmd("delete %s \"%s\"" %(type, name), properties)
                return vdisk
            else:
                raise ErrorDuringExecution("Could not delete %s %s from storage. %s %s does not exist" %(type, name, type, name))
        except CommandError, ce:
            raise ErrorDuringExecution("Could not delete %s %s to storage\nExecution errorcode %u: \ncmd: %s" %(type, name, self.sssu.last_error_code, self.sssu.last_cmd), ce)

    def _add(self, type, name, properties):
        try:
            mylogger.debug("add %s \"%s\" %s" %(type, name, properties))
            if self.sssu.cmd("add %s \"%s\"" %(type, name), properties)==0:
                if type=="vdisk":
                    self.sssu.cmd("ls %s \"%s/ACTIVE\" xml" %(type, name))
                else:
                    self.sssu.cmd("ls %s \"%s\" xml" %(type, name))
                vdisk=None
                if self.sssu.xml_output:
                    vdisk=HP_EVA_Object.fromXML(self.sssu.xml_output)
                return vdisk
            else:
                raise ErrorDuringExecution("Could not add %s %s to storage.\nExecution errorcode %u: \ncmd: %s, output: %s" %(type, name, self.sssu.last_error_code, self.sssu.last_cmd, self.sssu.last_output))
        except CommandError, ce:
            raise ErrorDuringExecution("Could not add %s %s to storage\nExecution errorcode %u: \ncmd: %s\noutput: %s" %(type, name, ce.errorcode, ce.cmd, ce.output))

    def add(self, disk, source=None):
        """ Adds the given disk. Parameters are packed as properties insite the disk. """
        return self._add("vdisk", disk.getAttribute("name"), disk.getProperties())

    def add_snapshot(self, destdisk, sourcedisk):
        """ Snapshots the given sourcedisk to destdisk. Options are packed as properties insite of destdisk."""
        properties=destdisk.getProperties()
        properties.setProperty("vdisk", sourcedisk.getAttribute("name"))
        return self._add("snapshot", destdisk.getAttribute("name"), properties)

    def add_clone(self, destdisk, sourcedisk):
        """ Clones the given sourcedisk to destdisk. Options are packed as properties insite of destdisk. """
        properties=destdisk.getProperties()
        properties["vdisk"]=sourcedisk.getAttribute("name")
        return self._add("snapshot", destdisk.getAttribute("name"), properties)

    def delete(self, disk, source=None):
        """ Deletes the given disk. If you only want to support the deleting of snapshots use delete_snaphot. """
        return self._delete("vdisk", disk.getAttribute("name"), disk.getProperties())

    def delete_snapshot(self, disk, source=None):
        """ Deletes the given disk only if its a snapshot. """
        return self._delete("snapshot", disk.getAttribute("name"), disk.getProperties(), self.isSnapshot)

    def delete_clone(self, disk, source=None):
        """ Deletes the given disk only if its a clone. """
        return self._delete("snapshot", disk.getAttribute("name"), disk.getProperties(), self.isClone)

    def close(self):
        """ Closes the connection """
        pass
        #self.sssu.disconnect()

    def isSnapshot(self, vdisk):
        """ Checks if the given vdisk is a snapshot """
        if vdisk.objecttype=="snapshot":
            return True
        else:
            return False
    def isClone(self, vdisk):
        """ Checks if the given vdisk is a clone """
        if vdisk.objecttype=="clone":
            return True
        else:
            return False

mylogger=ComLog.getLogger(HP_EVA_Storage.__logStrLevel__)

def main():
    from xml.dom.ext.reader import Sax2
    from comoonics.ComDisk import Disk
    reader=Sax2.Reader(validate=0)
    #mylogger.debug("xml: %s" %(match.group(1)))
    xml_dump="""
        <disk name="Virtual Disks/atix/sourcedisk">
            <properties>
                <property name="size" value="10"/>
                <property name="disk_group" value="146er"/>
            </properties>
        </disk>
"""
    doc=reader.fromString(xml_dump)
    disk=Disk(doc.documentElement, doc)
    for property in disk.getProperties().iter():
        print "property of disk: %s=>%s" %(property.getAttribute("name"),property.getAttribute("value"))
    storage=HP_EVA_Storage(system="127.0.0.1/EVA5000", username="Administrator", password="Administrator", autoconnect=True, cmd="./ComHP_EVA_SSSU_Sim.py")
    print "Connectionname: %s" %(storage.getConnectionName())
    print "Adding Disk %s" %(disk.getAttribute("name"))
    print storage.add(disk)
    print "Removing Disk %s" %(disk.getAttribute("name"))
    print storage.delete(disk)
    xml_dump="""
        <disk name="Virtual Disks/atix/sourcedisk_snap">
            <mapping lun="1">
                <host name="server1"/>
            </mapping>
        </disk>
"""
    doc=reader.fromString(xml_dump)
    disk=Disk(doc.documentElement, doc)
    print "Adding Luns to Disk %s" %(disk.getAttribute("name"))
    print storage.map_luns(disk)
    print "Removing Luns from Disk %s" %(disk.getAttribute("name"))
    print storage.unmap_luns(disk)

    storage.close()

if __name__ == '__main__':
    main()

########################
# $Log: ComHP_EVA_Storage.py,v $
# Revision 1.1  2007-02-09 11:36:16  marc
# initial revision
#