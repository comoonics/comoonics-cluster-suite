"""
Class for the SesSesam Backupcontroller.
"""
from comoonics import ComLog, ComSystem

class SepSesam(object):
	FULL="F"
	COPY="C"
	DIFFERENTIAL="D"
	INCREMENTAL="I"

    log=ComLog.getLogger("comoonics.backup.SepSesam.SepSesam")
    SESAM_CMD="/opt/sesam/bin/sesam/sm_cmd"
	"""Class for Controlling the SepSesam Client"""

    def __init__(self, group, client, mediapool=None):
        self.log.debug(".__init__(%s, %s, %s)"%(client, group))
        self.client=client
        self.group=group
        self.mediapool=mediapool
        self.level=FULL

    def doBackup(self, level, filename=None):
        self.level=level
        #output=self.add_backuptask(filename=filename)
        output+=self.start_backuptask(filename)
        #output+=self.wait_for_task()
        #output+=self.delete_task()

    def doRecover(self, filename, destdir, dir=True):
        output=self.start_restoretask()
        #output+=self.wait_for_task()

    def add_backuptask(filename=None):
    	cmd="add task %(taskname)s -c %(client)s -j %(group)s" %(self.__dict__)
    	if filename:
    		cmd+=" -s %s" %filename
    	return self.execute(cmd)

    def start_backuptask(filename=None):
    	cmd="backup %(group)s -l %(level)s" %self.__dict__
    	if self.mediapool:
    		cmd+=" -m %s" %self.mediapool
    	if filename:
    		cmd+=" -s %s" %filename
    	return self.execute(cmd)

    def start_restoretask(filename=None):
    	cmd="restore -j %(group)s" %self.__dict__
    	if self.mediapool:
    		cmd+=" -m %s" %self.mediapool
    	if filename:
    		cmd+=" -s %s" %filename
    	return self.execute(cmd)

    def execute(self, cmd):
        return ComSystem.execLocalOutput("%s %s" %(self.SESAM_CMD, cmd))