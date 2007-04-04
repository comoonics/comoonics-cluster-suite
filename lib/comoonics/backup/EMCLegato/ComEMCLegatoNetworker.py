"""
Class for the EMC-Legator BackupHandlerImplementation.
"""
# here is some internal information
# $Id: ComEMCLegatoNetworker.py,v 1.2 2007-04-04 12:47:08 marc Exp $
#


from comoonics import ComLog, ComSystem
from comoonics.ComSystem import execLocalOutput
from comoonics.ComExceptions import ComException

class LegatoBackupLevel(object):
    FULL="full"
    SKIP="skip"
    INCR="incr"
    ONE="1"
    TWO="2"
    THREE="3"
    FOUR="4"
    FIVE="5"
    SIX="6"
    SEVEN="7"
    EIGHT="8"
    NINE="9"

class LegatoNetworkerError(ComException):
    def __str__(self):
        return "Error during the execution of %s. Error: %s" %(LegatoNetworker.LEGATO_CMD_SAVEFS, self.value)

class LegatoNetworkerSaveFSError(LegatoNetworkerError):
    def __str__(self):
        return "Error during the execution of %s. Error: %s" %(LegatoNetworker.LEGATO_CMD_SAVEFS, self.value)
class LegatoNetworkerRecoverError(LegatoNetworkerError):
    def __str__(self):
        return "Error during the execution of %s. Error: %s" %(LegatoNetworker.LEGATO_CMD_RECOVER, self.value)

class LegatoNetworker(object):
    log=ComLog.getLogger("LegatoNetworker")
    LEGATO_CMD_SAVEFS="/usr/sbin/savefs"
    LEGATO_CMD_RECOVER="/usr/sbin/recover"
    OPTION_NOT_IN_SAVESET="-F"
    OPTION_AUTOMATIC_RECOVERY="-a"
    """
    Creates a new LegatoNetworker instance for the given client and backupset
    @client: the client to backup or restore
    @group:  the backupgroup to backup or restore
    @server: use which backupserver
    """
    def __init__(self, client, group, server):
        self.log.debug(".__init__(%s, %s, %s)"%(client, group, server))
        self.client=client
        self.group=group
        self.server=server
        self.savefs_options =list()
        self.recover_options=list()
        self.recover_options.append(self.OPTION_AUTOMATIC_RECOVERY)

    def executeSaveFs(self, level, file=None):
        values=list()
        if file:
            self.savefs_options.append(LegatoNetworker.OPTION_NOT_IN_SAVESET)
            values.append(file)
        cmd="%s %s -l %s -c %s -s %s -g %s %s" %(LegatoNetworker.LEGATO_CMD_SAVEFS, " ".join(self.savefs_options), level, \
                                                 self.client, self.server, self.group, " ".join(values))
        ComSystem.execLocalOutput(cmd)

    def executeRecover(self, file, destdir):
        # recover -s wspbackup.messe-muenchen.de -c wspbackup.messe-muenchen.de -a -d /mnt/backup/recover /tmp/metadata/vg_gfstest-lv_gfstest_filesystem.xml
        cmd="%s %s -c %s -s %s -d %s %s" %(LegatoNetworker.LEGATO_CMD_RECOVER, " ".join(self.recover_options),
                                              self.client, self.server, destdir, file)
        ComSystem.execLocalOutput(cmd)

#######################
# $Log: ComEMCLegatoNetworker.py,v $
# Revision 1.2  2007-04-04 12:47:08  marc
# MMG Backup Legato Integration:
# - added executeRecover for restoring data
#
# Revision 1.1  2007/03/26 07:48:58  marc
# initial revision
#
