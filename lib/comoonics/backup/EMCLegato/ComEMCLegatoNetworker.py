"""
Class for the EMC-Legator BackupHandlerImplementation.
"""
# here is some internal information
# $Id: ComEMCLegatoNetworker.py,v 1.6 2010-02-12 10:08:06 marc Exp $
#

import os.path
from logging import DEBUG
from comoonics import ComLog, ComSystem
from comoonics.cluster.tools import pexpect
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
    log=ComLog.getLogger("comoonics.backup.EMCLegato.LegatoNetworker")
    LEGATO_CMD_SAVEFS="/usr/sbin/savefs"
    LEGATO_CMD_RECOVER="/usr/sbin/recover"
    LEGATO_RECOVER_SHELL="recover>"
    OPTION_NOT_IN_SAVESET="-F"
    OPTION_AUTOMATIC_RECOVERY="-a"
    OPTION_FORCEOVERWRITE_RECOVERY="-f"
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
        #self.recover_options.append(self.OPTION_AUTOMATIC_RECOVERY)
        self.recover_options.append(self.OPTION_FORCEOVERWRITE_RECOVERY)

    def executeSaveFs(self, level, file=None):
        values=list()
        if file:
            self.savefs_options.append(LegatoNetworker.OPTION_NOT_IN_SAVESET)
            values.append(file)
        _cmd="%s %s -l %s -c %s -s %s -g %s %s" %(LegatoNetworker.LEGATO_CMD_SAVEFS, " ".join(self.savefs_options), level, \
                                                 self.client, self.server, self.group, " ".join(values))
        _output=ComSystem.execLocalOutput(_cmd)
        self.log.debug("executeSaveFs: cmd=%s, output=%s" %(_cmd, _output))

    def executeRecover(self, _file, destdir, dir=True):
        # recover -s wspbackup.messe-muenchen.de -c wspbackup.messe-muenchen.de -a -d /mnt/backup/recover /tmp/metadata/vg_gfstest-lv_gfstest_filesystem.xml
        if dir:
            _dir=_file
            _selection="*"
        else:
            _dir=os.path.dirname(_file)
            _selection=os.path.basename(_file)
        _cmd="%s %s -c %s -s %s -d %s %s" %(LegatoNetworker.LEGATO_CMD_RECOVER, " ".join(self.recover_options),
                                            self.client, self.server, destdir, _dir)
        if ComSystem.askExecModeCmd(_cmd):
            # Ignore timeouts
            _shell=pexpect.spawn(_cmd, [], None)
            if self.log.getEffectiveLevel() == DEBUG:
                _shell.logfile=file(str("/tmp/%s.log" %(os.path.basename(LegatoNetworker.LEGATO_CMD_RECOVER))), "w")
                _shell.cmdlogfile=file(str("/tmp/%s-cmd.log" %(os.path.basename(LegatoNetworker.LEGATO_CMD_RECOVER))), "w")
            _shell.expect(self.LEGATO_RECOVER_SHELL)
            _shell.sendline("add -q %s" %_selection)
            _shell.expect(self.LEGATO_RECOVER_SHELL)
            _shell.sendline("recover")
            _shell.expect(self.LEGATO_RECOVER_SHELL, None)
            _shell.close()

#######################
# $Log: ComEMCLegatoNetworker.py,v $
# Revision 1.6  2010-02-12 10:08:06  marc
# new version that fixed import problemes
#
# Revision 1.5  2007/08/07 15:15:21  marc
# - Fix Bug BZ #77 that the restore command is likely to timeout. This is ignored now. 2nd attempt (validated)
#
# Revision 1.4  2007/08/07 11:18:35  marc
# - Fix Bug BZ #77 that the restore command is likely to timeout. This is ignored now.
#
# Revision 1.3  2007/07/10 11:33:24  marc
# changed way to restore as all files would be restored in the basedir of all files which is not what we want.
#
# Revision 1.2  2007/04/04 12:47:08  marc
# MMG Backup Legato Integration:
# - added executeRecover for restoring data
#
# Revision 1.1  2007/03/26 07:48:58  marc
# initial revision
#
