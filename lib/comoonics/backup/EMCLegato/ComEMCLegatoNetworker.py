"""
Class for the EMC-Legator BackupHandlerImplementation.
"""
# here is some internal information
# $Id: ComEMCLegatoNetworker.py,v 1.1 2007-03-26 07:48:58 marc Exp $
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
        return "Error during the execution of %s. Error: %s" %(LegatoNetworker.LEGATO_CMD, self.value)

class LegatoNetworker(object):
    log=ComLog.getLogger("LegatoNetworker")
    LEGATO_CMD="/usr/sbin/savefs"
    OPTION_NOT_IN_SAVESET="-F"
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
        self.options=list()

    def executeSaveFs(self, level, file=None):
        values=list()
        if file:
            self.options.append(LegatoNetworker.OPTION_NOT_IN_SAVESET)
            values.append(file)
        cmd="%s %s -l %s -c %s -s %s -g %s %s" %(LegatoNetworker.LEGATO_CMD, " ".join(self.options), level, \
                                                 self.client, self.server, self.group, " ".join(values))
        ComSystem.execLocalOutput(cmd)

#######################
# $Log: ComEMCLegatoNetworker.py,v $
# Revision 1.1  2007-03-26 07:48:58  marc
# initial revision
#
