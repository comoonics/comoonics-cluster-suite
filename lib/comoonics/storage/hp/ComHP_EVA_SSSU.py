#!/usr/bin/python
"""
Python implementation of the HP SSSU utility to communicate with the HP EVA Storage Array system
"""

# here is some internal information
# $Id: ComHP_EVA_SSSU.py,v 1.1 2007-02-09 11:36:16 marc Exp $
#

__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/hp/ComHP_EVA_SSSU.py,v $

import re
from comoonics.ComDataObject import DataObject
from comoonics import pexpect, ComLog
from comoonics import ComExceptions
from xml.dom import Node
from ComHP_EVA import HP_EVA_Object

class CouldNotParseSSSU(ComExceptions.ComException): pass
class CouldNotConnectToManager(ComExceptions.ComException): pass
class NotConnectedToManager(ComExceptions.ComException): pass
class WrongParameterGiven(ComExceptions.ComException): pass
class CommandError(ComExceptions.ComException):
    def __init__(self, errorcode, cmd, output):
        self.errorcode=errorcode
        self.cmd=cmd
        self.output=output
    def __str__(self):
        return """
Command %s, exited with errorcode %u
Output:
%s
""" %(self.cmd, self.errorcode, self.output)

class HP_EVA_SSSU(object):
    __logStrLevel__="HP_EVA_SSSU"
    MATCH_MANAGER=re.compile("Manager:", re.IGNORECASE)
    MATCH_USERNAME=re.compile("username:", re.IGNORECASE)
    MATCH_PASSWORD=re.compile("password:", re.IGNORECASE)
    MATCH_CONNECTION_ERROR=re.compile("Error opening https connection", re.IGNORECASE)
    MATCH_NOSYSTEMSELECTED=re.compile("NoSystemSelected>", re.IGNORECASE)
    MATCH_COMMANDSTATUS="<sssucommandstatus>(\d+)</sssucommandstatus>"
    MATCH_XMLOBJECT=re.compile(".*(<object>.*</object>).*", re.MULTILINE|re.DOTALL)

    END_PROMPT=">"
    DELIM=" "

    DISPLAY_XMLSTATUS="DISPLAY_XMLSTATUS"

    SSSU_CMD="sssu"

    def __init__(self, manager, username, password, system, auto_connect=True, command=None, logfile=None, cmdlog=None):
        """
        Initializes the connection to the HP EVA. But not connects. This will be done implicitly or directly via
        the connect method.
        """
        self.manager=manager
        self.username=username
        self.password=password
        self.system=system
        self.logfile=logfile
        if isinstance(self.logfile, basestring):
            self.logfile=file(self.logfile, "w")
        self.cmdlog=cmdlog
        if isinstance(self.cmdlog, basestring):
            self.cmdlog=file(self.cmdlog, "w")
        self.xml_output=None
        if command:
            self.sssu_cmd=command
        else:
            self.sssu_cmd=HP_EVA_SSSU.SSSU_CMD
        self.sssu_shell=None
        self.auto_connect=auto_connect

        self.autoConnect()

    def autoConnect(self):
        """ autoconnects to HP EVA MA, if auto_connect is enabled """
        if self.auto_connect:
            self.connect()

    def connected(self):
        """ checks for connection to HP EVA MA. If not connected it will automatically connect. Returns True/False."""
        if not self.sssu_shell and self.auto_connect:
            self.connect()

        if self.sssu_shell and self.sssu_shell.isalive():
            return True
        else:
            return False

    def connectedRaise(self):
        """ does the same as connect but raises a NotConnectedToManager if not connected. """
        if not self.connected():
            raise NotConnectedToManager("We are not connected to the Manager. Please connect first.")

    def connect(self):
        """
        Connects to the HP EVA MA. With the parameters given to the constructor.
        """
        mylogger.debug("spawning shell %s" %(self.sssu_cmd))
        self.sssu_shell=pexpect.spawn(self.sssu_cmd)
        self.sssu_shell.logfile=self.logfile
        self.sssu_shell.cmdlogfile=self.cmdlog
        if not self.sssu_shell.isalive():
            raise CouldNotConnectToManager("Could not connect to manager %s" %(self.manager))
        mylogger.debug("connecting to manager shell %s" %(self.manager))
        if self.sssu_shell.expect(HP_EVA_SSSU.MATCH_MANAGER) >= 0:
            self.sssu_shell.sendline(self.manager)
        else:
            mylogger.debug(self.sssu_shell.buffer)
            raise CouldNotParseSSSU("Manager not found")
        mylogger.debug("username %s" %(self.username))
        if self.sssu_shell.expect(HP_EVA_SSSU.MATCH_USERNAME)>=0:
            self.sssu_shell.sendline(self.username)
        else:
            raise CouldNotParseSSSU("Username not found")
        mylogger.debug("password: ***")
        if self.sssu_shell.expect(HP_EVA_SSSU.MATCH_PASSWORD)>=0:
            self.sssu_shell.sendline(self.password)
        else:
            raise CouldNotParseSSSU("Password not found")

        if self.sssu_shell.expect([HP_EVA_SSSU.MATCH_NOSYSTEMSELECTED, pexpect.TIMEOUT, pexpect.EOF], 10)>0:
            raise CouldNotConnectToManager, "Either manager, username or password or all are wrong.\nCould not estabilsh connection to %s/%s/*****\n" %(self.manager, self.username)

        mylogger.debug("Switching to xmlstatus")
        self.setOptions(HP_EVA_SSSU.DISPLAY_XMLSTATUS)
        self.selectSystem(self.system)
        mylogger.debug("manage system")
        self.setSystem(self.system, "manage")

    def setOptions(self, option):
        """
        Sets the options on the sssu. (Command: set options)
        """
        self.cmd("set options", option)

    def selectSystem(self, system):
        """
        Selects the given system (Command: select system)
        """
        mylogger.debug("select system %s" %(system))
        self.cmd("select system", system)

    def setSystem(self, system, param):
        """
        Sets an option to this system (Command: set system)
        """
        pass

    def disconnect(self):
        """
        Disconnects from sssu
        """
        self.cmd("exit", None, pexpect.EOF)

    def cmd(self, cmd, params=None, match=None):
        self.last_cmd=cmd
        if not match:
            match=HP_EVA_SSSU.MATCH_COMMANDSTATUS

        self.last_cmd=cmd+HP_EVA_SSSU.DELIM+self.toParams(params)

        self.sssu_shell.sendline(self.last_cmd)
        self.sssu_shell.expect(match)
        self.last_output=self.sssu_shell.before
        self.xml_output=None
        if self.sssu_shell.match==pexpect.EOF:
            return 0
        else:
            if isinstance(self.sssu_shell.match,pexpect.ExceptionPexpect):
                raise CommandError(1, self.last_cmd, self.sssu_shell.before)
            else:
                thematch=self.sssu_shell.match
                mylogger.debug("self.sssu_shell.match.group(1): %s" %(thematch.group(1)))
                self.last_error_code=int(thematch.group(1))
                if self.last_error_code == 0:
                    self.xml_output=self.LastOutput2XML()
                    return self.last_error_code
                else:
                    raise CommandError(self.last_error_code, self.last_cmd, self.last_output)

    def toParams(self, params):
        from comoonics.ComProperties import Properties
        buf=""
        if params and isinstance(params, basestring):
            buf=params
        elif params and type(params)==list or type(params)==tuple:
            buf=HP_EVA_SSSU.DELIM.join(params)
        elif params and isinstance(params, Properties):
            for property in params.iter():
                #mylogger.debug("Property: %s" %(property))
                mylogger.debug("toParams(%s): %s" %(property.getAttribute("name"),property.getAttribute("value")))
                if property.hasAttribute("name"):
                    buf+=property.getAttribute("name")
                    if property.getAttribute("value") and type(property.getAttribute("value"))==bool:
                        pass
                    else:
                        buf+="=\""+property.getAttribute("value")+"\""
                    buf+=HP_EVA_SSSU.DELIM
        elif params and isinstance(params, DataObject):
            for property in params.getProperties().iter():
                buf+=property.getAttribute("name")
                if property.getAttribute("value") and type(property.getAttribute("value"))==bool:
                    pass
                else:
                    buf+="="+property.getAttribute("value")
                buf+=HP_EVA_SSSU.DELIM
        return buf

    def LastOutput2XML(self):
        """
        Converts the last output to XML if possible returns None if not possible
        """
        match=HP_EVA_SSSU.MATCH_XMLOBJECT.match(self.last_output)
        #mylogger.debug("%s, %s" %(self.last_output,match))
        if match:
            from xml.dom.ext.reader import Sax2
            reader=Sax2.Reader(validate=0)
            #mylogger.debug("xml: %s" %(match.group(1)))
            doc=reader.fromString(match.group(1))
            return doc.documentElement
        else:
            return None


mylogger=ComLog.getLogger(HP_EVA_SSSU.__logStrLevel__)

def main():
    from xml.dom.ext import PrettyPrint
    log = file('/tmp/ComHP_EVA_SSSU.log','w')
    sssu=HP_EVA_SSSU("127.0.0.1", "Administrator", "Administrator", "EVA5000", True, "./ComHP_EVA_SSSU_Sim.py", log)
    sssu.cmd("add", ["vdisk", "myvdisk", "size=100"])
    sssu.cmd("ls", "vdisk myvdisk")
    print "vdisk mydisk: %s" %(sssu.last_output)
    sssu.cmd("ls", "vdisk myvdisk xml")
    if sssu.xml_output:
        print "vdisk mydisk as HP_EVA_Object:"
        vdisk=HP_EVA_Object.fromXML(sssu.xml_output)
        print vdisk
    else:
        print "no last xmloutput %s" %(sssu.xml_output)
    sssu.disconnect()
    log.close()

if __name__ == '__main__':
    import sys
    main()

########################
# $Log: ComHP_EVA_SSSU.py,v $
# Revision 1.1  2007-02-09 11:36:16  marc
# initial revision
#