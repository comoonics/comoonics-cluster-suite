#!/usr/bin/python
"""
Python implementation of the Base Storage Interface to connect a modification or copyset to a storage implementation
"""

# here is some internal information
# $Id: ComHP_EVA_Storage.py,v 1.8 2010-03-08 12:30:48 marc Exp $
#

__version__ = "$Revision: 1.8 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/hp/ComHP_EVA_Storage.py,v $

from comoonics.cluster.tools.pexpect import TIMEOUT
from comoonics import ComLog
from comoonics.storage.hp.ComHP_EVA_SSSU import HP_EVA_SSSU, CommandError
from comoonics.storage.ComStorage import Storage, ErrorDuringExecution
from comoonics.storage.hp.ComHP_EVA import HP_EVA_Object

class HP_EVA_Storage(Storage):
   __logStrLevel__ = "comoonics.storage.hp.HP_EVA_Storage"
   """
   Baseclass for storagesystem implementations. All supported methods should be implemented. If not an exception is
   raised.
   """
   def __init__(self, **kwds):
      """ Default constructor does nothing here """
      super(HP_EVA_Storage, self).__init__(**kwds)
      (self.manager,self.system)=self.system.split("/")

      if not hasattr(self, "timeout"):
         self.timeout=1
      if kwds.has_key("timeout"):
         self.cmd=kwds["timout"]

      if not hasattr(self, "cmd"):
#         mylogger.debug("setting cmd cause not set kwds: %s" %(kwds))
         self.cmd=HP_EVA_SSSU.SSSU_CMD
#      else:
#         mylogger.debug("cmd already set to cause %s" %(self.cmd))
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
      self.sssu=None
      if kwds.has_key("autoconnect"):
         self.autoconnect=kwds["autoconnect"]
         self.connect()


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
         mylogger.debug("system: %s, manager: %s, cmd: %s" %(self.system,self.manager,self.cmd))
         logfile=cmdlogfile=None
         if self.log:
            logfile = file(self.log, "w")
         if self.cmdlog:
            cmdlogfile = file(self.cmdlog, "w")
         self.sssu=HP_EVA_SSSU(self.manager, self.username, self.password, self.system, self.autoconnect, self.cmd, logfile, cmdlogfile)
         self.sssu.connect()

   def map_luns(self, *params):
      """ Lunmaps the given disk. Hosts and luns are integrated insite the disk and returns the luns if need be. """
      if not params or len(params)==0:
         raise TypeError("map_luns takes at lease 1 argument 0 given.")
      elif params and len(params)>2:
         raise TypeError("map_luns takes at lease 1 argument %u given." %(len(params)))
      disk=params[0]
      source=None
      if len(params)==2:
         source=params[1]
      luns=list()
      for lun in disk.getLuns():
         for host in disk.getHostNames(lun):
            try:
               self.sssu.cmd("add lun %s vdisk=\"%s\" host=\"%s\"" %(lun, disk.getAttribute("name"), host))
               if lun.count("\\")==0:
                  if host.count("\\")==0:
                     host="\Hosts\\%s" %(host)
                  self.sssu.cmd("ls lun \"%s\\%s\" xml" %(host,lun))
               else:
                  self.sssu.cmd("ls lun \"%s\" xml" %(lun))
               lun=None
               if self.sssu.xml_output:
                  lun=HP_EVA_Object.fromXML(self.sssu.xml_output)
                  luns.append(lun)
            except CommandError, ce:
               raise ErrorDuringExecution("Could not add lun to storage\nExecution errorcode %u: \ncmd: %s" %(self.sssu.last_error_code, self.sssu.last_cmd), ce)
      self.wait()
      return luns

   def unmap_luns(self, *params):
      """ Lunmaps the given disk. Hosts and luns are integrated insite the disk. """
      if not params or len(params)==0:
         raise TypeError("unmap_luns takes at lease 1 argument 0 given.")
      elif params and len(params)>2:
         raise TypeError("unmap_luns takes at lease 1 argument %u given." %(len(params)))
      disk=params[0]
      source=None
      if len(params)==2:
         source=params[1]
      luns=list()
      for lun in disk.getLuns():
         for host in disk.getHostNames(lun):
            try:
               if host.count("\\")>0:
                  path=host+"\\"
               else:
                  path=""
               if self.sssu.cmd("ls lun \"%s%s\" xml" %(path,lun))==0 and self.sssu.xml_output:
                  luns.append(HP_EVA_Object.fromXML(self.sssu.xml_output))
               self.sssu.cmd("delete lun \"%s%s\"" %(path,lun))
            except CommandError, ce:
               raise ErrorDuringExecution("Could not delete lun from storage\nExecution errorcode %u: \ncmd: %s" %(self.sssu.last_error_code, self.sssu.last_cmd), ce)
      self.wait()
      return luns

   def wait(self):
      """Sometimes host is not fast enough to see the lun so we'll wait here"""
      import time
      mylogger.debug("wait(%u)" %(self.timeout))
      time.sleep(self.timeout)

   def _delete(self, _type, name, properties, checkfunc=None):
      try:
         vdisk=None
         default_params={ "vdisk" : [ "WAIT_FOR_COMPLETION" ]}
         allowed_params={ "vdisk":  [ "WAIT_FOR_COMPLETION", "NOWAIT_FOR_COMPLETION"] }
         # this means we are called as undo in consequence as called like add so we have to make the name
         # and move other paramaters away
         if _type=="vdisk" and properties and properties.has_key("vdisk"):
            vdisk=properties["vdisk"].getAttribute("value")
            if vdisk.find("\\ACTIVE")>0:
               vdisk=vdisk[:vdisk.rindex("\\ACTIVE")]
            name=vdisk+"\\"+name
         # clear all other properties except those allowed for delete
         if properties:
            for key in properties.keys():
               if allowed_params.has_key(_type) and key in allowed_params[_type]:
                  pass
               else:
                  del properties[key]
         if default_params.has_key(_type):
            if not properties:
               properties=dict()
            for def_parm in default_params[_type]:
               if type(properties) == dict:
                  properties[def_parm]=True
               else:
                  properties[def_parm]=""
                  mylogger.debug("property[%s]=%s, type=%s" %(def_parm, properties[def_parm].getValue(), type(properties[def_parm].getValue())))

         if self.sssu.cmd("ls %s \"%s\" xml" %(_type, name))==0 and self.sssu.xml_output:
            vdisk=HP_EVA_Object.fromXML(self.sssu.xml_output)
            mylogger.debug("deleting vdisk %s" %(vdisk.objectname))
            if isinstance(vdisk, HP_EVA_Object):
               if not checkfunc or (checkfunc and checkfunc(vdisk)):
                  self.sssu.cmd("delete %s \"%s\"" %(_type, name), properties)
            return vdisk
         else:
            raise ErrorDuringExecution("Could not delete %s %s from storage. %s %s does not exist" %(type, name, type, name))
      except CommandError, ce:
         raise ErrorDuringExecution("Could not delete %s %s to storage\nExecution errorcode %u: \ncmd: %s" %(type, name, self.sssu.last_error_code, self.sssu.last_cmd), ce)

   def _add(self, type, name, properties):
      #
      # THOUGTS: We need to check disk for
      #  operationalstate .....................: attention
      # VS
      #  operationalstate .....................: good
      # to simulate something like WAIT_FOR_COMLETITION
      #
      try:
         mylogger.debug("add %s \"%s\" %s" %(type, name, properties))
         try:
            _result=self.sssu.cmd("add %s \"%s\"" %(type, name), properties)
         except TIMEOUT:
            _result=0
         if _result==0:
            if type=="vdisk":
               lscmd="ls %s \"%s\\ACTIVE\" xml" %(type, name)
            elif type=="snapshot":
               vdisk=properties["vdisk"].getAttribute("value")
               if vdisk.find("\\ACTIVE")>0:
                  vdisk=vdisk[:vdisk.rindex("\\ACTIVE")]
               lscmd="ls %s \"%s\\%s\" xml" %(type, vdisk, name)
            else:
               lscmd="ls %s \"%s\" xml" %(type, name)
            operational=False
            iterations=0
            maxiterations=10
            while not operational and iterations<maxiterations:
               self.sssu.cmd(lscmd)
               vdisk=None
               if self.sssu.xml_output:
                  vdisk=HP_EVA_Object.fromXML(self.sssu.xml_output)
                  if hasattr(vdisk, "operationalstate"):
                     mylogger.debug("_add: operationalstate: %s" %(getattr(vdisk, "operationalstate")))
                     if getattr(vdisk, "operationalstate")=="good":
                        operational=True
                     else:
                        import time
                        mylogger.debug("_add: operationalstate is not good waiting(%u).." %(iterations))
                        time.sleep(5)
                        iterations+=1
               else:
                  iterations=maxiterations
            return vdisk
         else:
            raise ErrorDuringExecution("Could not add %s %s to storage.\nExecution errorcode %u: \ncmd: %s, output: %s" %(type, name, self.sssu.last_error_code, self.sssu.last_cmd, self.sssu.last_output))
      except CommandError, ce:
         raise ErrorDuringExecution("Could not add %s %s to storage\nExecution errorcode %u: \ncmd: %s\noutput: %s" %(type, name, ce.errorcode, ce.cmd, ce.output))

   def add(self, *params):
      """ Adds the given disk. Parameters are packed as properties insite the disk. """
      if not params or len(params)==0:
         raise TypeError("add takes at lease 1 argument 0 given.")
      elif params and len(params)>2:
         raise TypeError("add takes at lease 1 argument %u given." %(len(params)))
      disk=params[0]
      return self._add("vdisk", disk.getAttribute("name"), disk.getProperties())

   def add_snapshot(self, *params):
      """ Snapshots the given sourcedisk to destdisk. Options are packed as properties insite of destdisk."""
      if not params or len(params)==0:
         raise TypeError("add_snapshot takes at lease 1 argument 0 given.")
      elif params and len(params)>2:
         raise TypeError("add_snapshot takes at lease 1 argument %u given." %(len(params)))
      destdisk=params[0]
      sourcedisk=params[1]
      properties=destdisk.getProperties()
      properties.setProperty("vdisk", sourcedisk.getAttribute("name"))
      return self._add("snapshot", destdisk.getAttribute("name"), properties)

   def add_clone(self, *params):
      """ Clones the given sourcedisk to destdisk. Options are packed as properties insite of destdisk. """
      if not params or len(params)==0:
         raise TypeError("add_clone takes at lease 1 argument 0 given.")
      elif params and len(params)>2:
         raise TypeError("add_clone takes at lease 1 argument %u given." %(len(params)))
      destdisk=params[0]
      sourcedisk=params[1]
      properties=destdisk.getProperties()
      properties["vdisk"]=sourcedisk.getAttribute("name")
      return self._add("snapshot", destdisk.getAttribute("name"), properties)

   def delete(self, *params):
      """ Deletes the given disk. If you only want to support the deleting of snapshots use delete_snaphot. """
      if not params or len(params)==0:
         raise TypeError("delete takes at lease 1 argument 0 given.")
      elif params and len(params)>2:
         raise TypeError("delete takes at lease 1 argument %u given." %(len(params)))
      disk=params[0]
      return self._delete("vdisk", disk.getAttribute("name"), disk.getProperties())

   def delete_snapshot(self, *params):
      """ Deletes the given disk only if its a snapshot. """
      if not params or len(params)==0:
         raise TypeError("delete_snapshot takes at lease 1 argument 0 given.")
      elif params and len(params)>2:
         raise TypeError("delete_snapshot takes at lease 1 argument %u given." %(len(params)))
      disk=params[0]
      return self._delete("vdisk", disk.getAttribute("name"), disk.getProperties(), self.isSnapshot)

   def delete_clone(self, *params):
      """ Deletes the given disk only if its a clone. """
      if not params or len(params)==0:
         raise TypeError("delete_clone takes at lease 1 argument 0 given.")
      elif params and len(params)>2:
         raise TypeError("delete_clone takes at lease 1 argument %u given." %(len(params)))
      disk=params[0]
      return self._delete("vdisk", disk.getAttribute("name"), disk.getProperties(), self.isClone)

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
